#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/document/document.py
# Purpose:                Contains an object representing an MEI document.
#
# Copyright (C) 2015 Christopher Antila
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
Contains an object representing an MEI document.
'''

import os.path

from lxml import etree

from lychee import exceptions


_XMLNS = '{http://www.w3.org/XML/1998/namespace}'
_XMLID = '{}id'.format(_XMLNS)
_XLINK = '{http://www.w3.org/1999/xlink}'
_MEINS = '{http://www.music-encoding.org/ns/mei}'
_SCORE = '{}score'.format(_MEINS)
_SECTION = '{}section'.format(_MEINS)

_SECTION_NOT_FOUND = 'Could not load <section xml:id="{xmlid}">'
_ERR_MISSING_MEIHEAD = 'missing <meiHead> element in "all_files"'
_ERR_FAILED_LOADING_MEIHEAD = 'failed to load <meiHead> file'
_ERR_MISSING_REPO_PATH = 'This Document is not using external files.'


def _check_xmlid_chars(xmlid):
    '''
    Ensure the only characters in a string are acceptable as an @xml:id.

    At the moment, this only checks that a ``"`` (double-quote) character is not in the string. If
    I can figure out what the XML:ID spec really means, then it may be restricted further... but it
    doesn't seem to be the case!

    :param str xmlid: The @xml:id string to check.
    :returns: ``True`` if all the characters are valid in an @xml:id string, otherwise ``False``.
    '''
    return '"' not in xmlid


def _set_default(here, this, that):
        '''
        Returns ``here[this]``, if ``this`` is a key in ``here``, otherwise returns ``that``.

        **Examples**

        >>> _set_default({'a': 12}, 'a', 42)
        12
        >>> _set_default({'a': 12}, 'b', 42)
        42
        '''
        if this in here:
            return here[this]
        else:
            return that


def _make_empty_all_files(pathname):
    '''
    Produce and return an empty ``all_files.mei`` file that will be used to cross-reference all
    other files in this repository.

    :param str pathname: The pathname to use for the file---must include the "all_files.mei" part.
        If ``pathname`` is ``None``, the file will not be saved.
    :returns: The XML document produced.
    :rtype: :class:`lxml.etree.ElementTree`
    '''
    root = etree.Element('{}meiCorpus'.format(_MEINS))
    root.append(etree.Element('{}meiHead'.format(_MEINS)))
    root.append(etree.Element('{}mei'.format(_MEINS)))
    tree = etree.ElementTree(root)
    if pathname is not None:
        _save_out(tree, pathname)
    return tree


def _ensure_score_order(score, order):
    '''
    Ensure there are <section> elements in ``score`` with the same @xml:id attributes, in the same
    order, as they appear in ``order``.

    :param score: The <score> element in which to inspect the <section> elements.
    :type score: :class:`lxml.etree.Element`
    :param order: List of the expected @xml:id attribute values, in the order desired.
    :type order: list of str
    :returns: Whether the desired <section> elements are in the proper order.
    :rtype: bool

    **Examples**

    >>> score_tag = '{http://www.music-encoding.org/ns/mei}score'
    >>> section_tag = '{http://www.music-encoding.org/ns/mei}section'
    >>> xmlid_tag = '{http://www.w3.org/XML/1998/namespace}id'
    >>> from lxml import etree
    >>> score = etree.Element(score_tag)
    >>> score.append(etree.Element(section_tag, attrib={xmlid_tag: '123'}))
    >>> score.append(etree.Element(section_tag, attrib={xmlid_tag: '456'}))
    >>> score.append(etree.Element(section_tag, attrib={xmlid_tag: '789'}))
    >>> _ensure_score_order(score, ['123', '456', '789'])
    True
    >>> _ensure_score_order(score, ['123', '789'])
    False
    >>> _ensure_score_order(score, ['123', '789', '456'])
    False
    >>> _ensure_score_order(score, ['123', '234', '456', '789'])
    False
    '''

    sections = [x for x in score.findall('./{}'.format(_SECTION))]

    if len(sections) != len(order):
        return False

    for i, section in enumerate(sections):
        if order[i] != section.get(_XMLID):
            return False

    return True


def _save_out(this, to_here):
    '''
    Take ``this`` :class:`Element` or :class:`ElementTree` and save ``to_here``.

    :param this: An element (tree) to save to a file.
    :type this: :class:`lxml.etree.Element` or :class:`lxml.etree.ElementTree`
    :param str to_here: The pathname in which to save the file.
    :returns: ``None``
    :raises: :exc:`OSError` if something messes up
    '''
    if isinstance(this, etree._Element):
        this = etree.ElementTree(this)
    this.write_c14n(to_here)


def _make_ptr(targettype, target):
    '''
    Make a <ptr> element with the specified ``targettype`` and ``target`` attributes.

    :param str targettype: The value of the @targettype attribute.
    :param str target: The value of the @target attribute.
    :returns: The <ptr>.
    :rtype: :class:`lxml.etree.Element`
    '''
    return etree.Element('{}ptr'.format(_MEINS),
                         attrib={'targettype': targettype,
                                 'target': target,
                                 '{}actuate'.format(_XLINK): 'onRequest',
                                 '{}show'.format(_XLINK): 'embed'})


class Document(object):
    '''
    Object representing an MEI document. Use methods prefixed with ``get`` to obtain portions of
    the document, automatically loading from files if required. Use methods prefixed with ``put``
    to submit a new portion to *replace* the existing portion outright.

    If you do not provide a ``repository_path`` argument to the initialization method, no files will
    be written. Additionally, the :meth:`save_everything` method therefore will not work, and all
    :meth:`get_` methods will not return useful data until they have been given data.

    .. note:: When you use a :meth:`put_` method, the element(s) replace those already present in
        this :class:`Document` instance, but they will not be written to the document's directory
        until you call :meth:`save_everything` or the context manager exits, if applicable.

    The recommended way to use a :class:`Document` with file output is as a context manager (using
    a :obj:`with` statement). This way, you cannot forget to save your changes to the filesystem.
    '''

    def __init__(self, repository_path=None, **kwargs):
        '''
        :param str repository_path: Path to a directory in which the files for this :class:`Document`
            are or will be stored. The default of ``None`` will not save any files.
        '''

        # path to the Mercurial repository directory
        self._repo_path = repository_path

        # file that indicates the other files in this repository
        self._all_files_path = None
        if self._repo_path is None:
            self._all_files = _make_empty_all_files(None)
        else:
            self._all_files_path = os.path.join(self._repo_path, 'all_files.mei')
            if os.path.exists(self._all_files_path):
                self._all_files = etree.parse(self._all_files_path)
            else:
                self._all_files = _make_empty_all_files(self._all_files_path)

        # @xml:id to the <section> with that id
        self._sections = {}
        # the <score> element
        self._score = None
        # the order of <section> elements in the <score>, indicated with @xml:id
        self._score_order = []
        # the <meiHead> element
        self._head = None

    def __enter__(self):
        '''
        Start a context manager for :class:`Document`.
        '''
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        Save all sections into files and stuff.
        '''
        # In the future, we should "auto-heal" from some exceptions that were raised by methods in
        # this class.
        if exc_type is None:
            if self._repo_path is not None:
                self.save_everything()
            return True
        else:
            return False

    def load_everything(self):
        '''
        Load all portions of the MEI document from files. This method effectively caches the
        document in memory for faster access later.

        .. note:: Unlike the other ``get``-prefixed methods, this method returns nothing.
        '''
        # TODO: when you write this, it should just call the other methods
        raise NotImplementedError()

    def save_everything(self):
        '''
        Write the MEI document(s) into files.

        :returns: A list of the absolute pathnames written out. This does not imply that all the
            files have changed---just that they are part of the MEI document as it now exists.
        :rtype: list of str
        :raises: :exc:`lychee.exceptions.CannotSaveError` if the document cannot be written to the
            filesystem (this happens when ``repository_path`` was not supplied on initialization).

        A Lychee-MEI document is a complex of various XML elements. This method arranges for the
        documents stored in memory to be saved into files in the proper arrangement as specified
        by the order.
        '''

        if self._repo_path is None:
            raise exceptions.CannotSaveError(_ERR_MISSING_REPO_PATH)

        # hold the absolute paths of all modified files
        saved_files = []

        # hold the "all_files.mei" document
        all_files = etree.Element('{}meiCorpus'.format(_MEINS))

        # hold the <mei> element for "all_files.mei"
        mei_elem = etree.Element('{}mei'.format(_MEINS))

        # hold the <meiHead> element for "all_files.mei"
        mei_head = etree.Element('{}meiHead'.format(_MEINS))

        # 1.) save the <meiHead> element
        if self._head is not None:
            head_path = os.path.join(self._repo_path, 'head.mei')
            _save_out(self._head, head_path)
            saved_files.append(head_path)
            mei_head.append(_make_ptr('head', 'head.mei'))

        # 2.) build the <score> element and save it
        if len(self._score_order) > 0:
            # make the <score> proper
            score = etree.Element('{}score'.format(_MEINS))
            for xmlid in self._score_order:
                section_path = '{}.mei'.format(xmlid)  # path relative to "all_files.mei"
                score.append(_make_ptr('section', section_path))
            score_path = os.path.join(self._repo_path, 'score.mei')
            _save_out(score, score_path)
            saved_files.append(score_path)
            # put a <ptr> in "all_files"
            mei_elem.insert(0, _make_ptr('score', 'score.mei'))

        # 3.) save contained <section> elements
        section_paths = []
        for xmlid, section in self._sections.items():
            section_path = '{}.mei'.format(xmlid)  # path relative to "all_files.mei"
            section_paths.append(section_path)
            section_path = os.path.join(self._repo_path, section_path)  # build absolute path
            _save_out(section, section_path)
            saved_files.append(section_path)
        section_paths = sorted(section_paths)
        for each_path in section_paths:
            mei_elem.append(_make_ptr('section', each_path))

        # 5.) save "all_files.mei"
        all_files.append(mei_head)
        all_files.append(mei_elem)
        self._all_files = all_files
        _save_out(self._all_files, self._all_files_path)
        saved_files.append(self._all_files_path)

        return saved_files

    def get_head(self):
        '''
        Load and return the MEI header metadata.

        :returns: The ``<meiHead>`` portion of the MEI document.
        :rtype: :class:`lxml.etree.Element`
        :raises: :exc:`lychee.exceptions.HeaderNotFoundError` if the ``<meiHead>`` element is
            missing or it contains a ``<ptr>`` without a @target attribute
        '''

        # if self._head hasn't been loaded/created, we'll do that now
        if self._head is None:
            # make sure "_all_files" contains an <meiHead>
            mei_head = self._all_files.find('./{}meiHead'.format(_MEINS))
            if mei_head is None:
                raise exceptions.HeaderNotFoundError(_ERR_MISSING_MEIHEAD)

            # see if there's a <ptr> in the <meiHead>
            ptr = mei_head.find('./{}ptr[@targettype="head"]'.format(_MEINS))
            if ptr is None:
                # the Document's probably empty; we'll return the <meiHead> we have, and put_head()
                # can save it with a <ptr> later
                self._head = mei_head
            else:
                # otherwise we can load the file specified in the <ptr>
                try:
                    self._head = etree.parse(ptr.get('target', default='')).getroot()
                except OSError:
                    raise exceptions.HeaderNotFoundError(_ERR_FAILED_LOADING_MEIHEAD)

        return self._head

    def put_head(self, new_head):
        '''
        Save new header metadata.

        :param: new_head: An ``<meiHead>`` element that should replace the existing one.
        :type new_head: :class:`lxml.etree.Element`
        '''

        # I admit this is a little weird, so maybe we'll change it later. But for now the idea is
        # that the presence of the <ptr> in the "all_files" file will indicate whether we have an
        # <meiHead> with useful information, or just empty.
        if (self._repo_path is not None
            and self._all_files.find('.//{}ptr[@targettype="head"]'.format(_MEINS)) is None):
            mei_head = self._all_files.find('./{}meiHead'.format(_MEINS))
            mei_head.append(etree.Element('{}ptr'.format(_MEINS),
                                          attrib={'targettype': 'head',
                                                  'target': 'head.mei',
                                                  '{}actuate'.format(_XLINK): 'onRequest',
                                                  '{}show'.format(_XLINK): 'embed'}))
        self._head = new_head

    def get_ui(self):
        '''
        Load and return Lychee-specific user interface data.

        :returns: Some element... ???
        :rtype: :class:`lxml.etree.Element`
        '''
        raise NotImplementedError()

    def put_ui(self, new_ui):
        '''
        Save new Lychee-specific user interface data.

        :param new_ui: Some element... ???
        :type new_ui: :class:`lxml.etree.Element`
        '''
        raise NotImplementedError()

    def get_score(self):
        '''
        Load and return the whole score, excluding metadata and "inactive" ``<section>`` elements.

        :returns: A ``<score>`` element with relevant ``<section>`` elements in the proper order.
        :rtype: :class:`lxml.etree.Element`
        :raises: :exc:`lychee.exceptions.SectionNotFoundError` if one or more of the ``<section>``
            elements require for the ``<score>`` cannot be found.

        **Side Effect**

        Caches the returned ``<score>`` for later access.
        '''

        if self._score is not None and _ensure_score_order(self._score, self._score_order):
            return self._score
        else:
            score = etree.Element('{}score'.format(_MEINS))
            for xmlid in self._score_order:
                score.append(self.get_section(xmlid))
            self._score = score
            return score

    def put_score(self, new_music):
        '''
        Save a new score in place of the existing one. The "score order" in ``new_music`` is taken
        to replace the existing "score order." Note that <section> elements not included in
        ``new_music`` are not deleted---they remain tracked in "all_files." Also note that any
        <section> elements already contained in the local list of sections is replaced by the
        section that has a matching @xml:id in ``new_music``.

        :param new_music: The <score> element to use in place of the existing one.
        :type new_music: :class:`lxml.etree.Element`
        '''
        score_order = []
        for section in new_music.findall('./{}section'.format(_MEINS)):
            xmlid = section.get(_XMLID)
            score_order.append(xmlid)
            self._sections[xmlid] = section

        self._score = new_music
        self._score_order = score_order

    def get_section(self, section_id):
        '''
        Load and return a section of the score.

        :returns: The section with an ``@xml:id`` matching ``section_id``.
        :rtype: :class:`lxml.etree.Element`
        :raises: :exc:`lychee.exceptions.SectionNotFoundError` if no ``<section>`` with the
            specified @xml:id can be found.

        **Side Effects**

        If the section is not found, :meth:`get_section` first tries to load the section with
        :meth:`load_everything` before failing.
        '''

        if section_id.startswith('#'):
            section_id = section_id[1:]

        try:
            return self._sections[section_id]
        except KeyError:
            self.load_everything()
            try:
                return self._sections[section_id]
            except KeyError:
                raise exceptions.SectionNotFoundError(_SECTION_NOT_FOUND.format(xmlid=section_id))

    def put_section(self, section_id, new_section):
        '''

        In the future, you will be able to submit a section that is an element other than
        ``<section>``. For now, doing so will raise a :exc:`NotImplementedError`.

        :param new_section: A replacement for the section with ``section_id``.
        :type new_section: :class:`lxml.etree.Element`
        '''
        if section_id.startswith('#'):
            section_id = section_id[1:]

        self._sections[section_id] = new_section
