#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/workflow/session.py
# Purpose:                Manage a document editing session through several workflow actions.
#
# Copyright (C) 2016 Christopher Antila
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

from mercurial import error as hg_error
import hug

import lychee
from lychee.converters import registrar
from lychee.document import document
from lychee import exceptions
from lychee import signals
from lychee.workflow import steps


_CANNOT_SAFELY_HG_INIT = 'Could not safely initialize the repository'
_CANNOT_MAKE_HG_DIR = 'Could not create repository directory'


def _error_slot(**kwargs):
    '''
    Slot for *_ERROR signals in any module.
    '''
    if 'msg' in kwargs:
        lychee.log('Caught an ERROR signal: {}'.format(kwargs['msg']), level='error')
    else:
        lychee.log('Caught an ERROR signal without a messge.', level='error')


signals.inbound.CONVERSION_ERROR.connect(_error_slot)
signals.inbound.VIEWS_ERROR.connect(_error_slot)
signals.vcs.ERROR.connect(_error_slot)
signals.outbound.ERROR.connect(_error_slot)


class InteractiveSession(object):
    '''
    Manage the Lychee-MEI :class:`~lychee.document.Document`, Mercurial repository, and
    other related data for an interactive music notation session.
    '''

    def __init__(self, *args, **kwargs):
        '''
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
        signals.inbound.CONVERSION_FINISH.connect(self.inbound_conversion_finish)
        signals.inbound.VIEWS_FINISH.connect(self.inbound_views_finish)

        # thse should be cleared for each action
        self._inbound_converted = None
        self._inbound_views_info = None

    def __del__(self):
        '''
        If this session is using a temporary directory, delete it.
        '''
        self.unset_repo_dir()

    def get_document(self):
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

    def set_repo_dir(self, path):
        '''
        Change the pathname to Lychee's repository.

        :param str path: The pathname of the directory of the repository. This should either be an
            absolute path or something that will become absolute with :func:`os.path.abspath`.
        :returns: The absolute pathname to the repository directory.
        :rtype: str
        :raises: :exc:`~lychee.exceptions.RepositoryError` when ``path`` exists and contains files
            but is not a Mercurial repository, or is a repository but cannot be written to.
        :raises: :exc:`~lychee.exceptions.RepositoryError` when ``path`` does not exist and cannot
            be created.

        If ``path`` does not exist, it will be created.

        If ``path`` is ``''`` (an empty string) the repository will be initialized in a new
        temporary directory that should be automatically deleted.

        .. warning:: If this :class:`InteractiveSession` instance already has a repository in a
            temporary directory, it will be deleted before the new repository directory is set.
        '''
        self.unset_repo_dir()

        if '' == path:
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

        try:
            self._hug = hug.Hug(self._repo_dir, safe=True)
        except hg_error.RepoError:
            raise exceptions.RepositoryError(_CANNOT_SAFELY_HG_INIT)

        return self._repo_dir

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
            return self.set_repo_dir('')

    def _action_start(self, **kwargs):
        '''
        Slot for the ACTION_START signal.

        :kwarg dtype: As the :const:`lychee.signals.ACTION_START` signal.
        :kwarg doc: As the :const:`lychee.signals.ACTION_START` signal.

        Emits the :const:`lychee.signals.outbound.CONVERSION_FINISHED` signal on completion. May
        also cause a bunch of different error signals if there's a problem.
        '''
        self._cleanup_for_new_action()

        try:
            if 'dtype' in kwargs and 'doc' in kwargs:
                # only do the inbound, document, and VCS steps if there's an incoming change
                try:
                    self._run_inbound_doc_vcs(kwargs['dtype'], kwargs['doc'])
                except exceptions.InboundConversionError:
                    return

            signals.outbound.STARTED.emit()
            for outbound_dtype in self._registrar.get_registered_formats():
                post = steps.do_outbound_steps(
                    self.get_repo_dir(),
                    self._inbound_views_info,  # might be None, but that's okay
                    outbound_dtype)
                signals.outbound.CONVERSION_FINISHED.emit(
                    dtype=outbound_dtype,
                    placement=post['placement'],
                    document=post['document'])

        finally:
            self._cleanup_for_new_action()

    def _run_inbound_doc_vcs(self, dtype, doc):
        '''
        Helper method for :meth:`_action_start`.

        :arg str dtype: From the :const:`~lychee.signals.ACTION_START` signal.
        :arg ??? doc: From the :const:`~lychee.signals.ACTION_START` signal.
        :raises: :exc:`lychee.exceptions.InboundConversionError` when the conversion or views
            processing steps fail.

        When there is an incoming change, :meth:`_action_start` uses this method to run the inbound
        conversion and views processing, document, and VCS steps. The functionality is held in this
        helper method to ease testing and error-handling.
        '''
        steps.do_inbound_conversion(
            session=self,
            dtype=dtype,
            document=doc)
        if self._inbound_converted is None:
            raise exceptions.InboundConversionError()

        steps.do_inbound_views(
            session=self,
            dtype=dtype,
            document=doc,
            converted=self._inbound_converted)
        if self._inbound_views_info is None:
            raise exceptions.InboundConversionError()

        document_pathnames = steps.do_document(
            converted=self._inbound_converted,
            session=self,
            views_info=self._inbound_views_info)

        steps.do_vcs(session=self, pathnames=document_pathnames)

    def _cleanup_for_new_action(self):
        '''
        Perform required cleanup before starting a new "action."

        This cleanup should not normally be needed. This method is a cross-check in case a module
        failed or errored, or otherwise did not clean up after itself.
        '''
        self._inbound_converted = None
        self._inbound_views_info = None
        steps.flush_inbound_converters()
        steps.flush_inbound_views()

    def inbound_conversion_finish(self, converted, **kwargs):
        '''
        Accept the data emitted by an inbound converter. Slot for :const:`inbound.CONVERSION_FINISH`.

        :param converted: Lychee-MEI data for an incoming change.
        :type converted: :class:`lxml.etree.Element`
        '''
        self._inbound_converted = converted
        signals.inbound.CONVERSION_FINISHED.emit()

    def inbound_views_finish(self, views_info, **kwargs):
        '''
        Accept the views data from an inbound views processor. Slot for :const:`inbound.VIEWS_FINISH`.

        :param views_info: Views data for an incoming change.
        :type views_info: ????????????????
        '''
        self._inbound_views_info = views_info
        signals.inbound.VIEWS_FINISHED.emit()
