#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/workflow/session.py
# Purpose:                Manage a document editing session through several workflow actions.
#
# Copyright (C) 2016, 2017 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
'''
Manage a document editing session through several workflow actions.
'''

import os
import os.path
import shutil
import tempfile
import codecs

from lxml import etree
import six

# Mercurial and mercurial-hug are disabled for now.
# from mercurial import error as hg_error
# import hug

from lychee.document import document
from lychee import exceptions
from lychee.logs import SESSION_LOG as log
from lychee import signals
from lychee.workflow import registrar, steps


_CANNOT_SAFELY_HG_INIT = 'Could not safely initialize the repository'
_CANNOT_MAKE_HG_DIR = 'Could not create repository directory'
_FAILURE_DURING_INBOUND = 'Action failed during the inbound steps'
_UNKNOWN_REVISION = "ACTION_START requested a revision that doesn't exist"
_VCS_UNSUPPORTED = 'VCS is unsupported'
_SAVE_ERR_BAD_DATA = 'Incorrect data while trying to save.'

# for text editor contents not passed through the workflow
SAVE_DIR = 'save'

USER_SETTINGS_DIR = "user"
USER_SETTINGS_FILE = os.path.join(USER_SETTINGS_DIR, "lychee_settings.xml")


@log.wrap('info', 'error signal', 'action')
def _error_slot(action, **kwargs):
    '''
    Slot for *_ERROR signals in any module.
    '''
    if 'msg' in kwargs:
        action.failure('Caught an ERROR signal: {msg}', msg=kwargs['msg'])
    else:
        action.failure('Caught an ERROR signal without a messge.')


signals.inbound.CONVERSION_ERROR.connect(_error_slot)
signals.inbound.VIEWS_ERROR.connect(_error_slot)
signals.vcs.ERROR.connect(_error_slot)
signals.outbound.ERROR.connect(_error_slot)


