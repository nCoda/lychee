#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               document/test/test_document.py
# Purpose:                Tests for the "lychee.document.document" module.
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
Tests for the :mod:`lychee.document.document` module.
'''

import unittest

from lxml import etree

from lychee.document import document


_XMLNS = '{http://www.w3.org/XML/1998/namespace}'
_XMLID = '{}id'.format(_XMLNS)
_MEINS = '{http://www.music-encoding.org/ns/mei}'


class TestSmallThings(unittest.TestCase):
    '''
    Tests for small helper functions that require few tests:
    - :func:`_check_xmlid_chars`
    - :meth:`_set_default`
    '''

    def test__check_xmlid_chars_1(self):
        '''
        Test when there is a " in the string.
        '''
        self.assertFalse(document._check_xmlid_chars('kjkljamai23uoius"2jjl2nj3alks'))

    def test__check_xmlid_chars_2(self):
        '''
        Test when there isn't a " in the string.
        '''
        self.assertTrue(document._check_xmlid_chars('kj123jjli78s098df'))

    def test__set_default_1(self):
        '''
        Key not in the dict; it should return the default.
        '''
        self.assertEqual(42, document._set_default({'a': 12}, 'b', 42))

    def test__set_default_2(self):
        '''
        Key is in the dict; it should return that.
        '''
        doc = document.Document()
        self.assertEqual(12, document._set_default({'a': 12}, 'a', 42))

    def test__make_empty_all_files(self):
        '''
        That _make_empty_all_files() works.
        '''
        # 1.) run the function
        test_path = 'test_all_files.mei'
        actual = document._make_empty_all_files(test_path)
        # 2.) ensure the returned "actual" document is proper
        self.assertIsInstance(actual, etree._ElementTree)
        root = actual.getroot()
        for i, elem in enumerate([x for x in root.iter()]):
            if 0 == i:
                self.assertEqual('{http://www.music-encoding.org/ns/mei}meiCorpus', elem.tag)
            elif 1 == i:
                self.assertEqual('{http://www.music-encoding.org/ns/mei}meiHead', elem.tag)
            elif 2 == i:
                self.assertEqual('{http://www.music-encoding.org/ns/mei}mei', elem.tag)
            else:
                raise AssertionError('i should only be 0, 1, or 2 but it was {}'.format(i))
        # 3.) ensure the saved document is also proper
        actualFile = etree.parse(test_path)
        self.assertIsInstance(actualFile, etree._ElementTree)
        root = actualFile.getroot()
        for i, elem in enumerate([x for x in root.iter()]):
            if 0 == i:
                self.assertEqual('{http://www.music-encoding.org/ns/mei}meiCorpus', elem.tag)
            elif 1 == i:
                self.assertEqual('{http://www.music-encoding.org/ns/mei}meiHead', elem.tag)
            elif 2 == i:
                self.assertEqual('{http://www.music-encoding.org/ns/mei}mei', elem.tag)
            else:
                raise AssertionError('i should only be 0, 1, or 2 but it was {}'.format(i))


class TestGetPutSection(unittest.TestCase):
    '''
    Tests for Document.get_section() and Document.put_section().
    '''

    def test_get_1(self):
        '''
        When the provided "id" starts wth an octothorpe, it should be removed.
        '''
        doc = document.Document()
        doc._sections['123'] = 'some section'
        self.assertEqual('some section', doc.get_section('#123'))

    def test_get_2(self):
        '''
        When the "id" doesn't start with an octothorpe, it shouldn't be removed.
        '''
        doc = document.Document()
        doc._sections['123'] = 'some section'
        self.assertEqual('some section', doc.get_section('123'))

    def test_get_3(self):
        '''
        When the "id" doesn't exist, the function should return None.
        '''
        doc = document.Document()
        doc._sections['123'] = 'some section'
        self.assertIsNone(doc.get_section('888'))

    def test_put_1(self):
        '''
        When the "id" starts with an octothorpe, the section is assigned without the octothorpe.
        '''
        doc = document.Document()
        doc.put_section('#123', 'some section')
        self.assertEqual('some section', doc._sections['123'])

    def test_put_2(self):
        '''
        When the "id" starts without an octothorpe, the section is assigned without the octothorpe.
        '''
        doc = document.Document()
        doc.put_section('123', 'some section')
        self.assertEqual('some section', doc._sections['123'])


class TestGetPutScore(unittest.TestCase):
    '''
    Tests for Document.get_score() and Document.put_score().
    '''

    def test_put_1(self):
        '''
        When the <score> has no <section> elements.
        '''
        doc = document.Document()
        the_score = etree.Element('{}score'.format(_MEINS))
        doc.put_score(the_score)
        self.assertEqual(0, len(doc._score_order))
        self.assertEqual(0, len(doc._sections))

    def test_put_2(self):
        '''
        When the <score> has three <section> elements.
        '''
        section_tag = '{}section'.format(_MEINS)
        doc = document.Document()
        the_score = etree.Element('{}score'.format(_MEINS))
        the_score.append(etree.Element(section_tag, attrib={_XMLID: '123'}))
        the_score.append(etree.Element(section_tag, attrib={_XMLID: '456'}))
        the_score.append(etree.Element(section_tag, attrib={_XMLID: '789'}))
        exp_xmlids = ['123', '456', '789']

        doc.put_score(the_score)

        self.assertEqual(exp_xmlids, doc._score_order)
        self.assertEqual(3, len(doc._sections))
        for xmlid in exp_xmlids:
            self.assertEqual(section_tag, doc._sections[xmlid].tag)
            self.assertEqual(xmlid, doc._sections[xmlid].get(_XMLID))

