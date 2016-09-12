#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               document/test/test_document.py
# Purpose:                Tests for the "lychee.document.document" module.
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
Tests for the :mod:`lychee.document.document` module.
'''

# pylint: disable=protected-access

import inspect
import os
import os.path
import shutil
import tempfile
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

import pytest
import six

from lxml import etree

import hug

import lychee
from lychee import exceptions
from lychee.document import document
from lychee.namespaces import mei, xlink, xml, lychee as lyns
from lychee.workflow import session


class DocumentTestCase(unittest.TestCase):
    '''
    Base for test cases that use an instance of :class:`lychee.document.Document`. The setUp()
    method here does some things those test cases will want.
    '''

    def assertElementsEqual(self, first, second, msg=None):
        '''
        Type-specific equality function for :class:`lxml.etree.Element` and
        :class:`lxml.etree.ElementTree` objects.
        '''
        first_list = [x for x in first.iter()]
        second_list = [x for x in second.iter()]
        if len(first_list) != len(second_list):
            raise self.failureException('element trees are different sizes')
        for i in range(len(first_list)):
            if first_list[i].tag != second_list[i].tag:
                raise self.failureException('Tags are not equal')
            first_keys = [x for x in first_list[i].keys()]
            second_keys = [x for x in second_list[i].keys()]
            six.assertCountEqual(self, first_keys, second_keys)
            for key in first_keys:
                if key == lyns.VERSION:
                    assert first_list[i].get(key) is not None and second_list[i].get(key) is not None
                else:
                    assert first_list[i].get(key) == second_list[i].get(key)

    def setUp(self):
        '''
        Make an empty Document on "self.document" with a temporary directory. The repository
        directory's name is stored in "self.repo_dir." There should already be an "all_files.mei"
        file, in accordance with how Document.__init__() works.
        '''
        self.addTypeEqualityFunc(etree._Element, self.assertElementsEqual)
        self.addTypeEqualityFunc(etree._ElementTree, self.assertElementsEqual)
        self._session = session.InteractiveSession()
        self.repo_dir = self._session.set_repo_dir('')
        self.doc = self._session.get_document()

    def tearDown(self):
        '''
        In Python before 3.2, we need to clean up the temporary directory ourselves.
        '''
        self._session.unset_repo_dir()


class TestSmallThings(DocumentTestCase):
    '''
    Tests for small helper functions that require few tests:
    - :func:`_check_xmlid_chars`
    - :meth:`_set_default`
    '''

    def setUp(self):
        '''
        Make a temporary directory.
        '''
        # self.addTypeEqualityFunc(etree._Element, self.assertElementsEqual)
        # self.addTypeEqualityFunc(etree._ElementTree, self.assertElementsEqual)
        DocumentTestCase.setUp(self)
        try:
            # Python 3.2+
            self._temp_dir = tempfile.TemporaryDirectory()
            self.repo_dir = self._temp_dir.name
        except AttributeError:
            # Python Boring
            self._temp_dir = None
            self.repo_dir = tempfile.mkdtemp()

    def tearDown(self):
        '''
        Clean up the temporary directory.
        '''
        if self._temp_dir is None:
            shutil.rmtree(self.repo_dir)

        DocumentTestCase.tearDown(self)

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
        self.assertEqual(12, document._set_default({'a': 12}, 'a', 42))

    def test__make_empty_all_files_1(self):
        '''
        That _make_empty_all_files() works when a pathname is given.
        '''
        # 1.) get a temporary file
        test_path = os.path.join(self.repo_dir, 'test_all_files.mei')
        expected_path = os.path.join(os.path.dirname(inspect.getfile(self.__class__)),
                                     'exp_all_files_1a.mei')
        expected = etree.parse(expected_path)
        # 2.) run the function
        actual = document._make_empty_all_files(test_path)
        # 3.) ensure the returned "actual" document is proper
        self.assertEqual(expected, actual)
        # 4.) ensure the saved document is also proper
        actual_file = etree.parse(test_path)
        self.assertEqual(expected, actual_file)

    def test__make_empty_all_files_2(self):
        '''
        That _make_empty_all_files() works when the pathname is "None."
        '''
        # 1.) get a temporary file
        test_path = None
        expected_path = os.path.join(os.path.dirname(inspect.getfile(self.__class__)),
                                     'exp_all_files_1b.mei')
        expected = etree.parse(expected_path)
        # 2.) run the function
        actual = document._make_empty_all_files(test_path)
        # 3.) ensure the returned "actual" document is proper
        self.assertEqual(expected, actual)
        # 4.) ensure the saved document is also proper
        self.assertFalse(os.path.exists('None'))

    def test__make_ptr(self):
        '''
        That _make_ptr() works.
        '''
        targettype = 'silly'
        target = 'bullseye'
        actual = document._make_ptr(targettype, target)
        self.assertEqual(mei.PTR, actual.tag)
        self.assertEqual(targettype, actual.get('targettype'))
        self.assertEqual(target, actual.get('target'))
        self.assertEqual('onRequest', actual.get(xlink.ACTUATE))
        self.assertEqual('embed', actual.get(xlink.SHOW))

    def test__make_empty_head(self):
        '''
        Thankfully, complicated though it is, _make_empty_head() only has one possible output!
        '''
        expected = etree.fromstring('''
        <mei:meiHead xmlns:mei="http://www.music-encoding.org/ns/mei">
            <mei:fileDesc>
                <mei:titleStmt>
                    <mei:title>
                        <mei:title type="main">(Untitled)</mei:title>
                    </mei:title>
                </mei:titleStmt>
                <mei:pubStmt>
                    <mei:unpub>This is an unpublished Lychee-MEI document.</mei:unpub>
                </mei:pubStmt>
            </mei:fileDesc>
        </mei:meiHead>
        ''')
        self.assertEqual(expected, document._make_empty_head())

    def test__load_score_order_1(self):
        '''
        - check that "all_files" contains a "score" <ptr> (if not, return empty list)
        '''
        # NOTE: the first arg must be None, because that's what Document.__init__() will give when
        #       the repository path is missing
        assert [] == document._load_score_order(None, document._make_empty_all_files(None))

    def test__load_score_order_2(self):
        '''
        - check the <ptr>s have @target that ends with ".mei" (if not raise InvalidFileError)
        '''
        # this automatically inserts the path to the test file
        all_files = etree.fromstring('''
        <mei:meiCorpus xmlns:mei="http://www.music-encoding.org/ns/mei" xmlns:xlink="http://www.w3.org/1999/xlink">
            <mei:mei>
                <mei:ptr target="{}" targettype="score" xlink:actuate="onRequest" xlink:show="embed"/>
            </mei:mei>
        </mei:meiCorpus>
        '''.format('bad_score.mei'))

        with self.assertRaises(exceptions.InvalidFileError) as ife:
            document._load_score_order(os.path.split(__file__)[0], all_files)

        assert document._ERR_MISSING_FILE == ife.exception.args[0]

    def test__load_score_order_3(self):
        '''
        - check that all the <ptr>s' @target attributes are returned properly
        '''
        expected = ['1', '2', '1']
        # this automatically inserts the path to the test file
        all_files = etree.fromstring('''
        <mei:meiCorpus xmlns:mei="http://www.music-encoding.org/ns/mei" xmlns:xlink="http://www.w3.org/1999/xlink">
            <mei:mei>
                <mei:ptr target="{}" targettype="score" xlink:actuate="onRequest" xlink:show="embed"/>
            </mei:mei>
        </mei:meiCorpus>
        '''.format('exp_score_1.mei'))

        actual = document._load_score_order(os.path.split(__file__)[0], all_files)

        assert expected == actual

    def test__seven_digits(self):
        '''
        _seven_digits()
        '''
        # Statistically, ten percent of the initial strings should begin with a zero. Given that,
        # calling _seven_digits() 100 times gives us a pretty good chance of hitting that case at
        # least once.
        for _ in range(100):
            actual = document._seven_digits()
            assert 7 == len(actual)
            assert not actual.startswith('0')
            assert int(actual)

    def test__check_valid_section_id_1(self):
        '''
        _check_valid_section_id() returns True when it's valid
        '''
        xmlid = 'Sme-s-m-l-e1234567'
        expected = True
        actual = document._check_valid_section_id(xmlid)
        assert expected == actual

    def test__check_valid_section_id_2(self):
        '''
        _check_valid_section_id() returns False when xmlid doesn't start with the right thing.
        '''
        xmlid = 'S!!-s-m-l-e1234567'
        expected = False
        actual = document._check_valid_section_id(xmlid)
        assert expected == actual

    def test__check_valid_section_id_3(self):
        '''
        _check_valid_section_id() returns False when the "e part" has too many digits
        '''
        xmlid = 'Sme-s-m-l-e123456789'
        expected = False
        actual = document._check_valid_section_id(xmlid)
        assert expected == actual

    def test__check_valid_section_id_4(self):
        '''
        _check_valid_section_id() returns False when the "e part" is less than 1 million
        '''
        xmlid = 'Sme-s-m-l-e0012345'
        expected = False
        actual = document._check_valid_section_id(xmlid)
        assert expected == actual

    def test__check_valid_section_id_5(self):
        '''
        _check_valid_section_id() returns False when the "e part" isn't an integer
        '''
        xmlid = 'Sme-s-m-l-e123gg67'
        expected = False
        actual = document._check_valid_section_id(xmlid)
        assert expected == actual


class TestCheckVersionAttr(unittest.TestCase):
    "Tests for document._check_version_attr()."

    @mock.patch('lychee.log')
    def test_check_version_1(self, mock_log):
        '''
        version is missing
        '''
        lmei = etree.ElementTree(etree.Element(mei.SECTION))
        actual = document._check_version_attr(lmei)
        assert actual is lmei
        mock_log.assert_called_with(document._LY_VERSION_MISSING, 'error')

    @mock.patch('lychee.log')
    def test_check_version_2(self, mock_log):
        '''
        the version has only two numbers
        '''
        lmei = etree.ElementTree(etree.Element(mei.SECTION, {lyns.VERSION: '4.6'}))
        actual = document._check_version_attr(lmei)
        assert actual is lmei
        mock_log.assert_called_with(document._LY_VERSION_INVALID, 'error')

    @mock.patch('lychee.log')
    def test_check_version_3(self, mock_log):
        '''
        the version contains letters
        '''
        lmei = etree.ElementTree(etree.Element(mei.SECTION, {lyns.VERSION: '9.2.3a'}))
        actual = document._check_version_attr(lmei)
        assert actual is lmei
        mock_log.assert_called_with(document._LY_VERSION_INVALID, 'error')

    @mock.patch('lychee.log')
    def test_check_version_4(self, mock_log):
        '''
        the version is different than the version of this Lychee
        '''
        lmei = etree.ElementTree(etree.Element(mei.SECTION, {lyns.VERSION: '0.2.1'}))
        actual = document._check_version_attr(lmei)
        assert actual is lmei
        mock_log.assert_called_with(document._LY_VERSION_MISMATCH, 'warning')

    @mock.patch('lychee.log')
    def test_check_version_5(self, mock_log):
        '''
        the version is correct
        '''
        lmei = etree.ElementTree(etree.Element(mei.SECTION, {lyns.VERSION: lychee.__version__}))
        actual = document._check_version_attr(lmei)
        assert actual is lmei
        assert mock_log.call_count == 0



class TestSaveAndLoad(DocumentTestCase):
    '''
    Tests for document._save_out() and document._load_in().
    '''


    def setUp(self):
        '''
        Make a temporary directory.
        '''
        DocumentTestCase.setUp(self)
        self.path_to_here = os.path.dirname(inspect.getfile(self.__class__))
        # self.addTypeEqualityFunc(etree._Element, DocumentTestCase.assertElementsEqual)
        # self.addTypeEqualityFunc(etree._ElementTree, DocumentTestCase.assertElementsEqual)
        try:
            # Python 3.2+
            self._temp_dir = tempfile.TemporaryDirectory()
            self.repo_dir = self._temp_dir.name
        except AttributeError:
            # Python Boring
            self._temp_dir = None
            self.repo_dir = tempfile.mkdtemp()

    def tearDown(self):
        '''
        Clean up the temporary directory.
        '''
        if self._temp_dir is None:
            shutil.rmtree(self.repo_dir)

        DocumentTestCase.tearDown(self)

    def test__save_out_1(self):
        '''
        Given an Element without @ly:version, save it as an ElementTree with @ly:version.
        '''
        elem = etree.Element('something')
        to_here = os.path.join(self.repo_dir, 'something.mei')
        document._save_out(elem, to_here)
        self.assertTrue(os.path.exists(to_here))
        # escape the 'lxml' echo chamber
        with open(to_here, 'r') as the_file:
            saved = the_file.read()
        assert '<?xml' in saved
        assert 'UTF-8' in saved
        assert 'ly:version="{0}"'.format(lychee.__version__) in saved

    def test__save_out_2(self):
        '''
        Given an ElementTree with outdated @ly:version, save it with updated @ly:version.
        '''
        elem = etree.ElementTree(etree.Element('something', {lyns.VERSION: '0.0.1'}))
        to_here = os.path.join(self.repo_dir, 'something.mei')
        document._save_out(elem, to_here)
        self.assertTrue(os.path.exists(to_here))
        # escape the 'lxml' echo chamber
        with open(to_here, 'r') as the_file:
            saved = the_file.read()
        assert '<?xml' in saved
        assert 'UTF-8' in saved
        assert 'ly:version="{0}"'.format(lychee.__version__) in saved

    def test__save_out_3(self):
        '''
        Given an ElementTree, it tries to save but gets IOError, so raises CannotSaveError.
        '''
        tree = mock.MagicMock(spec_set=etree._ElementTree)
        tree.write.side_effect = IOError('lol')
        to_here = 'whatever.mei'
        with pytest.raises(exceptions.CannotSaveError) as err:
            document._save_out(tree, to_here)
        assert document._SAVE_OUT_ERROR == err.value[0]

    @mock.patch('lychee.document.document._check_version_attr')
    @mock.patch('lxml.etree.XMLParser')
    @mock.patch('lxml.etree.parse')
    def test__load_in_1(self, mock_parse, mock_parser_class, mock_check):
        '''
        Pathname is invalid; raises FileNotFoundError. (Mocked lxml and _check_version_attr()).
        '''
        from_here = 'something'
        recover = False
        exp_message = document._ERR_MISSING_FILE
        mock_parser = 'a parser'
        mock_parser_class.return_value = mock_parser
        if six.PY2:
            mock_parse.side_effect = IOError
        else:
            mock_parse.side_effect = OSError

        with self.assertRaises(exceptions.FileNotFoundError) as fnfe:
            document._load_in(from_here, recover)
        self.assertEqual(exp_message, fnfe.exception.args[0])
        mock_parse.assert_called_with(from_here, mock_parser)
        mock_parser_class.assert_called_with(recover=False)
        assert mock_check.call_count == 0

    @mock.patch('lychee.document.document._check_version_attr')
    @mock.patch('lxml.etree.XMLParser')
    @mock.patch('lxml.etree.parse')
    def test__load_in_2(self, mock_parse, mock_parser_class, mock_check):
        '''
        File can't be parsed by "lxml"; raises InvalidFileError. (Mocked lxml and _check_version_attr()).
        '''
        from_here = 'something'
        recover = False
        mock_parser = 'a parser'
        mock_parser_class.return_value = mock_parser
        mock_parse.side_effect = etree.XMLSyntaxError('shmooba', 2, 3, 4)

        with self.assertRaises(exceptions.InvalidFileError) as ife:
            document._load_in(from_here, recover)
        self.assertEqual('shmooba', ife.exception.args[0])
        mock_parse.assert_called_with(from_here, mock_parser)
        mock_parser_class.assert_called_with(recover=False)
        assert mock_check.call_count == 0

    @mock.patch('lychee.document.document._check_version_attr')
    @mock.patch('lxml.etree.XMLParser')
    @mock.patch('lxml.etree.parse')
    def test__load_in_3(self, mock_parse, mock_parser_class, mock_check):
        '''
        File is loaded just fine. Returns the file. (Mocked lxml and _check_version_attr()).
        '''
        from_here = 'something'
        recover = True
        mock_parser = 'a parser'
        mock_parser_class.return_value = mock_parser
        mock_parse.return_value = 'parsed'
        expected = 'such an XML'
        mock_check.return_value = expected

        actual = document._load_in(from_here, recover)

        assert expected == actual
        mock_parse.assert_called_with(from_here, mock_parser)
        mock_parser_class.assert_called_with(recover=True)
        mock_check.assert_called_with('parsed')

    def test__load_in_1_int(self):
        '''
        Pathname is invalid; raises FileNotFoundError.
        '''
        from_here = os.path.join(self.path_to_here, '*blows nose*')
        recover = False
        exp_message = document._ERR_MISSING_FILE
        with self.assertRaises(exceptions.FileNotFoundError) as fnfe:
            document._load_in(from_here, recover)
        self.assertEqual(exp_message, fnfe.exception.args[0])

    def test__load_in_2_int(self):
        '''
        File can't be parsed by "lxml"; raises InvalidFileError.
        '''
        from_here = os.path.join(self.path_to_here, 'broken.xml')
        recover = False
        exp_message = 'Opening and ending tag mismatch'
        with self.assertRaises(exceptions.InvalidFileError) as ife:
            document._load_in(from_here, recover)
        self.assertTrue(ife.exception.args[0].startswith(exp_message))

    def test__load_in_3_int(self):
        '''
        File is loaded just fine. Returns the file.
        '''
        from_here = os.path.join(self.path_to_here, 'broken.xml')
        recover = True
        actual = document._load_in(from_here, recover)
        self.assertIsInstance(actual, etree._ElementTree)
        self.assertEqual('one', actual.getroot().tag)


class TestEnsureScoreOrder(unittest.TestCase):
    '''
    Tests for document._ensure_score_order().
    '''

    def test__ensure_score_order_1(self):
        '''
        When the sections are in the expected order.
        '''
        score = etree.Element(mei.SCORE)
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '123'}))
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '456'}))
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '789'}))
        order = ['123', '456', '789']
        self.assertTrue(document._ensure_score_order(score, order))

    def test__ensure_score_order_2(self):
        '''
        When "score" has more sections than "order" wants.
        '''
        score = etree.Element(mei.SCORE)
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '123'}))
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '456'}))
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '789'}))
        order = ['123', '789']
        self.assertFalse(document._ensure_score_order(score, order))

    def test__ensure_score_order_3(self):
        '''
        When "score" and "order" are in a different order.
        '''
        score = etree.Element(mei.SCORE)
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '123'}))
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '456'}))
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '789'}))
        order = ['123', '789', '456']
        self.assertFalse(document._ensure_score_order(score, order))

    def test__ensure_score_order_4(self):
        '''
        When "score" has fewer sections than "order" wants.
        '''
        score = etree.Element(mei.SCORE)
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '123'}))
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '456'}))
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '789'}))
        order = ['123', '234', '456', '789']
        self.assertFalse(document._ensure_score_order(score, order))

    def test__ensure_score_order_5(self):
        '''
        When "order" has no elements.
        '''
        score = etree.Element(mei.SCORE)
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '123'}))
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '456'}))
        score.append(etree.Element(mei.SECTION, attrib={xml.ID: '789'}))
        order = []
        self.assertFalse(document._ensure_score_order(score, order))

    def test__ensure_score_order_6(self):
        '''
        When "score" has no child elements.
        '''
        score = etree.Element(mei.SCORE)
        order = ['123', '456', '789']
        self.assertFalse(document._ensure_score_order(score, order))


class TestDocumentInit(unittest.TestCase):
    '''
    Tests for document.Document.__init__().
    '''

    def setUp(self):
        '''
        Make a temporary directory.
        '''
        try:
            # Python 3.2+
            self._temp_dir = tempfile.TemporaryDirectory()
            self.repo_dir = self._temp_dir.name
        except AttributeError:
            # Python Boring
            self._temp_dir = None
            self.repo_dir = tempfile.mkdtemp()

    def tearDown(self):
        '''
        Clean up the temporary directory.
        '''
        if self._temp_dir is None:
            shutil.rmtree(self.repo_dir)

    def test_init_1(self):
        '''
        Repository already has an "all_files.mei" file. It's loaded properly. Instance variables are
        initialized as expected.
        '''
        all_files_path = os.path.join(self.repo_dir, 'all_files.mei')
        document._make_empty_all_files(all_files_path)

        with mock.patch('lychee.document.document._make_empty_all_files') as mock_meaf:
            doc = document.Document(self.repo_dir)

        self.assertEqual(0, mock_meaf.call_count)
        self.assertIsInstance(doc._all_files, etree._ElementTree)
        self.assertEqual({}, doc._sections)
        self.assertIsNone(doc._score)
        self.assertEqual([], doc._score_order)
        self.assertIsInstance(doc._head, etree._Element)

    @mock.patch('lychee.document.document.Document.get_head')
    @mock.patch('lychee.document.document._make_empty_all_files')
    def test_init_2(self, mock_meaf, mock_ghead):
        '''
        Repository is empty. _make_empty_all_files() is called to create a new "all_files.mei" file.
        Instance variables are initialized as expected.
        '''
        mock_meaf.return_value = etree.Element(mei.MEI_CORPUS)  # so _load_score_order() won't fail
        all_files_path = os.path.join(self.repo_dir, 'all_files.mei')
        mock_ghead.return_value = 5

        doc = document.Document(self.repo_dir)

        mock_meaf.assert_called_once_with(all_files_path)
        self.assertEqual(mock_meaf.return_value, doc._all_files)
        self.assertEqual({}, doc._sections)
        self.assertIsNone(doc._score)
        self.assertEqual([], doc._score_order)
        self.assertEqual(5, doc._head)

    @mock.patch('lychee.document.document.Document.get_head')
    @mock.patch('lychee.document.document._make_empty_all_files')
    def test_init_3(self, mock_meaf, mock_ghead):
        '''
        Repository is None. _make_empty_all_files() is called to create a new "all_files.mei" file.
        Instance variables are initialized as expected.
        '''
        mock_meaf.return_value = etree.Element(mei.MEI_CORPUS)  # so _load_score_order() won't fail
        mock_ghead.return_value = 5

        doc = document.Document(None)

        mock_meaf.assert_called_once_with(None)
        self.assertEqual(mock_meaf.return_value, doc._all_files)
        self.assertEqual({}, doc._sections)
        self.assertIsNone(doc._score)
        self.assertEqual([], doc._score_order)
        self.assertEqual(5, doc._head)

    @mock.patch('lychee.document.Document.save_everything')
    def test_with_1(self, mock_save):
        '''
        Ensure the context manager stuff works (no exception raised).
        '''
        with document.Document(self.repo_dir) as doc:
            self.assertIsInstance(doc, document.Document)
        mock_save.assert_called_once_with()

    @mock.patch('lychee.document.Document.save_everything')
    def test_with_2(self, mock_save):
        '''
        Ensure the context manager stuff works (no output directory, but the error from
        save_everything() is suppressed).
        '''
        mock_save.side_effect = exceptions.CannotSaveError
        with document.Document() as doc:
            self.assertIsInstance(doc, document.Document)
        self.assertEqual(0, mock_save.call_count)

    @mock.patch('lychee.document.Document.save_everything')
    def test_with_3(self, mock_save):
        '''
        Ensure the context manager stuff works (arbitrary exception raised).
        '''
        with self.assertRaises(RuntimeError):
            with document.Document(self.repo_dir) as doc:
                self.assertIsInstance(doc, document.Document)
                raise RuntimeError('asdf')
        self.assertEqual(0, mock_save.call_count)


class TestGetSectionIds(DocumentTestCase):
    '''
    Tests for Document.get_section_ids().
    '''

    def test_get_section_ids_1(self):
        '''
        "all_sections" is False; list is empty
        '''
        self.doc._score_order = []
        expected = []
        all_sections = False
        actual = self.doc.get_section_ids(all_sections)
        self.assertEqual(expected, actual)

    def test_get_section_ids_2(self):
        '''
        "all_sections" is False; there's stuff
        '''
        self.doc._score_order = ['1', '2', '3']
        expected = ['1', '2', '3']
        all_sections = False
        actual = self.doc.get_section_ids(all_sections)
        self.assertEqual(expected, actual)

    def test_get_section_ids_3(self):
        '''
        "all_sections" is True; dict is empty
        '''
        self.doc._sections = {}
        expected = []
        all_sections = True
        actual = self.doc.get_section_ids(all_sections)
        self.assertEqual(expected, actual)

    def test_get_section_ids_4(self):
        '''
        "all_sections" is True; dict has stuff
        '''
        self.doc._sections = {'1': 1, '2': 2, '3': 3}
        expected = ['1', '2', '3']
        all_sections = True
        actual = self.doc.get_section_ids(all_sections)
        six.assertCountEqual(self, expected, actual)


class TestGetPutHead(DocumentTestCase):
    '''
    Tests for Document.get_head() and Document.put_head().
    '''

    def test_get_1(self):
        '''
        Preconditions:
        - self._head has an Element
        Postconditions:
        - it's returned
        '''
        mei_head = etree.Element(mei.MEI_HEAD)
        self.doc._head = mei_head
        self.assertTrue(mei_head is self.doc.get_head())

    def test_get_2(self):
        '''
        Preconditions:
        - self._head missing
        - self._all_files has no <meiHead>
        Postconditions:
        - method raises exception
        '''
        self.doc._all_files = etree.Element(mei.MEI_CORPUS)
        self.doc._head = None
        with self.assertRaises(exceptions.HeaderNotFoundError) as hnferr:
            self.doc.get_head()
        self.assertEqual(document._ERR_MISSING_MEIHEAD, hnferr.exception.args[0])

    def test_get_3(self):
        '''
        Preconditions:
        - self._head missing
        - _all_files has <meiHead> without <ptr>
        Postconditions:
        - the <meiHead> is cached
        - the <meiHead> is returned
        '''
        exp_mei_head = self.doc._all_files.find('./{}'.format(mei.MEI_HEAD))
        actual = self.doc.get_head()
        self.assertTrue(exp_mei_head is actual)
        self.assertTrue(exp_mei_head is self.doc._head)

    def test_get_4(self):
        '''
        Preconditions:
        - self._head missing
        - _all_files has <meiHead> with <ptr>
        - try to load the file and it works
        Postconditions:
        - the <meiHead> is cached
        - the <meiHead> is returned
        '''
        self.doc._head = None
        # @ident is a marker to ensure Document.get_head() loads from the file
        mei_head = etree.Element(mei.MEI_HEAD, attrib={'ident': '42'})
        mei_head = etree.ElementTree(mei_head)
        head_pathname = os.path.join(self.repo_dir, 'meiHead.mei')
        mei_head.write_c14n(head_pathname, exclusive=False, inclusive_ns_prefixes=['mei'])
        doc_mei_head = self.doc._all_files.find('./{}'.format(mei.MEI_HEAD))
        doc_mei_head.append(etree.Element(mei.PTR,
                                          attrib={'targettype': 'head', 'target': head_pathname}))
        actual = self.doc.get_head()
        self.assertIsInstance(actual, etree._Element)
        self.assertEqual('42', actual.get('ident'))

    def test_get_5(self):
        '''
        Preconditions:
        - self._head missing
        - _all_files has <meiHead> with <ptr>
        - try to load the file but it doesn't exist
        Postconditions:
        - method raises exception
        '''
        self.doc._head = None
        exp_mei_head = self.doc._all_files.find('./{}'.format(mei.MEI_HEAD))
        exp_mei_head.append(etree.Element(mei.PTR,
                                          attrib={'targettype': 'head', 'target': 'noexista.mei'}))
        with self.assertRaises(exceptions.HeaderNotFoundError) as hnferr:
            self.doc.get_head()
        self.assertEqual(document._ERR_MISSING_MEIHEAD, hnferr.exception.args[0])

    def test_get_6(self):
        '''
        Preconditions:
        - self._head missing
        - _all_files has <meiHead> with <ptr>
        - try to load the file but it's corrupt
        Postconditions:
        - method raises exception
        '''
        # copy the corrupt file into the repository, where get_head() expects to find it
        filename = 'corrupt_meiHead.mei'
        shutil.copyfile(os.path.join(os.path.split(__file__)[0], filename),
                        os.path.join(self.repo_dir, filename))
        self.doc._head = None
        #
        exp_mei_head = self.doc._all_files.find('./{}'.format(mei.MEI_HEAD))
        exp_mei_head.append(etree.Element(mei.PTR,
                                          attrib={'targettype': 'head', 'target': filename}))
        with self.assertRaises(exceptions.HeaderNotFoundError) as hnferr:
            self.doc.get_head()
        self.assertEqual(document._ERR_CORRUPT_MEIHEAD, hnferr.exception.args[0])

    def test_put_1(self):
        '''
        - self._repo_path is None
        ----
        - <meiHead> is cached
        '''
        # we have to make a new Document for this test so that _repo_path is None
        doc = document.Document()
        mei_head = etree.Element(mei.MEI_HEAD)
        doc.put_head(mei_head)
        self.assertTrue(mei_head is doc._head)

    def test_put_2(self):
        '''
        - self._repo_path is something
        - self._all_files <meiHead> has a <ptr>
        ----
        - <meiHead> is cached
        '''
        old_head = self.doc._all_files.find('.//{}'.format(mei.MEI_HEAD))
        old_head.append(etree.Element(mei.PTR, attrib={'targettype': 'head'}))
        new_head = etree.Element(mei.MEI_HEAD)
        self.doc.put_head(new_head)
        self.assertTrue(new_head is self.doc._head)

    def test_put_3(self):
        '''
        - self._repo_path is something
        - self._all_files <meiHead> is empty
        ----
        - <ptr> is added to <meiHead>
        - <meiHead> is cached
        '''
        new_head = etree.Element(mei.MEI_HEAD)
        self.doc.put_head(new_head)
        self.assertTrue(new_head is self.doc._head)
        self.assertIsNotNone(self.doc._all_files.find('.//{}'.format(mei.MEI_HEAD)))


class TestGetPutSection(DocumentTestCase):
    '''
    Tests for Document.get_section() and Document.put_section().
    '''

    def test_get_1(self):
        '''
        When the provided "id" starts wth an octothorpe, it should be removed.
        '''
        self.doc._sections['123'] = 'some section'
        self.assertEqual('some section', self.doc.get_section('#123'))

    def test_get_2(self):
        '''
        When the "id" doesn't start with an octothorpe, it shouldn't be removed.
        '''
        self.doc._sections['123'] = 'some section'
        self.assertEqual('some section', self.doc.get_section('123'))

    @mock.patch('lychee.document.document._load_in')
    def test_get_3(self, mock_load_in):
        '''
        When the "id" doesn't exist, see if calling self.load_everything() will load the section.
        In this case, it does.
        '''
        section_id = '888'
        expected = 'some section'
        the_section = mock.Mock()
        the_section.getroot = mock.Mock(return_value=expected)
        mock_load_in.return_value = the_section

        actual = self.doc.get_section(section_id)

        assert expected is actual
        mock_load_in.assert_called_with(os.path.join(self.repo_dir, '888.mei'))

    @mock.patch('lychee.document.document._load_in')
    def test_get_4(self, mock_load_in):
        '''
        When the "id" doesn't exist, see if calling self.load_everything() will load the section.
        In this case, the file doesn't exist.
        '''
        section_id = '888'
        mock_load_in.side_effect = exceptions.FileNotFoundError

        with self.assertRaises(exceptions.SectionNotFoundError) as exc:
            self.doc.get_section(section_id)
        self.assertEqual(document._SECTION_NOT_FOUND.format(xmlid=section_id), exc.exception.args[0])
        mock_load_in.assert_called_with(os.path.join(self.repo_dir, '888.mei'))

    @mock.patch('lychee.document.document._load_in')
    def test_get_5(self, mock_load_in):
        '''
        When the "id" doesn't exist, see if calling self.load_everything() will load the section.
        In this case, the file is invalid.
        '''
        section_id = '888'
        mock_load_in.side_effect = exceptions.InvalidFileError('whatever')

        with self.assertRaises(exceptions.InvalidFileError) as exc:
            self.doc.get_section(section_id)
        self.assertEqual('whatever', exc.exception.args[0])
        mock_load_in.assert_called_with(os.path.join(self.repo_dir, '888.mei'))

    @mock.patch('lychee.document.document._load_in')
    def test_get_6(self, mock_load_in):
        '''
        When the "id" doesn't exist, see if calling self.load_everything() will load the section.
        In this case, the section doesn't exist, and there is no "repo_dir" configured.
        '''
        section_id = '888'

        doc = document.Document()
        with self.assertRaises(exceptions.SectionNotFoundError) as exc:
            doc.get_section(section_id)
        self.assertEqual(document._SECTION_NOT_FOUND.format(xmlid=section_id), exc.exception.args[0])
        self.assertEqual(0, mock_load_in.call_count)

    @mock.patch('lychee.document.document._load_in')
    def test_get_7(self, mock_load_in):
        '''
        When the "id" is in self._sections but it's None, call self.load_everything().
        '''
        section_id = '888'
        expected = 'some section'
        the_section = mock.Mock()
        the_section.getroot = mock.Mock(return_value=expected)
        mock_load_in.return_value = the_section
        self.doc._sections = {section_id: None}

        actual = self.doc.get_section(section_id)

        assert expected is actual

    @mock.patch('lychee.document.document._load_in')
    def test_get_8(self, mock_load_in):
        '''
        When the "id" is in self._sections and it's not None, return that.
        '''
        section_id = '888'
        expected = 'Fulbright'
        self.doc._sections = {section_id: expected}

        actual = self.doc.get_section(section_id)

        assert expected == actual
        assert 0 == mock_load_in.call_count

    def test_put_1(self):
        '''
        When there's already an @xml:id, it's used just fine.
        '''
        xmlid = 'Sme-s-m-l-e8888888'
        section = etree.Element(mei.SECTION, attrib={xml.ID: xmlid})
        actual = self.doc.put_section(section)
        self.assertEqual(xmlid, actual)
        self.assertEqual(xmlid, self.doc._sections[xmlid].get(xml.ID))

    def test_put_2(self):
        '''
        When there isn't an @xml:id, a new one is created.
        '''
        # use the @marker attribute to ensure it's the same <section>
        section = etree.Element(mei.SECTION, attrib={'marker': 'crayon'})

        actual = self.doc.put_section(section)

        assert 'crayon' == self.doc._sections[actual].get('marker')
        assert document._check_valid_section_id(actual)

    def test_put_3(self):
        '''
        When there's already an @xml:id, but it's invalid, a new one is created
        '''
        # use the @marker attribute to ensure it's the same <section>
        section = etree.Element(mei.SECTION, attrib={xml.ID: '888', 'marker': 'crayon'})

        actual = self.doc.put_section(section)

        assert 'crayon' == self.doc._sections[actual].get('marker')
        assert document._check_valid_section_id(actual)


class TestGetPutScore(DocumentTestCase):
    '''
    Tests for Document.get_score() and Document.put_score().
    '''

    def test_put_1(self):
        '''
        When the <score> has no <section> elements.
        '''
        the_score = etree.Element(mei.SCORE)
        expected = []
        actual = self.doc.put_score(the_score)
        self.assertEqual(expected, actual)
        self.assertEqual(0, len(self.doc._score_order))
        self.assertEqual(0, len(self.doc._sections))

    def test_put_2(self):
        '''
        When the <score> has three <section> elements.
        '''
        section_tag = mei.SECTION
        the_score = etree.Element(mei.SCORE)
        the_score.append(etree.Element(section_tag, attrib={xml.ID: 'Sme-s-m-l-e1234567'}))
        the_score.append(etree.Element(section_tag, attrib={xml.ID: 'Sme-s-m-l-e2345678'}))
        the_score.append(etree.Element(section_tag, attrib={xml.ID: 'Sme-s-m-l-e3456789'}))
        exp_xmlids = ['Sme-s-m-l-e1234567', 'Sme-s-m-l-e2345678', 'Sme-s-m-l-e3456789']

        actual = self.doc.put_score(the_score)

        self.assertEqual(exp_xmlids, actual)
        self.assertEqual(exp_xmlids, self.doc._score_order)
        self.assertEqual(3, len(self.doc._sections))
        for xmlid in exp_xmlids:
            self.assertEqual(section_tag, self.doc._sections[xmlid].tag)
            self.assertEqual(xmlid, self.doc._sections[xmlid].get(xml.ID))

    @mock.patch('lychee.document.document._ensure_score_order')
    @mock.patch('lychee.document.Document.get_section')
    def test_get_1(self, mock_get_section, mock_score_order):
        '''
        When self._score is something, and _ensure_score_order() says it's good.
        '''
        the_score = mock.MagicMock()
        the_order = [1, 2, 3]
        self.doc._score = the_score
        self.doc._score_order = the_order
        mock_score_order.return_value = True
        expected = the_score

        actual = self.doc.get_score()

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
        mock_get_section.side_effect = lambda x: etree.Element(x)  # pylint: disable=unnecessary-lambda
        the_score = mock.MagicMock()
        the_order = ['one', 'two', 'three']
        self.doc._score = the_score
        self.doc._score_order = the_order
        mock_score_order.return_value = False

        actual = self.doc.get_score()

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
        the_score = mock.MagicMock()
        the_order = ['one', 'two', 'three']
        self.doc._score = the_score
        self.doc._score_order = the_order
        mock_score_order.return_value = False

        with self.assertRaises(exceptions.SectionNotFoundError):
            self.doc.get_score()

        mock_score_order.assert_called_once_with(the_score, the_order)
        mock_get_section.assert_called_once_with('one')


class TestSaveLoadEverything(DocumentTestCase):
    '''
    Tests for Document.save_everything() and Document.load_everything().
    '''

    def setUp(self):
        '''
        Add a "path_to_here" property that holds the directory this file is in.
        '''
        DocumentTestCase.setUp(self)
        self.path_to_here = os.path.dirname(inspect.getfile(self.__class__))

    def load_n_compare(self, this, that):
        '''
        Do an "assertEqual" on two Element objects. "This" should be the filename of an MEI/XML
        file that contains the expected result, relative to the directory of this file. "That"
        should be the absolute path to the outputted result to compare.
        '''
        that = etree.parse(that)
        this = etree.parse(os.path.join(self.path_to_here, this))
        self.assertEqual(this, that)

    def test_save_template_nomock(self, **kwargs):
        '''
        This is a template test with default values. This test should run by itself, but it may
        also be used for targeted testing of the other functionality in
        :meth:`Document.save_everything`. Unit tests should use :meth:`test_save_template`; this
        method is intended for integration tests, since :func:`_write_out` is not mocked here.
        Use the following keyword arguments to adjust pre- and post-conditions:

        :kwarg head: The value to assign to :attr:`Document._head` before the test.
        :type head: :class:`lxml.etree.Element`
        :kwarg score_order: The value to assign to :attr:`Document._score_order` before the test.
        :type score_order: list of str
        :kwarg sections: The value to assign to :attr:`Document._sections` before the test.
        :type sections: dict of str to :class:`Element`
        :kwarg expected: Expected return value of :meth:`save_everything`.
        :type expected: list of str
        :returns: The return value of the function-under-test.
        :rtype: list of str

        .. note:: This test method automatically prepends the ``repository_pathname`` to the
            pathnames expected in ``expected``.

        .. note:: You should be using this test method when you want to check the validity of the
            files outputted by :func:`_write_out`. You must do this manually.

        Default Preconditions:
        - head is None
        - score_order is empty
        - sections is empty
        Default Postconditions:
        - expected is ``['all_files.mei']``
        '''

        # 1.) prepare the preconditions parameters
        head = kwargs.get('head', None)
        score_order = kwargs.get('score_order', [])
        sections = kwargs.get('sections', {})
        # prepend the full path to the "expected" return values
        expected = kwargs.get('expected', ['all_files.mei'])
        expected = [os.path.join(self.repo_dir, x) for x in expected]

        # 2.) prepare the Document instance
        self.doc._head = head
        self.doc._score_order = score_order
        self.doc._sections = sections

        # 3.) do the test
        actual = self.doc.save_everything()

        # 4.) assert the postconditions
        six.assertCountEqual(self, expected, actual)

        return actual

    @mock.patch('lychee.document.document._save_out')
    def test_save_template(self, mock_save_out, **kwargs):
        '''
        This is a modified version of :meth:`test_save_template_nomock` that adds a mock to
        :func:`_save_out` so that it may be tested.

        :kwarg save_out_calls: A list of 2-tuples representing the calls expected to
            :func:`_save_out`. The order of calls is not checked. You may use :const:`mock.ANY` for
            the frist argument if it's not important which object is submitted. The second argument,
            being an absolute pathname determined in part at runtime (by the ``repository_pathname``)
            is modified in this method to incorporate the full path. The default value is this:
            ``[(<something>, 'all_files.mei')]``, and this argument is added automatically by this
            test method.
        :type save_out_calls: list of :class:`mock.call`

        .. note:: This test method does *not* check the validity of any files outputted. In fact,
            because _write_out() is mocked, you cannot check that with this test method. Use
            :meth:`test_save_template_nomock` for that.

        Default Preconditions:
        - (no difference)
        Default Postconditions:
        - save_out_calls has one call: ``call('')``
        '''

        save_out_calls = [] if 'save_out_calls' not in kwargs else kwargs['save_out_calls']
        save_out_calls = [(x[0], os.path.join(self.repo_dir, x[1])) for x in save_out_calls]
        save_out_calls.append((mock.ANY, os.path.join(self.repo_dir, 'all_files.mei')))

        actual = self.test_save_template_nomock(**kwargs)

        self.assertEqual(len(save_out_calls), mock_save_out.call_count)
        for each_call in save_out_calls:
            mock_save_out.assert_any_call(each_call[0], each_call[1])

        return actual

    def test_save_1(self):
        '''
        Preconditions:
        - self._repo_path is None
        Postconditions:
        - raises CannotSaveError

        .. note:: This test doesn't use the template.
        '''
        doc = document.Document(repository_path=None)
        with self.assertRaises(exceptions.CannotSaveError) as cse:
            doc.save_everything()
        self.assertEqual(cse.exception.args[0], document._ERR_MISSING_REPO_PATH)

    def test_save_2(self):
        '''
        Integration version of test_save_template() that tests proper structure of "all_files.mei".
        '''
        files = self.test_save_template_nomock()
        self.load_n_compare('exp_all_files_6.mei', files[0])

    def test_save_3a(self):
        '''
        Preconditions:
        - self._head is something
        Postconditions:
        - _save_out() is called with "head.mei"
        - "head.mei" is in returned stuff
        '''
        self.test_save_template(head=12,
                                expected=['all_files.mei', 'head.mei'],
                                save_out_calls=[(12, 'head.mei')])

    def test_save_3b(self):
        '''
        Integration test for test_save_3a().
        '''
        saved_out = ['all_files.mei', 'head.mei']
        head = etree.parse(os.path.join(self.path_to_here, 'input_meiHead.mei'))
        files = self.test_save_template_nomock(head=head, expected=saved_out)
        listdir = os.listdir(os.path.dirname(files[0]))
        six.assertCountEqual(self, saved_out, listdir)
        for each_file in files:
            if each_file.endswith('all_files.mei'):
                self.load_n_compare('exp_all_files_2.mei', each_file)
            elif each_file.endswith('head.mei'):
                self.load_n_compare('input_meiHead.mei', each_file)

    def test_save_4a(self):
        '''
        Preconditions:
        - there are three contained <section> elements
        - _score_order is empty
        Postconditions:
        - _save_out() called with each <section>
        - each section's filename is returned
        '''
        self.test_save_template(sections={'1': 'section 1', '2': 'section 3', '3': 'section 3'},
                                expected=['1.mei', '2.mei', '3.mei', 'all_files.mei'],
                                save_out_calls=[(mock.ANY, '1.mei'), (mock.ANY, '2.mei'),
                                                (mock.ANY, '3.mei')])
    def test_save_4b(self):
        '''
        Integration test for test_save_4a().
        '''
        sections = {'1': etree.Element(mei.SECTION, attrib={xml.ID: '1'}),
                    '2': etree.Element(mei.SECTION, attrib={xml.ID: '2'}),
                    '3': etree.Element(mei.SECTION, attrib={xml.ID: '3'})
                   }
        saved_out = ['all_files.mei', '1.mei', '2.mei', '3.mei']
        files = self.test_save_template_nomock(sections=sections, expected=saved_out)
        listdir = os.listdir(os.path.dirname(files[0]))
        six.assertCountEqual(self, saved_out, listdir)
        for each_file in files:
            if each_file.endswith('all_files.mei'):
                self.load_n_compare('exp_all_files_3.mei', each_file)
            else:
                # TODO: find a way to not need creating an XMLParser with recover=True...
                #       the reason we need it now is that lxml otherwise fails to parse the
                #       @xml:id attribute that IT OUTPUTTED BY ITSELF ANYWAY and that's weird
                actual_section = etree.parse(each_file, etree.XMLParser(recover=True))
                if each_file.endswith('1.mei'):
                    self.assertEqual(sections['1'], actual_section.getroot())
                elif each_file.endswith('2.mei'):
                    self.assertEqual(sections['2'], actual_section.getroot())
                elif each_file.endswith('3.mei'):
                    self.assertEqual(sections['3'], actual_section.getroot())

    def test_save_5a(self):
        '''
        Preconditions:
        - there are three contained <section> elements
        - _score_order holds three elements, but the first and third are the same
        Postconditions:
        - _save_out() called with each <section>
        - _savo_out() called with "score.mei"
        - each section's filename is returned
        - "score.mei" is returned
        '''
        self.test_save_template(sections={'1': 'section 1', '2': 'section 3', '3': 'section 3'},
                                score_order=['1', '2', '1'],
                                expected=['1.mei', '2.mei', '3.mei', 'all_files.mei', 'score.mei'],
                                save_out_calls=[(mock.ANY, '1.mei'), (mock.ANY, '2.mei'),
                                                (mock.ANY, '3.mei'), (mock.ANY, 'score.mei')])

    def test_save_5b(self):
        '''
        Integration test for test_save_5a().
        '''
        sections = {'1': etree.Element(mei.SECTION, attrib={xml.ID: '1'}),
                    '2': etree.Element(mei.SECTION, attrib={xml.ID: '2'}),
                    '3': etree.Element(mei.SECTION, attrib={xml.ID: '3'})
                   }
        saved_out = ['all_files.mei', 'score.mei', '1.mei', '2.mei', '3.mei']
        files = self.test_save_template_nomock(sections=sections, score_order=['1', '2', '1'],
                                               expected=saved_out)
        listdir = os.listdir(os.path.dirname(files[0]))
        six.assertCountEqual(self, saved_out, listdir)
        for each_file in files:
            if each_file.endswith('all_files.mei'):
                self.load_n_compare('exp_all_files_4.mei', each_file)
            elif each_file.endswith('score.mei'):
                self.load_n_compare('exp_score_1.mei', each_file)
            else:
                # TODO: find a way to not need creating an XMLParser with recover=True...
                #       the reason we need it now is that lxml otherwise fails to parse the
                #       @xml:id attribute that IT OUTPUTTED BY ITSELF ANYWAY and that's weird
                actual_section = etree.parse(each_file, etree.XMLParser(recover=True))
                if each_file.endswith('1.mei'):
                    self.assertEqual(sections['1'], actual_section.getroot())
                elif each_file.endswith('2.mei'):
                    self.assertEqual(sections['2'], actual_section.getroot())
                elif each_file.endswith('3.mei'):
                    self.assertEqual(sections['3'], actual_section.getroot())

    def test_save_6a(self):
        '''
        Preconditions:
        - there are three contained <section> elements
        - _score_order holds three elements, but the first and third are the same
        - self._head is something
        Postconditions:
        - _save_out() called with "head.mei"
        - _save_out() called with each <section>
        - _savo_out() called with "score.mei"
        - each section's filename is returned
        - "score.mei" is returned
        - "head.mei" is returned
        '''
        self.test_save_template(sections={'1': 'section 1', '2': 'section 3', '3': 'section 3'},
                                head='something',
                                score_order=['1', '2', '1'],
                                expected=['1.mei', '2.mei', '3.mei', 'all_files.mei',
                                          'score.mei', 'head.mei'],
                                save_out_calls=[(mock.ANY, '1.mei'), (mock.ANY, '2.mei'),
                                                (mock.ANY, '3.mei'), (mock.ANY, 'score.mei'),
                                                (mock.ANY, 'head.mei')])

    def test_save_6b(self):
        '''
        Integration test for test_save_6a().
        '''
        head = etree.parse(os.path.join(self.path_to_here, 'input_meiHead.mei'))
        sections = {'1': etree.Element(mei.SECTION, attrib={xml.ID: '1'}),
                    '2': etree.Element(mei.SECTION, attrib={xml.ID: '2'}),
                    '3': etree.Element(mei.SECTION, attrib={xml.ID: '3'})
                   }
        saved_out = ['all_files.mei', 'head.mei', 'score.mei', '1.mei', '2.mei', '3.mei']
        files = self.test_save_template_nomock(sections=sections, score_order=['1', '2', '1'],
                                               head=head, expected=saved_out)
        listdir = os.listdir(os.path.dirname(files[0]))
        six.assertCountEqual(self, saved_out, listdir)
        for each_file in files:
            if each_file.endswith('all_files.mei'):
                self.load_n_compare('exp_all_files_5.mei', each_file)
            elif each_file.endswith('score.mei'):
                self.load_n_compare('exp_score_1.mei', each_file)
            elif each_file.endswith('head.mei'):
                self.load_n_compare('input_meiHead.mei', each_file)
            else:
                # TODO: find a way to not need creating an XMLParser with recover=True...
                #       the reason we need it now is that lxml otherwise fails to parse the
                #       @xml:id attribute that IT OUTPUTTED BY ITSELF ANYWAY and that's weird
                actual_section = etree.parse(each_file, etree.XMLParser(recover=True))
                if each_file.endswith('1.mei'):
                    self.assertEqual(sections['1'], actual_section.getroot())
                elif each_file.endswith('2.mei'):
                    self.assertEqual(sections['2'], actual_section.getroot())
                elif each_file.endswith('3.mei'):
                    self.assertEqual(sections['3'], actual_section.getroot())

    def test_save_7a(self):
        '''
        Preconditions:
        - there are three contained <section> elements
        - none of the <section>s were loaded
        - _score_order is empty
        Postconditions:
        - _save_out() not called with each <section>
        - each section's filename is returned
        '''
        self.test_save_template(sections={'1': None, '2': None, '3': None},
                                expected=['1.mei', '2.mei', '3.mei', 'all_files.mei'],
                                save_out_calls=[])


class TestGetFromPutInHead(DocumentTestCase):
    '''
    Tests for Document.get_from_head() and Document.put_in_head().
    '''

    def test_get_1(self):
        '''
        Try to "get" something that isn't approved for getting: it returns an empty list.
        '''
        what = 'facePlant'
        assert [] == self.doc.get_from_head(what)

    def test_get_2(self):
        '''
        Try to "get" something that is approved, but not in this <meiHead>: it returns an empty list.
        '''
        what = 'composer'
        assert [] == self.doc.get_from_head(what)

    def test_get_3(self):
        '''
        Try to "get" something that is approved and does exist: it returns that element in a list.
        '''
        # add a "composer" element in the right spot
        titleStmt = self.doc._head.find('.//{}'.format(mei.TITLE_STMT))
        titleStmt.append(etree.Element(mei.COMPOSER))

        what = 'composer'
        actual = self.doc.get_from_head(what)

        assert 1 == len(actual)
        actual = actual[0]
        assert isinstance(actual, etree._Element)
        assert mei.COMPOSER == actual.tag

    def test_get_4(self):
        '''
        Try to "get" the <title> element, which requires a different algorithm internally.
        '''
        what = 'title'
        actual = self.doc.get_from_head(what)

        assert 1 == len(actual)
        actual = actual[0]
        assert isinstance(actual, etree._Element)
        assert mei.TITLE == actual.tag
        actual = actual.find('./{}'.format(mei.TITLE))
        assert mei.TITLE == actual.tag
        assert 'main' == actual.get('type')
        assert document._PLACEHOLDER_TITLE == actual.text


class TestInitSectionsDict(object):
    '''
    Tests for the _init_sections_dict() helper function.
    '''

    def test_empty_doc(self):
        '''
        There are no <ptr targettype="section">.
        '''
        mei_elem = etree.Element(mei.MEI)
        root = etree.Element(mei.MEI_CORPUS)
        assert {} == document._init_sections_dict(root)

    def test_three_valid_sections(self):
        '''
        There are three valid <ptr targettype="section">.
        '''
        mei_elem = etree.Element(mei.MEI)
        mei_elem.append(etree.Element(mei.PTR, attrib={'targettype': 'section', 'target': 'asdf.mei'}))
        mei_elem.append(etree.Element(mei.PTR, attrib={'targettype': 'section', 'target': 'bsdf.mei'}))
        mei_elem.append(etree.Element(mei.PTR, attrib={'targettype': 'section', 'target': 'csdf.mei'}))
        expected = {'asdf': None, 'bsdf': None, 'csdf': None}
        root = etree.Element(mei.MEI_CORPUS)
        root.append(mei_elem)

        assert expected == document._init_sections_dict(root)

    def test_invalid_section(self):
        '''
        There is one valid and one invalid <ptr targettype="section">.
        '''
        mei_elem = etree.Element(mei.MEI)
        mei_elem.append(etree.Element(mei.PTR, attrib={'targettype': 'section', 'target': 'asdf.mei'}))
        mei_elem.append(etree.Element(mei.PTR, attrib={'targettype': 'section', 'target': 'bsdf'}))
        root = etree.Element(mei.MEI_CORPUS)
        root.append(mei_elem)

        with pytest.raises(exceptions.InvalidDocumentError) as err:
            document._init_sections_dict(root)
        assert err.value[0] == document._ERR_CORRUPT_TARGET.format('bsdf')


class TestMoveSectionTo(DocumentTestCase):
    '''
    Tests for Document.move_section_to().
    '''

    def test_section_missing(self):
        '''
        when the section to move is actually missing (SectionNotFoundError)
        '''
        xmlid = 'Sme-s-l-e11111'
        with pytest.raises(exceptions.SectionNotFoundError) as err:
            self.doc.move_section_to(xmlid, 14)
        assert err.value[0] == document._SECTION_NOT_FOUND.format(xmlid=xmlid)

    def test_not_yet_active(self):
        '''
        When the section is not in the active score.
        We'll test with 3 sections, and add them in a variety of ways.
        '''
        sect_ids = []
        for _ in range(3):
            sect_ids.append(self.doc.put_section(etree.Element(mei.SECTION)))

        self.doc.move_section_to(sect_ids[0], 0)
        self.doc.move_section_to(sect_ids[1], 40)
        self.doc.move_section_to(sect_ids[2], 1)

        assert self.doc.get_section_ids() == [sect_ids[0], sect_ids[2], sect_ids[1]]

    def test_move_later(self):
        '''
        When the section is in the score, moving to a later place.
        In this test, it amounts to swapping the first 2 of 3 sections.
        '''
        sect_ids = []
        for _ in range(3):
            sect_ids.append(self.doc.put_section(etree.Element(mei.SECTION)))
        score = etree.Element(mei.SCORE)
        for each_id in sect_ids:
            score.append(self.doc.get_section(each_id))
        self.doc.put_score(score)

        self.doc.move_section_to(sect_ids[0], 2)

        assert self.doc.get_section_ids() == [sect_ids[1], sect_ids[0], sect_ids[2]]

    def test_move_to_end(self):
        '''
        when the section is in the score, move it to the end
        '''
        sect_ids = []
        for _ in range(3):
            sect_ids.append(self.doc.put_section(etree.Element(mei.SECTION)))
        score = etree.Element(mei.SCORE)
        for each_id in sect_ids:
            score.append(self.doc.get_section(each_id))
        self.doc.put_score(score)

        self.doc.move_section_to(sect_ids[0], 3)

        assert self.doc.get_section_ids() == [sect_ids[1], sect_ids[2], sect_ids[0]]

    def test_move_earlier(self):
        '''
        when the section is in the score, moving to an earlier place
        '''
        sect_ids = []
        for _ in range(3):
            sect_ids.append(self.doc.put_section(etree.Element(mei.SECTION)))
        score = etree.Element(mei.SCORE)
        for each_id in sect_ids:
            score.append(self.doc.get_section(each_id))
        self.doc.put_score(score)

        self.doc.move_section_to(sect_ids[2], 0)

        assert self.doc.get_section_ids() == [sect_ids[2], sect_ids[0], sect_ids[1]]
