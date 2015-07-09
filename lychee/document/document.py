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


_XMLNS = '{http://www.w3.org/XML/1998/namespace}'
_XMLID = '{}id'.format(_XMLNS)
_MEINS = '{http://www.music-encoding.org/ns/mei}'


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
    :returns: The XML document produced.
    :rtype: :class:`lxml.etree.ElementTree`
    '''
    root = etree.Element('{}meiCorpus'.format(_MEINS))
    root.append(etree.Element('{}meiHead'.format(_MEINS)))
    root.append(etree.Element('{}mei'.format(_MEINS)))
    tree = etree.ElementTree(root)
    tree.write_c14n(pathname, exclusive=False, inclusive_ns_prefixes=['mei'])
    return tree


class Document(object):
    '''
    Object representing an MEI document. Use methods prefixed with ``get`` to obtain portions of
    the document, automatically loading from files if required. Use methods preifxed with ``put``
    to submit a new portion to *replace* the existing portion outright.
    '''

    def __init__(self, **kwargs):
        '''
        The initialization method accepts no arguments.

        :kwarg str repository_pathname: The pathname, relative or absolute, to where the Lychee-MEI
            files are stored. Default is "testrepo."
        '''
        # TODO: tests for this method

        # path to the Mercurial repository directory
        self.repository_pathname = _set_default(kwargs, 'repository_pathname', 'testrepo')

        # file that indicates the other files in this repository
        #self._all_files_file = os.path.join(self.repository_pathname, 'all_files.mei')
        #if os.path.exists(self._all_files_file):
            #self._all_files = etree.parse(self._all_files_file)
        #else:
            #self._all_files = _make_empty_all_files(self._all_files_file)

        # TODO: the "metadata" file

        # files that hold MEI <section> elements; @xml:id to Element
        # TODO: this bit is questionably working
        self._sections = {}
        #for pointer in self._all_files.findall('.//ptr[@targettype="section"]'):
            #section = etree.parse(pointer.get('target')).getroot()
            #self._sections[section.get('xml:id')] = section

        # the <score> element
        self._score = None
        # the order of <section> elements in the <score>, indicated with @xml:id
        self._score_order = []

    def get_everything(self):
        '''
        Load all portions of the MEI document from files. This method effectively caches the
        document in memory for faster access later.

        .. note:: Unlike the other ``get``-prefixed methods, this method returns nothing.
        '''
        raise NotImplementedError()

    def save_everything(self):
        '''
        Writes the MEI document(s) into files. For now, it just writes "self._score."

        :returns: A list of the pathnames modified during the write-to-files.
        :rtype: list of str
        '''
        chree = etree.ElementTree(self._score)
        chree.write(self.output_filename,
                    encoding='UTF-8',
                    xml_declaration=True,
                    pretty_print=True)
        return [self.output_filename]

    def get_head(self):
        '''
        Load and return the MEI header metadata.

        :returns: The ``<head>`` portion of the MEI document.
        :rtype: :class:`lxml.etree.Element`
        '''
        raise NotImplementedError()

    def put_head(self, new_head):
        '''
        Save new header metadata.

        :param: new_head: A ``<head>`` element that should replace the existing one.
        :type new_head: :class:`lxml.etree.Element`
        '''
        raise NotImplementedError()

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

        :returns: A ``<music>`` element.
        :rtype: :class:`lxml.etree.Element`
        '''
        raise NotImplementedError()

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

        Returns ``None`` if there is no ``<section>`` with the given ``@xml:id``.

        :returns: The section with an ``@xml:id`` matching ``section_id``.
        :rtype: :class:`lxml.etree.Element`
        '''
        if section_id.startswith('#'):
            section_id = section_id[1:]

        try:
            return self._sections[section_id]
        except KeyError:
            return None

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
