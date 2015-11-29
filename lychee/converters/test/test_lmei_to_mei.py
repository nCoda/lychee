#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/test/test_lmei_to_mei.py
# Purpose:                Tests for "lmei_to_mei.py" and "lmei_to_verovio.py"
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
Tests for "lmei_to_mei.py" and "lmei_to_verovio.py"
'''

from lxml import etree

try:
    from unittest import mock
except ImportError:
    import mock

from lychee.converters import lmei_to_mei, lmei_to_verovio
from lychee.namespaces import mei


def test_wrap_section_element():
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


def test_change_measure_hierarchy_1():
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


def test_change_measure_hierarchy_2():
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


def test_change_measure_hierarchy_3():
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


# def test_change_measure_hierarchy_4():
#     '''
#     That change_measure_hierarchy() works when one of the staves is missing the first measure.
#     TODO: get this to work
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


def test_change_measure_hierarchy_5():
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


@mock.patch('lychee.converters.lmei_to_verovio.lmei_to_mei.change_measure_hierarchy')
@mock.patch('lychee.converters.lmei_to_verovio.lmei_to_mei.wrap_section_element')
def test_export_for_verovio(mock_wrap, mock_change):
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
