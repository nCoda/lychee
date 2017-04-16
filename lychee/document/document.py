#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/document/document.py
# Purpose:                Contains an object representing an MEI document.
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
The :class:`Document` class represents a Lychee-MEI document. In order to ensure compliance with the
Lychee-MEI specification, we recommend using :class:`Document` whenever possible to avoid duplicating
functionality (improperly).

The Lychee-MEI specification is described in :ref:`lychee_mei`. You can find information about
supported Lychee-MEI metadata headers in :ref:`mei_headers`.
'''

import os.path
import random

import six
from six.moves import range

from lxml import etree

import lychee
from lychee import exceptions
from lychee.logs import DOCUMENT_LOG as log
from lychee.namespaces import mei, xlink, xml, lychee as lyns


# translatable strings
_SECTION_NOT_FOUND = 'Could not load <section xml:id="{xmlid}">'
_ERR_MISSING_MEIHEAD = 'missing <meiHead> element in "all_files"'
_ERR_MISSING_MEIHEAD = 'File with <meiHead> is missing.'
_ERR_CORRUPT_MEIHEAD = 'File with <meiHead> is inavlid.'
_ERR_MISSING_REPO_PATH = 'This Document is not using external files.'
_ERR_MISSING_FILE = 'Could not load indicated file.'
_ERR_CORRUPT_TARGET = '@target does not end with ".mei": {0}'
_PUBSTMT_DEFAULT_CONTENTS = 'This is an unpublished Lychee-MEI document.'
_ABJAD_FULL_NAME = 'Abjad API for Formalized Score Control'
_PLACEHOLDER_TITLE = '(Untitled)'
_SAVE_OUT_ERROR = 'Could not save an XML file (IOError).'
_LY_VERSION_MISSING = 'Lychee-MEI file file is missing @ly:version'
_LY_VERSION_MISMATCH = 'Lychee-MEI file has different version than us'
_LY_VERSION_INVALID = 'Lychee-MEI file has invalid @ly:version'


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
    root = etree.Element(mei.MEI_CORPUS)
    root.append(_make_empty_head())
    root.append(etree.Element(mei.MEI))
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

    sections = [x for x in score.findall('./{}'.format(mei.SECTION))]

    if len(sections) != len(order):
        return False

    for i, section in enumerate(sections):
        if order[i] != section.get(xml.ID):
            return False

    return True


def _save_out(this, to_here):
    '''
    Take ``this`` :class:`Element` or :class:`ElementTree` and save ``to_here``.

    :param this: An element (tree) to save to a file.
    :type this: :class:`lxml.etree.Element` or :class:`lxml.etree.ElementTree`
    :param str to_here: The pathname in which to save the file.
    :returns: ``None``
    :raises: :exc:`lychee.exceptions.CannotSaveError` if something messes up
    '''
    # get an ElementTree in "this" and the root Element in "root"
    if isinstance(this, etree._Element):  # pylint: disable=protected-access
        root = this
        this = etree.ElementTree(this)
    else:
        root = this.getroot()
    # make sure the root element has a proper @ly:version attribute
    root.set(lyns.VERSION, lychee.__version__)
    # finally, save it out
    try:
        this.write(to_here, encoding='UTF-8', pretty_print=True, xml_declaration=True)
    except IOError:
        raise exceptions.CannotSaveError(_SAVE_OUT_ERROR)


def _load_in(from_here, recover=None):
    '''
    Try to load an MEI/XML file at the path ``from_here``.

    :param str from_here: The pathname from which to try parsing a file.
    :param bool recover: If ``True``, the XML document will be parsed with a parser object set to
        "recover," which tries "hard to parse through broken XML." Default is ``False``. Generally,
        this should be avoided---callers should make their users aware that they're entering some
        parallel universe when their XML is broken.
    :returns: The MEI/XML document stored at ``from_here``.
    :rtype: :class:`lxml.etree.ElementTree`
    :raises: :exc:`exceptions.FileNotFoundError` if the file does not exist, is not readable, is a
        directory, or something like that.
    :raises: :exc:`exceptions.InvalidFileError` if the file exists and can be loaded, but ``lxml``
        cannot parse a valid XML document from it.
    '''

    if recover is None:
        recover = False

    try:
        return _check_version_attr(etree.parse(from_here, etree.XMLParser(recover=recover)))
    except (IOError, OSError):
        raise exceptions.FileNotFoundError(_ERR_MISSING_FILE)
    except etree.XMLSyntaxError as xse:
        raise exceptions.InvalidFileError(xse.args[0])


@log.wrap('info', 'check LMEI version attribute', 'action')
def _check_version_attr(lmei, action):
    '''
    Check the @ly:version attribute on the root element of an LMEI :class:`ElementTree`.

    :param lmei: An LMEI :class:`ElementTree` to check.
    :type lmei: :class:`lxml.etree.ElementTree`
    :returns: The unmodified LMEI document.
    :rtype: :class:`lxml.etree.ElementTree`

    Currently, this function checks whether the @ly:version attribute is present on the root element
    of the :class:`ElementTree` given, and:

    - if @ly:version is missing, prints an "error" log message
    - if @ly:version is not a proper "semantic versioning" string, prints an "error" log message
    - if @ly:version is different than the version of this Lychee, prints a "warning" log message
    - if @ly:version is the same as the version of this Lychee, continues silently
    '''
    version = lmei.getroot().get(lyns.VERSION)
    if version is None:
        action.failure(_LY_VERSION_MISSING)
    elif version != lychee.__version__:
        version_numbers = version.split('.')
        if len(version_numbers) != 3:
            action.failure(_LY_VERSION_INVALID)
        else:
            try:
                [int(num) for num in version_numbers]
            except ValueError:
                action.failure(_LY_VERSION_INVALID)
            else:
                action.failure(_LY_VERSION_MISMATCH)

    return lmei


def _make_ptr(targettype, target):
    '''
    Make a <ptr> element with the specified ``targettype`` and ``target`` attributes.

    :param str targettype: The value of the @targettype attribute.
    :param str target: The value of the @target attribute.
    :returns: The <ptr>.
    :rtype: :class:`lxml.etree.Element`
    '''
    return etree.Element(mei.PTR,
                         attrib={'targettype': targettype,
                                 'target': target,
                                 xlink.ACTUATE: 'onRequest',
                                 xlink.SHOW: 'embed'})


def _make_empty_head():
    '''
    Produce an "empty" <meiHead> element.

    :returns: The <meiHead> element.
    :rtype: :class:`lxml.etree.Element`

    The output produced is not truly "empty." It contains the minimal information required:

    .. code-block:: xml

        <meiHead>
            <fileDesc>
                <titleStmt>
                    <title>
                        <title type="main">(Untitled)</title>
                    </title>
                </titleStmt>
                <pubStmt>
                    <unpub>This is an unpublished Lychee-MEI document.</unpub>
                </pubStmt>
            </fileDesc>
        </meiHead>
    '''
    mei_head = etree.Element(mei.MEI_HEAD)

    title = mei_head.makeelement(mei.TITLE)
    title_main = mei_head.makeelement(mei.TITLE, attrib={'type': 'main'})
    title_main.text = _PLACEHOLDER_TITLE
    title.append(title_main)
    title_stmt = mei_head.makeelement(mei.TITLE_STMT)
    title_stmt.append(title)

    unpub = mei_head.makeelement(mei.UNPUB)
    unpub.text = _PUBSTMT_DEFAULT_CONTENTS
    pub_stmt = mei_head.makeelement(mei.PUB_STMT)
    pub_stmt.append(unpub)

    file_desc = mei_head.makeelement(mei.FILE_DESC)
    file_desc.append(title_stmt)
    file_desc.append(pub_stmt)

    mei_head.append(file_desc)

    return mei_head


def _load_score_order(repo_path, all_files):
    '''
    Determine the proper "self._score_order" instance variable from the local repository.

    :param repo_path: The repository's directory path.
    :type repo_path: str
    :param all_files: The "all_files" document from which to determine the score order.
    :type all_files: :class:`lxml.etree._Element`
    :returns: An ordered list of the @xml:id attributes of <section> elements in the active score.
    :rtype: list of str
    :raises: :exc:`lychee.exceptions.InvalidFileError` if the <ptr> elements are malformed

    This method requires that "self._all_files" exists. If this is the default returned by
    :func:`_make_empty_all_files`, an empty list is returned. Otherwise, the "score" <ptr> is
    loaded, and the returned value is the @target attributes of contained <ptr> elements for
    which @targettype="section", but without the terminating ".mei" part of the filename. In
    other words, if the repository contains a compliant Lychee-MEI file, this method returns
    a list of the @xml:id of <section> elements in the active score.
    '''

    score_ptr = all_files.find('./{mei}/{ptr}[@targettype="score"]'.format(mei=mei.MEI, ptr=mei.PTR))

    if score_ptr is None:
        return []

    score = _load_in(os.path.join(repo_path, score_ptr.get('target'))).getroot()

    sections = []
    for ptr in score.iterfind('./{ptr}'.format(ptr=mei.PTR)):
        if not ptr.get('target').endswith('.mei'):
            raise exceptions.InvalidFileError(_ERR_MISSING_FILE)
        else:
            sections.append(ptr.get('target')[:-4])

    return sections


def _seven_digits():
    '''
    Produce a string of seven pseudo-random digits.

    :returns: A string with seven pseudo-random digits.
    :rtype: str

    .. note:: The first character will never be 0, so you can rely on the output from this function
        being greater than or equal to one million, and strictly less than ten million.
    '''
    digits = '1234567890'
    len_digits = len(digits)
    post = [None] * 7
    for i in range(7):
        post[i] = digits[random.randrange(0, len_digits)]
    post = ''.join(post)

    if post[0] == '0':
        return _seven_digits()
    else:
        return post


def _check_valid_section_id(xmlid):
    '''
    Determine whether "xmlid" is a valid Lychee-MEI @xml:id value for a ``<section>``.

    :param str xmlid: The @xml:id value to check.
    :returns: Whether "xmlid" is valid.
    :rtype: bool
    '''
    expected_startswith = 'Sme-s-m-l-e'
    expected_len = len('Sme-s-m-l-e1234567')
    try:
        e_part = int(xmlid[len(expected_startswith):])
    except ValueError:
        return False

    if ((expected_len != len(xmlid)) or
        (not xmlid.startswith(expected_startswith)) or
        (e_part < 1000000)):
        return False

    return True



def _init_sections_dict(all_files):
    '''
    Initialize a dictionary with keys corresponding to all the ``<section>`` elements in the
    document, but the keys set to ``None``. In effect, this is enough information to know which
    sections are in a document, but does not spend time loading and caching the sections.

    :param all_files: The "all_files" ``<meiCorpus>`` element from which to load sections.
    :type all_files: :class:`lxml.etree._Element`
    :returns: A dictionary with keys as @xml:id of every ``<section>``.
    :rtype: dict
    :raises: :exc:`lychee.exceptions.InvalidDocumentError` if the @target attribute of a ``<ptr>``
        to a ``<section>`` does not end with ``".mei"``.
    '''
    post = {}

    xpath_query = './{mei}/{ptr}[@targettype="section"]'.format(mei=mei.MEI, ptr=mei.PTR)
    for ptr in all_files.findall(xpath_query):
        target = ptr.get('target')
        if len(target) > 4 and target.endswith('.mei'):
            post[target[:-4]] = None
        else:
            raise exceptions.InvalidDocumentError(_ERR_CORRUPT_TARGET.format(target))

    return post


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

    _APPROVED_HEAD_ELEMENTS = ('fileDesc', 'titleStmt', 'title', 'respStmt', 'arranger', 'author',
        'composer', 'editor', 'funder', 'librettist', 'lyricist', 'sponsor', 'pubStmt')

    def __init__(self, repository_path=None):
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
        self._sections = _init_sections_dict(self._all_files)
        # the <score> element
        self._score = None
        # the order of <section> elements in the <score>, indicated with @xml:id
        self._score_order = _load_score_order(self._repo_path, self._all_files)
        # the <meiHead> element
        self._head = None
        self._head = self.get_head()

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

    def get_section_ids(self, all_sections=False):
        '''
        By default, return the ordered @xml:id attributes of active ``<section>`` elements in this
        score. If ``all_sections`` is ``True``, return the @xml:id attributes of all ``<section>``
        elements in this MEI document, in arbitrary order.

        :param bool all_sections: Whether to return the IDs of all sections in this document, rather
            than just the sections currently active in the score.
        :returns: A list of the section IDs.
        :rtype: list of str
        '''

        if all_sections:
            return [x for x in six.iterkeys(self._sections)]
        else:
            return self._score_order

    # def load_everything(self):
    #     '''
    #     Load all portions of the MEI document from files. This method effectively caches the
    #     document in memory for faster access later.
    #
    #     .. caution:: This method is not yet implemented.
    #     '''
    #     # NB: when you write this, it should just call the other methods
    #     raise NotImplementedError()

    def save_everything(self):
        '''
        Write the MEI document(s) into files.

        :returns: A list of the absolute pathnames that are part of this Lychee-MEI document.
        :rtype: list of str
        :raises: :exc:`lychee.exceptions.CannotSaveError` if the document cannot be written to the
            filesystem (this happens when ``repository_path`` was not supplied on initialization).

        A Lychee-MEI document is a complex of various XML elements. This method arranges for the
        documents stored in memory to be saved into files in the proper arrangement as specified
        by the order.

        Note that the return value includes any file in the document. The files may not have been
        modified, and in fact may not even have been saved at all---they are simply part of this
        document.
        '''

        if self._repo_path is None:
            raise exceptions.CannotSaveError(_ERR_MISSING_REPO_PATH)

        # hold the absolute paths of all modified files
        saved_files = []

        # hold the "all_files.mei" document
        all_files = etree.Element(mei.MEI_CORPUS)

        # hold the <mei> element for "all_files.mei"
        mei_elem = etree.Element(mei.MEI)

        # hold the <meiHead> element for "all_files.mei"
        mei_head = etree.Element(mei.MEI_HEAD)

        # 1.) save the <meiHead> element
        if self._head is not None:
            head_path = os.path.join(self._repo_path, 'head.mei')
            _save_out(self._head, head_path)
            saved_files.append(head_path)
            mei_head.append(_make_ptr('head', 'head.mei'))

        # 2.) build the <score> element and save it
        if len(self._score_order) > 0:
            # make the <score> proper
            score = etree.Element(mei.SCORE)
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
            abs_section_path = os.path.join(self._repo_path, section_path)  # build absolute path
            saved_files.append(abs_section_path)
            if section is not None:
                # assume this <section> was never loaded to begin with
                _save_out(section, abs_section_path)
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
            mei_head = self._all_files.find('./{}'.format(mei.MEI_HEAD))
            if mei_head is None:
                raise exceptions.HeaderNotFoundError(_ERR_MISSING_MEIHEAD)

            # see if there's a <ptr> in the <meiHead>
            ptr = mei_head.find('./{}[@targettype="head"]'.format(mei.PTR))
            if ptr is None:
                # the Document's probably empty; we'll return the <meiHead> we have, and put_head()
                # can save it with a <ptr> later
                self._head = mei_head
            else:
                # otherwise we can load the file specified in the <ptr>
                try:
                    self._head = _load_in(os.path.join(self._repo_path, ptr.get('target'))).getroot()
                except exceptions.FileNotFoundError:
                    raise exceptions.HeaderNotFoundError(_ERR_MISSING_MEIHEAD)
                except exceptions.InvalidFileError:
                    raise exceptions.HeaderNotFoundError(_ERR_CORRUPT_MEIHEAD)

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
                and self._all_files.find('.//{}[@targettype="head"]'.format(mei.PTR)) is None):
            mei_head = self._all_files.find('./{}'.format(mei.MEI_HEAD))
            mei_head.append(etree.Element('{}'.format(mei.PTR),
                                          attrib={'targettype': 'head',
                                                  'target': 'head.mei',
                                                  xlink.ACTUATE: 'onRequest',
                                                  xlink.SHOW: 'embed'}))
        self._head = new_head

    def get_from_head(self, what):
        '''
        Getter for elements in the ``<meiHead>``.

        :param str what: The element name to find. See the list of valid values below.
        :returns: A list of the requested elements.
        :rtype: list of :class:`lxml.etree.Element`

        You may request the following elements:

        - fileDesc
        - titleStmt
        - title
        - respStmt
        - a role (arranger, author, composer, editor, funder, librettist, lyricist, or sponsor)
        - pubStmt

        The "respStmt" child elements describe Lychee users who have edited this document, whether
        or not they hold a more specific role.

        Also note that, if a role-specific element (such as ``<composer>``) corresponds to a Lychee
        user, the role-specific element will contain  a ``<persName>`` with a @nymref attribute
        that holds the @xml:id value of a ``<persName>`` given in the ``<respStmt>``. For example,
        if this work's composer is also the only person who has edited this score:

        >>> etree.dump(doc.get_from_head('composer')[0])
        <composer>
            <persName nymref="#p1234"/>
        </composer>
        >>> etree.dump(doc.get_from_head('respStmt')[0])
        <respStmt>
            <persName xml:id="p1234">
                <persName type="full">Danceathon Smith</persName>
            </persName>
        </respStmt>

        .. note:: At this point in time, :meth:`get_from_head` does not raise (its own) exceptions.
            If the "what" argument is invalid, this is treated the same as a missing element, so the
            return value will be ``None``.
        '''

        if what in Document._APPROVED_HEAD_ELEMENTS:
            if 'title' == what:
                return [self.get_head().find('.//{title}'.format(title=mei.TITLE))]
            else:
                return self.get_head().findall('.//{ns}{tag}'.format(ns=mei.MEINS, tag=what))
        else:
            return []

    def put_in_head(self, new_elem):
        '''
        As per :meth:`get_from_head`, but with setting instead.

        .. warning::
            This method is not implemented.
            Refer to `T109 <https://goldman.ncodamusic.org/T109>`_ for more information.
        '''
        raise NotImplementedError('Document.put_in_head() is not implemented.')

    # def get_ui(self):
    #     '''
    #     Load and return Lychee-specific user interface data.
    #     '''
    #     raise NotImplementedError()

    # def put_ui(self, new_ui):
    #     '''
    #     Save new Lychee-specific user interface data.
    #     '''
    #     raise NotImplementedError()

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
            score = etree.Element(mei.SCORE)
            for xmlid in self._score_order:
                score.append(self.get_section(xmlid))
            self._score = score
            return score

    def put_score(self, new_music):
        '''
        Save a new score in place of the existing one.

        :param new_music: The <score> element to use in place of the existing one.
        :type new_music: :class:`lxml.etree.Element`
        :returns: The @xml:id attributes of all top-level ``<section>`` elements found in
            ``new_music``, in the order they were found.
        :rtype: list of str

        The "score order" in ``new_music`` replaces the existing "score order." Note that existing
        <section> elements that aren't part of ``new_music`` are not deleted---they remain tracked
        internally. Also note that any <section> elements already contained in the local list of
        sections is replaced by the section that has a matching @xml:id in ``new_music``. Sections
        that don't have an @xml:id will be given one.
        '''

        self._score_order = []
        for section in new_music.findall('./{}'.format(mei.SECTION)):
            xmlid = self.put_section(section)
            self._score_order.append(xmlid)

        return self._score_order

    def get_section(self, section_id):
        '''
        Load and return a section of the score.

        :returns: The section with an ``@xml:id`` matching ``section_id``.
        :rtype: :class:`lxml.etree.Element`
        :raises: :exc:`lychee.exceptions.SectionNotFoundError` if no ``<section>`` with the
            specified @xml:id can be found.
        :raises: :exc:`lychee.exceptions.InvalidFileError` if the ``<section>`` is found but cannot
            be loaded because it is invalid.

        **Side Effects**

        If the section is not already loaded, :meth:`get_section` will try to fetch it from the
        filesystem, if a repository is configured.
        '''

        if section_id.startswith('#'):
            section_id = section_id[1:]

        if section_id in self._sections and self._sections[section_id] is not None:
            return self._sections[section_id]
        elif self._repo_path is None:
            raise exceptions.SectionNotFoundError(_SECTION_NOT_FOUND.format(xmlid=section_id))
        else:
            try:
                return _load_in(os.path.join(self._repo_path, section_id + '.mei')).getroot()
            except exceptions.FileNotFoundError:
                raise exceptions.SectionNotFoundError(_SECTION_NOT_FOUND.format(xmlid=section_id))
            except exceptions.InvalidFileError:
                raise

    def put_section(self, new_section):
        '''
        Add or replace a ``<section>`` in the current MEI document.

        :param new_section: A new section or a replacement for an existing section with the same
            @xml:id attribute.
        :type new_section: :class:`lxml.etree.Element`
        :returns: The @xml:id of the saved ``new_section``.
        :rtype: str

        .. note:: If ``new_section`` is missing an @xml:id attribute, or has an invalid @xml:id
            attribute, a new one is created.
        '''

        xmlid = new_section.get(xml.ID)

        if xmlid is None or not _check_valid_section_id(xmlid):
            xmlid = 'Sme-s-m-l-e{}'.format(_seven_digits())
            new_section.set(xml.ID, xmlid)

        self._sections[xmlid] = new_section
        return xmlid

    def move_section_to(self, xmlid, position):
        '''
        Move a ``<section>`` to another position in the score.

        :arg string xmlid: The @xml:id attribute of the ``<section>`` to move. The section may or
            may not already be in the active score, but it must already be part of the document.
        :arg int position: The requested new index of the section in the active score.
        :raises: :exc:`~lychee.exceptions.SectionNotFoundError` if the ``<section>`` to move is not
            found in the repository.

        Note that this function simply moves the indicated section to the requested position, but
        does not save the :class:`Document` instance or anything else (e.g., does not cause an
        outbound conversion that would update code external to *Lychee*).
        '''
        position = int(position)

        if xmlid not in self.get_section_ids(all_sections=True):
            raise exceptions.SectionNotFoundError(_SECTION_NOT_FOUND.format(xmlid=xmlid))

        score_order = self._score_order

        if xmlid in score_order:
            curr_pos = score_order.index(xmlid)
            if curr_pos < position:
                position -= 1
            del score_order[curr_pos]

        score_order.insert(position, xmlid)

        self._score_order = score_order