class InteractiveSession(object):
    '''
    Manage the Lychee-MEI :class:`~lychee.document.Document`, Mercurial repository, and
    other related data for an interactive music notation session.

    Version control is disabled by default, and must be enabled with the ``vcs`` parameter. Do note
    that *most* documentation referring to the Lychee "repository" refers to the directory in which
    the music document is stored, whether or not the directory is a VCS repository.
    '''

    def __init__(self, *args, **kwargs):
        '''
        :param str vcs: The VCS system to use. This is the string ``'mercurial'`` or ``None``.
        :raises: :exc:`lychee.exceptions.RepositoryError` when ``vcs`` is not valid.
        '''
        self._doc = None
        self._hug = None
        self._temp_dir = False
        self._repo_dir = None
        self._registrar = registrar.Registrar()

        signals.outbound.REGISTER_FORMAT.connect(self._registrar.register)
        signals.outbound.UNREGISTER_FORMAT.connect(self._registrar.unregister)
        signals.ACTION_START.connect(self._action_start)  # NOTE: this connection isn't tested
        signals.vcs.START.connect(steps._vcs_driver)
        signals.inbound.CONVERSION_FINISH.connect(self._inbound_conversion_finish)
        signals.inbound.VIEWS_FINISH.connect(self._inbound_views_finish)

        # thse should be cleared for each action
        self._inbound_converted = None
        self._inbound_views_info = None

        # handle VCS enablement
        self._vcs = None
        if 'vcs' in kwargs and kwargs['vcs']:
            # VCS is not supported currently.
            raise exceptions.RepositoryError(_VCS_UNSUPPORTED)

    @property
    def hug(self):
        '''
        Return the active :class:`mercurial-hug.Hug` instance.
        '''
        return self._hug

    @property
    def vcs_enabled(self):
        '''
        Return ``True`` if the VCS is enabled in this :class:`InteractiveSession`.
        '''
        return self._vcs is not None

    @property
    def registrar(self):
        '''
        Return the active :class:`~lychee.workflow.registrar.Registrar` instance.
        '''
        return self._registrar

    def __del__(self):
        '''
        If this session is using a temporary directory, delete it.
        '''
        try:
            self.unset_repo_dir()
        except AttributeError:
            pass

    @property
    def document(self):
        '''
        Get a :class:`~lychee.document.Document` for this session's repository.

        :returns: The :class:`Document` for this session.
        :rtype: :class:`lychee.document.Document`
        :raises: :exc:`~lychee.exceptions.RepositoryError` as per :meth:`set_repo_dir`.

        Do be aware that, if the repository directory is changed or unset, the :class:`Document`
        returned by this method will no longer be valid---but it won't know that.

        .. note:: If no repository directory has been set, this method creates a new repository in
            a temporary directory.
        '''
        if self._doc:
            return self._doc

        if self._repo_dir is None:
            self.set_repo_dir('')

        self._doc = document.Document(self._repo_dir)
        return self._doc

    @log.wrap('info', 'set the repository directory')
    def set_repo_dir(self, path, run_outbound=False):
        '''
        Change the pathname to Lychee's repository then optionally run registered outbound converters.

        :param str path: The pathname of the directory of the repository. This should either be an
            absolute path or something that will become absolute with :func:`os.path.abspath`.
        :param bool run_outbound: Whether to run conversions for all registered outbound formats
            after setting the repository directory. Defaults to ``False``.
        :returns: The absolute pathname to the repository directory.
        :rtype: str
        :raises: :exc:`~lychee.exceptions.RepositoryError` when ``path`` exists and contains files
            but is not a Mercurial repository, or is a repository but cannot be written to.
        :raises: :exc:`~lychee.exceptions.RepositoryError` when ``path`` does not exist and cannot
            be created.

        If ``path`` does not exist, it will be created.

        If ``path`` is ``''`` (an empty string) the repository will be initialized in a new
        temporary directory that should be automatically deleted when the :class:`InteractiveSession`
        instance is garbage collected.

        If VCS is enabled for this :class:`InteractiveSession`, a :class:`hug.Hug` instance will be
        created on the :prop:`hug` property.

        .. warning:: If this :class:`InteractiveSession` instance already has a repository in a
            temporary directory, it will be deleted before the new repository directory is set.
        '''
        self.unset_repo_dir()

        if path == '':
            self._repo_dir = tempfile.mkdtemp()
            self._temp_dir = True

        else:
            self._temp_dir = False  # just in case
            self._repo_dir = os.path.abspath(path)

            if not os.path.exists(self._repo_dir):
                try:
                    os.makedirs(self._repo_dir)
                except OSError:
                    raise exceptions.RepositoryError(_CANNOT_MAKE_HG_DIR)

        if self._vcs == 'mercurial':
            try:
                self._hug = hug.Hug(self._repo_dir, safe=True)
            except hg_error.RepoError:
                raise exceptions.RepositoryError(_CANNOT_SAFELY_HG_INIT)

        if run_outbound:
            self.run_outbound()

        return self._repo_dir

    @log.wrap('info', 'unset the repository directory')
    def unset_repo_dir(self):
        '''
        Unset the repository directory, deleting the repository if it's in a temporary directory,
        and do not set a new repository.
        '''
        if self._temp_dir and self._repo_dir:
            # If we don't check _repo_dir, and it's already None, then the call to rmtree() would
            # raise a TypeError.
            shutil.rmtree(self._repo_dir)

        self._repo_dir = None
        self._temp_dir = False
        self._hug = None
        self._doc = None

    def get_repo_dir(self):
        '''
        Return the absolute pathname for the directory holding Lychee's repository.

        :returns: The repository pathname.
        :rtype: str

        .. note:: If no repository pathname has been set, this function will initialize an empty
            repository in a temporary directory and return its path.
        '''
        if self._repo_dir:
            return self._repo_dir
        else:
            # NOTE: "run_outbound" must be False, in order to avoid a recursion loop
            return self.set_repo_dir('', run_outbound=False)

    def read_user_settings(self):
        """
        Read from this repo's user settings XML file.
        """
        user_settings = {}
        if self._repo_dir is None:
            return user_settings

        settings_file_name = os.path.join(self._repo_dir, USER_SETTINGS_FILE)
        try:
            with codecs.open(settings_file_name, encoding='utf-8') as settings_file:
                user_settings_xml = etree.parse(settings_file)
        except IOError:
            return user_settings

        for element in user_settings_xml.getroot():
            user_settings[element.tag] = element.text

        return user_settings

    def write_user_settings(self, user_settings):
        """
        Write to this repo's user settings XML file.
        """
        if self._repo_dir is None:
            return

        settings_file_name = os.path.join(self._repo_dir, USER_SETTINGS_FILE)
        try:
            os.makedirs(os.path.join(self._repo_dir, USER_SETTINGS_DIR))
        except OSError:
            pass

        user_settings_xml = etree.Element('lycheeSettings')
        for key in user_settings:
            element = etree.Element(key)
            element.text = user_settings[key]
            user_settings_xml.append(element)
        user_settings_xml = etree.ElementTree(user_settings_xml)

        try:
            with codecs.open(settings_file_name, 'w', encoding='utf-8') as settings_file:
                user_settings_xml.write(settings_file, pretty_print=True)
        except IOError:
            pass

    @staticmethod
    def make_save_path(repo_dir, sect_id, dtype):
        '''
        Makes the absolute pathname where s "text editor" file should be saved.

        :param str repo_dir: Root directory of the Session's LMEI document.
        :param str sect_id: The @xml:id of the section data.
        :param str dtype: Data type of the "doc" argument (e.g., "lilypond"). This should
            be a "dtype" recognized by :meth:`run_workflow`.
        :returns: Tuple with the directory name and full pathname for the file.
        :rtype: str
        :raises: :exc:`TypeError` if one of the arguments is not a string.
        :raises: :exc:`ValueError` if we cannot make a valid filesystem path to save.
        '''
        if not (isinstance(repo_dir, basestring) and
                isinstance(sect_id, basestring) and
                isinstance(dtype, basestring)
                ):
            raise TypeError(_SAVE_ERR_BAD_DATA)

        if not (len(repo_dir) > 0 and len(sect_id) > 0 and len(dtype) > 0):
            raise ValueError(_SAVE_ERR_BAD_DATA)

        sectiddtype = sect_id + dtype  # we should NOT append with os.path.join()
        if (os.pardir in sectiddtype or
                os.sep in sectiddtype or
                os.extsep in sectiddtype or
                os.pathsep in sectiddtype
            ):
            raise ValueError(_SAVE_ERR_BAD_DATA)

        save_dir = os.path.join(repo_dir, SAVE_DIR, sect_id)
        save_path = os.path.join(save_dir, dtype)

        return save_dir, save_path

    @log.wrap('debug', 'save text editor contents')
    def save_text_editor(self, sect_id, dtype, doc):
        '''
        Save the contents of a text editor, in any format, without checking validity.

        :param str sect_id: The @xml:id of the section data.
        :param str dtype: Data type of the "doc" argument (e.g., "lilypond"). This should
            be a "dtype" recognized by :meth:`run_workflow`.
        :param str doc: The text editor's contents to save.
        :returns: Pathname of the newly saved file.
        :rtype: str
        :raises: :exc:`TypeError` if one of the arguments is not a string.
        :raises: :exc:`ValueError` if we cannot make a valid filesystem path to save.
        :raises: :exc:`IOError` if the method cannot save for another reason.
        '''
        save_dir, save_path = InteractiveSession.make_save_path(self._repo_dir, sect_id, dtype)

        if not isinstance(doc, basestring):
            raise TypeError(_SAVE_ERR_BAD_DATA)

        if isinstance(doc, unicode):
            doc = doc.encode('utf-8')

        if len(doc) == 0:
            raise ValueError(_SAVE_ERR_BAD_DATA)

        try:
            os.makedirs(save_dir)
        except OSError:
            # raised if the directory exists; all the same to us
            pass

        with open(save_path, 'w') as save_file:
            save_file.write(doc)

        return save_path

    @log.wrap('critical', 'run a Lychee action', 'action')
    def _action_start(self, action, **kwargs):
        '''
        THIS METHOD IS DEPRECATED

        Use run_workflow(), run_inbound(), and run_outbound() instead.
        '''
        self._cleanup_for_new_action()
        initial_revision = None
        if self._vcs == 'mercurial' and 'revision' in kwargs:
            initial_revision = self._hug.summary()['parent'].split(' ')[0]

        try:
            if 'dtype' in kwargs and 'doc' in kwargs:
                # only do the inbound, document, and VCS steps if there's an incoming change
                if 'views_info' not in kwargs:
                    kwargs['views_info'] = None
                try:
                    self.run_inbound(kwargs['dtype'], kwargs['doc'], kwargs['views_info'])
                except exceptions.InboundConversionError:
                    action.failure(_FAILURE_DURING_INBOUND)
                    return

            else:
                if 'views_info' in kwargs:
                    self._inbound_views_info = kwargs['views_info']
                if self._vcs == 'mercurial' and 'revision' in kwargs:
                    try:
                        self._hug.update(kwargs['revision'])
                    except RuntimeError:
                        # raised when the revision is invalid
                        action.failure(_UNKNOWN_REVISION)
                        return

            self.run_outbound(views_info=self._inbound_views_info)

        finally:
            self._cleanup_for_new_action()
            if initial_revision:
                self._hug.update(initial_revision)

    @log.wrap('critical', 'run full workflow', 'action')
    def run_workflow(self, dtype, doc, sect_id=None, action=None):
        '''
        Run a full *Lychee* workflow, including the inbound, document, VCS (if enabled), and
        outbund steps.

        :param str dtype: The format (data type) of the inbound musical document. This must
            correspond to the name of a converter module in :mod:`lychee.converters.inbound`.
        :param object doc: The inbound musical document. The required type is determined by each
            converter module itself.
        :param str sect_id: The Lychee-MEI @xml:id attribute of the ``<section>`` contained in
            the "doc" argument. If omitted, "converted" will become a new ``<section>``.

        Emits the :const:`lychee.signals.outbound.CONVERSION_FINISHED` signal on completion. May
        also cause a bunch of different error signals if there's a problem.
        '''
        try:
            try:
                self.run_inbound(dtype, doc, sect_id)
            except exceptions.InboundConversionError:
                action.failure(_FAILURE_DURING_INBOUND)
                return

            self.run_outbound(views_info=self._inbound_views_info)

        finally:
            self._cleanup_for_new_action()

    @log.wrap('critical', 'run inbound workflow step')
    def run_inbound(self, dtype, doc, sect_id=None):
        '''
        Run the inbound (conversion and views), document, and (if enabled) VCS workflow steps.

        :param str dtype: The format (data type) of the inbound musical document. This must
            correspond to the name of a converter module in :mod:`lychee.converters.inbound`.
        :param object doc: The inbound musical document. The required type is determined by each
            converter module itself.
        :param str sect_id: The Lychee-MEI @xml:id attribute of the ``<section>`` contained in
            the "doc" argument. If omitted, "converted" will become a new ``<section>``.
        :raises: :exc:`lychee.exceptions.InboundConversionError` when the conversion or views
            processing steps fail.
        '''
        self._cleanup_for_new_action(sect_id)

        user_settings = self.read_user_settings()

        steps.do_inbound_conversion(
            session=self,
            dtype=dtype,
            document=doc,
            user_settings=user_settings)
        if not isinstance(self._inbound_converted, (etree._Element, etree._ElementTree)):
            raise exceptions.InboundConversionError()

        steps.do_inbound_views(
            session=self,
            dtype=dtype,
            document=doc,
            converted=self._inbound_converted,
            views_info=sect_id)
        if not isinstance(self._inbound_views_info, six.string_types):
            raise exceptions.InboundConversionError()

        document_pathnames = steps.do_document(
            converted=self._inbound_converted,
            session=self,
            views_info=self._inbound_views_info)

        self.write_user_settings(user_settings)

        steps.do_vcs(session=self, pathnames=document_pathnames)

    @log.wrap('critical', 'run outbound workflow step', 'action')
    def run_outbound(self, views_info=None, revision=None, action=None):
        '''
        Run the outbound workflow steps (views and conversion).

        :param str views_info: As per :func:`lychee.workflow.steps.do_outbound_steps`
        :param str revision: Checkout a specific changeset before running the outbound steps.
            This may be a revision number, but we recommend using the changeset hash when possible.
            This argument is ignored when version control is not enabled.

        You may request only (a portion of) a ``<section>`` for outbound conversion by providing
        the @xml:id attribute of that element. You may also request data from an arbitrary
        changeset that is by including the revision identifier as the ``revision`` argument.

        For example:

        >>> session.run_outbound()

        This causes the most recent version of the full score to be converted for all registered
        outbound data types. On the other hand:

        >>> session.run_outbound(views_info='Sme-s-m-l-e1182873')

        This causes only the ``<section>`` with ``@xml:id="Sme-s-m-l-e1182873"`` to be sent for
        outbound conversion. And:

        >>> session.run_outbound(revision='40:964b28acc4ee')

        This will checkout changeset r40, output the full score, then checkout the most recent
        changeset again. Finally:

        >>> session.run_outbound(views_info='Sme-s-m-l-e1182873', revision='40:964b28acc4ee')

        This will checkout changeset r40, output only the ``<section>`` with
        ``@xml:id="Sme-s-m-l-e1182873"``, then checkout the most recent changeset.
        '''
        try:
            # check out another revision, if possible/necessary
            initial_revision = None
            if self._vcs == 'mercurial' and revision:
                initial_revision = self._hug.summary()['parent'].split(' ')[0]
                try:
                    self._hug.update(revision)
                except RuntimeError:
                    # raised when the revision is invalid
                    action.failure(_UNKNOWN_REVISION)
                    return

            # gather data for the outbound converters
            changeset = ''
            if self._vcs == 'mercurial':
                summary = self._hug.summary()
                if 'tag' in summary:
                    changeset = summary['tag']
                else:
                    changeset = summary['parent']

            user_settings = self.read_user_settings()

            # run the outbound conversions
            signals.outbound.STARTED.emit()
            repo_dir = self.get_repo_dir()
            for outbound_dtype in self._registrar.get_registered_formats():
                post = steps.do_outbound_steps(repo_dir, views_info, outbound_dtype, user_settings)
                signals.outbound.CONVERSION_FINISHED.emit(
                    dtype=outbound_dtype,
                    placement=post['placement'],
                    document=post['document'],
                    changeset=changeset)

            # Currently we don't have any need for the outbound converters to write user settings,
            # but it may be necessary in the future. For some reason, this line causes outbound
            # converters to overwrite the Lychee settings to a blank XML file with only the root
            # element. I haven't bothered to figure out why.

            # self.write_user_settings(user_settings)

        finally:
            self._cleanup_for_new_action()
            if initial_revision:
                self._hug.update(initial_revision)

    def _cleanup_for_new_action(self, sect_id=None):
        '''
        Perform required cleanup before starting a new "action."

        :param str sect_id: If known, the @xml:id of the incoming ``<section>`` to convert.
            If provided, any saved "text editor" files will be deleted, to guarantee they
            will not be out-of-sync.

        This method does the following things:
        - Clear the result of the previous inbound conversion step (including "views").
        - Resets the selected inbound converter and views functions.
        - Deletes any saved "text editor" files for the section ID.
        '''
        self._inbound_converted = None
        self._inbound_views_info = None
        steps.flush_inbound_converters()
        steps.flush_inbound_views()

        if sect_id and self._repo_dir:
            shutil.rmtree(os.path.join(self._repo_dir, SAVE_DIR, str(sect_id)), True)

    def _inbound_conversion_finish(self, converted, **kwargs):
        '''
        NOTE: this method will be removed in T113

        Accept the data emitted by an inbound converter. Slot for :const:`inbound.CONVERSION_FINISH`.

        :param converted: Lychee-MEI data for an incoming change.
        :type converted: :class:`lxml.etree.Element`
        '''
        self._inbound_converted = converted
        signals.inbound.CONVERSION_FINISHED.emit()

    def _inbound_views_finish(self, views_info, **kwargs):
        '''
        NOTE: this method will be removed in T113

        Accept the views data from an inbound views processor. Slot for :const:`inbound.VIEWS_FINISH`.

        :param views_info: Views data for an incoming change.
        '''
        self._inbound_views_info = views_info
        signals.inbound.VIEWS_FINISHED.emit()
