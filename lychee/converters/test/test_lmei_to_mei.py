#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/test/test_lmei_to_mei.py
# Purpose:                Tests for "lmei_to_mei.py" and "lmei_to_verovio.py"
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
Tests for "lmei_to_mei.py" and "lmei_to_verovio.py"
'''

from lxml import etree
import pytest

try:
    from unittest import mock
except ImportError:
    import mock

from lychee.converters import lmei_to_mei, lmei_to_verovio
from lychee.namespaces import mei
from lychee.signals import outbound


class TestToMei:

    def test_wrap_section_element(self):
        '''
        Ensure that wrap_section_element() returns the proper element hierarchy:

        <mei>
            <music>
                <body>
                    <mdiv>
                        <score>
                            <section>
        '''
        section = etree.Element(mei.SECTION)
        actual = lmei_to_mei.wrap_section_element(section)
        assert mei.MEI == actual.tag
        actual = actual.getchildren()[0]
        assert mei.MUSIC == actual.tag
        actual = actual.getchildren()[0]
        assert mei.BODY == actual.tag
        actual = actual.getchildren()[0]
        assert mei.MDIV == actual.tag
        actual = actual.getchildren()[0]
        assert mei.SCORE == actual.tag
        actual = actual.getchildren()[0]
        assert mei.SECTION == actual.tag
        assert section is actual

    def test_change_measure_hierarchy_1(self):
        '''
        That change_measure_hierarchy() works with reasonable input.
        '''
        initial = [
            '<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">',
                '<mei:scoreDef/>',
                '<mei:staff n="1">',
                    '<mei:measure n="1"/>',
                    '<mei:measure n="2"/>',
                '</mei:staff>',
                '<mei:staff n="2">',
                    '<mei:measure n="1"/>',
                    '<mei:measure n="2"/>',
                '</mei:staff>',
            '</mei:section>',
            ]
        initial = etree.fromstringlist(initial)
        expected = [
            '<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">',
                '<mei:scoreDef/>',
                '<mei:measure n="1">',
                    '<mei:staff n="1"/>',
                    '<mei:staff n="2"/>',
                '</mei:measure>',
                '<mei:measure n="2">',
                    '<mei:staff n="1"/>',
                    '<mei:staff n="2"/>',
                '</mei:measure>',
            '</mei:section>',
            ]

        actual = lmei_to_mei.change_measure_hierarchy(initial)

        assert ''.join(expected) == etree.tostring(actual)

    def test_change_measure_hierarchy_2(self):
        '''
        That change_measure_hierarchy() works when the <scoreDef> is missing.
        '''
        initial = [
            '<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">',
                '<mei:staff n="1">',
                    '<mei:measure n="1"/>',
                    '<mei:measure n="2"/>',
                '</mei:staff>',
                '<mei:staff n="2">',
                    '<mei:measure n="1"/>',
                    '<mei:measure n="2"/>',
                '</mei:staff>',
            '</mei:section>',
            ]
        initial = etree.fromstringlist(initial)
        expected = [
            '<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">',
                '<mei:measure n="1">',
                    '<mei:staff n="1"/>',
                    '<mei:staff n="2"/>',
                '</mei:measure>',
                '<mei:measure n="2">',
                    '<mei:staff n="1"/>',
                    '<mei:staff n="2"/>',
                '</mei:measure>',
            '</mei:section>',
            ]

        actual = lmei_to_mei.change_measure_hierarchy(initial)

        assert ''.join(expected) == etree.tostring(actual)

    def test_change_measure_hierarchy_3(self):
        '''
        That change_measure_hierarchy() works when one of the staves is missing the second measure.
        '''
        initial = [
            '<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">',
                '<mei:scoreDef/>',
                '<mei:staff n="1">',
                    '<mei:measure n="1"/>',
                    '<mei:measure n="2"/>',
                '</mei:staff>',
                '<mei:staff n="2">',
                    '<mei:measure n="1"/>',
                '</mei:staff>',
            '</mei:section>',
            ]
        initial = etree.fromstringlist(initial)
        expected = [
            '<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">',
                '<mei:scoreDef/>',
                '<mei:measure n="1">',
                    '<mei:staff n="1"/>',
                    '<mei:staff n="2"/>',
                '</mei:measure>',
                '<mei:measure n="2">',
                    '<mei:staff n="1"/>',
                '</mei:measure>',
            '</mei:section>',
            ]

        actual = lmei_to_mei.change_measure_hierarchy(initial)

        assert ''.join(expected) == etree.tostring(actual)

    # def test_change_measure_hierarchy_4(self):
    #     '''
    #     That change_measure_hierarchy() works when one of the staves is missing the first measure.
    #     NOTE: see Lychee issue 19 on GitLab
    #     '''
    #     initial = [
    #         '<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">',
    #             '<mei:scoreDef/>',
    #             '<mei:staff n="1">',
    #                 '<mei:measure n="1"/>',
    #                 '<mei:measure n="2"/>',
    #             '</mei:staff>',
    #             '<mei:staff n="2">',
    #                 '<mei:measure n="2"/>',
    #             '</mei:staff>',
    #         '</mei:section>',
    #         ]
    #     initial = etree.fromstringlist(initial)
    #     expected = [
    #         '<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">',
    #             '<mei:scoreDef/>',
    #             '<mei:measure n="1">',
    #                 '<mei:staff n="1"/>',
    #             '<mei:measure n="2">',
    #                 '<mei:staff n="1"/>',
    #                 '<mei:staff n="2"/>',
    #             '</mei:measure>',
    #         '</mei:section>',
    #         ]
    #
    #     actual = lmei_to_mei.change_measure_hierarchy(initial)
    #
    #     assert ''.join(expected) == etree.tostring(actual)

    def test_change_measure_hierarchy_5(self):
        '''
        That change_measure_hierarchy() works when there are no measures. Perhaps this isn't the best
        conversion, but we just want to make sure we don't fail completely.
        '''
        initial = [
            '<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">',
                '<mei:scoreDef/>',
                '<mei:staff n="1">',
                '</mei:staff>',
                '<mei:staff n="2">',
                '</mei:staff>',
            '</mei:section>',
            ]
        initial = etree.fromstringlist(initial)
        expected = [
            '<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">',
                '<mei:scoreDef/>',
            '</mei:section>',
            ]

        actual = lmei_to_mei.change_measure_hierarchy(initial)

        assert ''.join(expected) == etree.tostring(actual)


