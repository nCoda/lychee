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

import os
import os.path
import unittest
from unittest import mock

from lxml import etree

from lychee import exceptions
from lychee.document import document


_XMLNS = '{http://www.w3.org/XML/1998/namespace}'
_XMLID = '{}id'.format(_XMLNS)
_MEINS = '{http://www.music-encoding.org/ns/mei}'
_SCORE = '{}score'.format(_MEINS)
_SECTION = '{}section'.format(_MEINS)


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
        # 1.) ensure we won't overwrite some file
        test_path = 'test_all_files.mei'
        if os.path.exists(test_path):
            raise AssertionError('cannot do this test because {} would be overwritten'.format(test_path))
        # 2.) run the function
        actual = document._make_empty_all_files(test_path)
        # 3.) ensure the returned "actual" document is proper
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
        # 4.) ensure the saved document is also proper
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
        # 5.) delete the test file
        os.remove(test_path)


class TestEnsureScoreOrder(unittest.TestCase):
    '''
    Tests for document._ensure_score_order().
    '''

    def test__ensure_score_order_1(self):
        '''
        When the sections are in the expected order.
        '''
        score = etree.Element(_SCORE)
        score.append(etree.Element(_SECTION, attrib={_XMLID: '123'}))
        score.append(etree.Element(_SECTION, attrib={_XMLID: '456'}))
        score.append(etree.Element(_SECTION, attrib={_XMLID: '789'}))
        order = ['123', '456', '789']
        self.assertTrue(document._ensure_score_order(score, order))

    def test__ensure_score_order_2(self):
        '''
        When "score" has more sections than "order" wants.
        '''
        score = etree.Element(_SCORE)
        score.append(etree.Element(_SECTION, attrib={_XMLID: '123'}))
        score.append(etree.Element(_SECTION, attrib={_XMLID: '456'}))
        score.append(etree.Element(_SECTION, attrib={_XMLID: '789'}))
        order = ['123', '789']
        self.assertFalse(document._ensure_score_order(score, order))

    def test__ensure_score_order_3(self):
        '''
        When "score" and "order" are in a different order.
        '''
        score = etree.Element(_SCORE)
        score.append(etree.Element(_SECTION, attrib={_XMLID: '123'}))
        score.append(etree.Element(_SECTION, attrib={_XMLID: '456'}))
        score.append(etree.Element(_SECTION, attrib={_XMLID: '789'}))
        order = ['123', '789', '456']
        self.assertFalse(document._ensure_score_order(score, order))

    def test__ensure_score_order_4(self):
        '''
        When "score" has fewer sections than "order" wants.
        '''
        score = etree.Element(_SCORE)
        score.append(etree.Element(_SECTION, attrib={_XMLID: '123'}))
        score.append(etree.Element(_SECTION, attrib={_XMLID: '456'}))
        score.append(etree.Element(_SECTION, attrib={_XMLID: '789'}))
        order = ['123', '234', '456', '789']
        self.assertFalse(document._ensure_score_order(score, order))

    def test__ensure_score_order_5(self):
        '''
        When "order" has no elements.
        '''
        score = etree.Element(_SCORE)
        score.append(etree.Element(_SECTION, attrib={_XMLID: '123'}))
        score.append(etree.Element(_SECTION, attrib={_XMLID: '456'}))
        score.append(etree.Element(_SECTION, attrib={_XMLID: '789'}))
        order = []
        self.assertFalse(document._ensure_score_order(score, order))

    def test__ensure_score_order_6(self):
        '''
        When "score" has no child elements.
        '''
        score = etree.Element(_SCORE)
        order = ['123', '456', '789']
        self.assertFalse(document._ensure_score_order(score, order))


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

    @mock.patch('lychee.document.Document.load_everything')
    def test_get_3(self, mock_load_everything):
        '''
        When the "id" doesn't exist, see if calling self.load_everything() will load the section.
        In this case, it does.
        '''
        section_id = '888'
        the_section = 'some section'
        doc = document.Document()
        def loader():
            doc._sections[section_id] = the_section
        mock_load_everything.side_effect = loader
        expected = the_section

        actual = doc.get_section(section_id)

        self.assertEqual(expected, actual)
        mock_load_everything.assert_called_once_with()

    @mock.patch('lychee.document.Document.load_everything')
    def test_get_4(self, mock_load_everything):
        '''
        When the "id" doesn't exist, see if calling self.load_everything() will load the section.
        In this case, it doesn't, so the function should raise SectionNotFoundError.
        '''
        doc = document.Document()
        doc._sections['123'] = 'some section'
        with self.assertRaises(exceptions.SectionNotFoundError) as exc:
            doc.get_section('888')
        self.assertEqual(document._SECTION_NOT_FOUND.format(xmlid='888'), exc.exception.args[0])
        mock_load_everything.assert_called_once_with()

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

    @mock.patch('lychee.document.document._ensure_score_order')
    @mock.patch('lychee.document.Document.get_section')
    def test_get_1(self, mock_get_section, mock_score_order):
        '''
        When self._score is something, and _ensure_score_order() says it's good.
        '''
        doc = document.Document()
        the_score = mock.MagicMock()
        the_order = [1, 2, 3]
        doc._score = the_score
        doc._score_order = the_order
        mock_score_order.return_value = True
        expected = the_score

        actual = doc.get_score()

        self.assertEqual(expected, actual)
        mock_score_order.assert_called_once_with(the_score, the_order)
        self.assertEqual(0, mock_get_section.call_count)

    @mock.patch('lychee.document.document._ensure_score_order')
    @mock.patch('lychee.document.Document.get_section')
    def test_get_2(self, mock_get_section, mock_score_order):
        '''
        When self._score is something, and _ensure_score_order() says it's bad.
        Uses self.get_section() to build a new score.
        Saves the result in self._score.
        '''
        mock_get_section.side_effect = lambda x: etree.Element(x)
        doc = document.Document()
        the_score = mock.MagicMock()
        the_order = ['one', 'two', 'three']
        doc._score = the_score
        doc._score_order = the_order
        mock_score_order.return_value = False

        actual = doc.get_score()

        mock_score_order.assert_called_once_with(the_score, the_order)
        self.assertEqual(3, mock_get_section.call_count)
        mock_get_section.assert_any_call('one')
        mock_get_section.assert_any_call('two')
        mock_get_section.assert_any_call('three')
        children = [x for x in actual.findall('*')]
        self.assertEqual(3, len(children))
        self.assertEqual('one', children[0].tag)
        self.assertEqual('two', children[1].tag)
        self.assertEqual('three', children[2].tag)

    @mock.patch('lychee.document.document._ensure_score_order')
    @mock.patch('lychee.document.Document.get_section')
    def test_get_3(self, mock_get_section, mock_score_order):
        '''
        When self._score is something, and _ensure_score_order() says it's bad.
        Uses self.get_section() to build a new score, but it raises SectionNotFoundError.
        Raises SectionNotFoundError.
        '''
        mock_get_section.side_effect = exceptions.SectionNotFoundError
        doc = document.Document()
        the_score = mock.MagicMock()
        the_order = ['one', 'two', 'three']
        doc._score = the_score
        doc._score_order = the_order
        mock_score_order.return_value = False

        with self.assertRaises(exceptions.SectionNotFoundError):
            doc.get_score()

        mock_score_order.assert_called_once_with(the_score, the_order)
        mock_get_section.assert_called_once_with('one')