class TestToVerovio:

    @mock.patch('lychee.converters.lmei_to_verovio.lmei_to_mei.change_measure_hierarchy')
    @mock.patch('lychee.converters.lmei_to_verovio.lmei_to_mei.wrap_section_element')
    def test_export_for_verovio(self, mock_wrap, mock_change):
        '''
        Make sure it works.
        '''
        document = 'hello'
        wrap_return = etree.fromstring('<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei"></mei:section>')
        mock_wrap.return_value = wrap_return
        expected = '<?xml version="1.0" encoding="UTF-8"?><section xmlns:mei="http://www.music-encoding.org/ns/mei"/>'

        actual = lmei_to_verovio.export_for_verovio(document)

        mock_change.assert_called_once_with(document)
        assert expected == actual
        assert isinstance(actual, unicode)


@pytest.fixture
def signals_fixture(request):
    '''
    This fixture sets up Mock functions as the slots to the outbound.CONVERSION_STARTED,
    CONVERSION_FINISH, and CONVERSION_ERROR signals. The mocks are returned in that order, and
    automatically disconnected from the signals at the end of the test.
    '''

    # set up some slots for the three signals called by lmei_to_mei.convert()
    started_mock = mock.Mock()
    finish_mock = mock.Mock()
    error_mock = mock.Mock()
    def started_slot(**kwargs):
        started_mock(**kwargs)
    def finish_slot(**kwargs):
        finish_mock(**kwargs)
    def error_slot(**kwargs):
        error_mock(**kwargs)

    # connect the slots to the signals
    outbound.CONVERSION_STARTED.connect(started_slot)
    outbound.CONVERSION_FINISH.connect(finish_slot)
    outbound.CONVERSION_ERROR.connect(error_slot)

    def finalizer():
        # disconnect the slots
        outbound.CONVERSION_STARTED.disconnect(started_slot)
        outbound.CONVERSION_FINISH.disconnect(finish_slot)
        outbound.CONVERSION_ERROR.disconnect(error_slot)

    request.addfinalizer(finalizer)

    return started_mock, finish_mock, error_mock


class TestIntegration:
    '''
    Integration tests.
    '''

    def test_integration_to_mei_1(self, signals_fixture):
        '''
        An integration test for the LMEI to MEI converter.
        '''
        # NOTE: this is the same input document as for test_change_measure_hierarchy_1
        initial = ('<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei"><mei:scoreDef/>'
                   '<mei:staff n="1"><mei:measure n="1"/><mei:measure n="2"/></mei:staff>'
                   '<mei:staff n="2"><mei:measure n="1"/><mei:measure n="2"/></mei:staff>'
                   '</mei:section>'
                  )
        expected = ('<mei:mei xmlns:mei="http://www.music-encoding.org/ns/mei"><mei:music><mei:body>'
                    '<mei:mdiv><mei:score><mei:section><mei:scoreDef/><mei:measure n="1">'
                    '<mei:staff n="1"/><mei:staff n="2"/></mei:measure><mei:measure n="2">'
                    '<mei:staff n="1"/><mei:staff n="2"/></mei:measure></mei:section></mei:score>'
                    '</mei:mdiv></mei:body></mei:music></mei:mei>'
                   )
        started_mock, finish_mock, error_mock = signals_fixture
        document = etree.fromstring(initial)

        lmei_to_mei.convert(document)

        started_mock.assert_called_once_with()
        finish_mock.assert_called_once_with(converted=mock.ANY)
        assert 0 == error_mock.call_count
        # check the converted document
        actual = etree.tostring(finish_mock.call_args[1]['converted'])
        assert expected == actual

    def test_integration_to_mei_2(self, signals_fixture):
        '''
        For the LMEI to MEI converter. Input isn't an _Element at all.
        '''
        started_mock, finish_mock, error_mock = signals_fixture
        document = 'dddddddddddddd'
        lmei_to_mei.convert(document)
        started_mock.assert_called_once_with()
        assert 0 == finish_mock.call_count
        error_mock.assert_called_once_with(msg=lmei_to_mei._ERR_INPUT_NOT_SECTION)

    def test_integration_to_mei_3(self, signals_fixture):
        '''
        For the LMEI to MEI converter. Input is an _Element with the wrong tag.
        '''
        started_mock, finish_mock, error_mock = signals_fixture
        document = etree.Element('dddddddddddddd')
        lmei_to_mei.convert(document)
        started_mock.assert_called_once_with()
        assert 0 == finish_mock.call_count
        error_mock.assert_called_once_with(msg=lmei_to_mei._ERR_INPUT_NOT_SECTION)

    def test_integration_to_verovio_1(self, signals_fixture):
        '''
        An integration test for the LMEI to Verovio converer.
        '''
        # NOTE: this is the same input document as for test_change_measure_hierarchy_1
        initial = ('<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei"><mei:scoreDef/>'
                   '<mei:staff n="1"><mei:measure n="1"/><mei:measure n="2"/></mei:staff>'
                   '<mei:staff n="2"><mei:measure n="1"/><mei:measure n="2"/></mei:staff>'
                   '</mei:section>'
                  )
        expected = ('<?xml version="1.0" encoding="UTF-8"?>'
                    '<mei xmlns:mei="http://www.music-encoding.org/ns/mei"><music><body><mdiv><score>'
                    '<section><scoreDef/><measure n="1"><staff n="1"/><staff n="2"/></measure>'
                    '<measure n="2"><staff n="1"/><staff n="2"/></measure></section></score>'
                    '</mdiv></body></music></mei>'
                   )
        started_mock, finish_mock, error_mock = signals_fixture
        document = etree.fromstring(initial)

        lmei_to_verovio.convert(document)

        started_mock.assert_called_once_with()
        finish_mock.assert_called_once_with(converted=mock.ANY)
        assert 0 == error_mock.call_count
        # check the converted document
        actual = finish_mock.call_args[1]['converted']
        assert isinstance(actual, unicode)
        assert expected == actual

    def test_integration_to_verovio_2(self, signals_fixture):
        '''
        For the LMEI to Verovio converer. Input isn't an _Element at all.
        '''
        started_mock, finish_mock, error_mock = signals_fixture
        document = 'dddddddddddddd'
        lmei_to_verovio.convert(document)
        started_mock.assert_called_once_with()
        assert 0 == finish_mock.call_count
        error_mock.assert_called_once_with(msg=lmei_to_verovio._ERR_INPUT_NOT_SECTION)

    def test_integration_to_verovio_3(self, signals_fixture):
        '''
        For the LMEI to Verovio converer. Input is an _Element with the wrong tag.
        '''
        started_mock, finish_mock, error_mock = signals_fixture
        document = etree.Element('dddddddddddddd')
        lmei_to_verovio.convert(document)
        started_mock.assert_called_once_with()
        assert 0 == finish_mock.call_count
        error_mock.assert_called_once_with(msg=lmei_to_verovio._ERR_INPUT_NOT_SECTION)
