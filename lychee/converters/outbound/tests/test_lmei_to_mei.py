#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/test/test_lmei_to_mei.py
# Purpose:                Tests for "lmei_to_mei.py" and "verovio.py"
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
Tests for "lmei_to_mei.py" and "verovio.py"
'''

from lxml import etree
import pytest
import six

try:
    from unittest import mock
except ImportError:
    import mock

from lychee.converters.outbound import verovio, mei as lmei_to_mei
from lychee import exceptions
from lychee.namespaces import mei
from lychee.signals import outbound


def assert_elements_equal(first, second):
    '''
    Type-specific equality function for :class:`lxml.etree.Element` and
    :class:`lxml.etree.ElementTree` objects.
    '''
    assert first.tag == second.tag
    assert first.attrib == second.attrib
    assert len(first) == len(second)

    first_children = list(first)
    second_children = list(second)

    for i in range(len(first_children)):
        try:
            assert_elements_equal(first_children[i], second_children[i])
        except AssertionError:
            print('failed with children of {tag}'.format(tag=first.tag))
            raise


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


class TestMeasureCreation(object):

    def test_1(self):
        """one staff, several measures, 4/4 time signature given"""
        initial = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:rest dur="4"/>
                        <mei:rest dur="2"/>
                        <mei:rest dur="4"/>
                        <!-- m.2 -->
                        <mei:rest dur="1"/>
                        <!-- m.3 -->
                        <mei:rest dur="2"/>
                        <mei:rest dur="4"/>
                        <mei:rest dur="4"/>
                        <!-- m.4 -->
                        <mei:rest dur="1"/>
                    </mei:layer>
                </mei:staff>
            </mei:section>
            ''')
        expected = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:measure n="1">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="4"/>
                            <mei:rest dur="2"/>
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="2">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="3">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="2"/>
                            <mei:rest dur="4"/>
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="4">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
            </mei:section>
            ''')

        actual = lmei_to_mei.create_measures(initial)

        assert_elements_equal(expected, actual)

    def test_several_layers(self):
        """one staff, a few layers, a few measures"""
        initial = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:rest dur="2"/>
                        <mei:rest dur="2"/>
                        <!-- m.2 -->
                        <mei:rest dur="1"/>
                    </mei:layer>
                    <mei:layer n="2">
                        <!-- m.1 -->
                        <mei:rest dur="1"/>
                        <!-- m.2 -->
                        <mei:rest dur="2"/>
                        <mei:rest dur="2"/>
                    </mei:layer>
                </mei:staff>
            </mei:section>
            ''')
        expected = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:measure n="1">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="2"/>
                            <mei:rest dur="2"/>
                        </mei:layer>
                        <mei:layer n="2">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="2">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                        <mei:layer n="2">
                            <mei:rest dur="2"/>
                            <mei:rest dur="2"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
            </mei:section>
            ''')

        actual = lmei_to_mei.create_measures(initial)

        assert_elements_equal(expected, actual)

    def test_1a_dots(self):
        """Same as test_1() but with a dotted note."""
        initial = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:rest dur="4"/>
                        <mei:rest dur="2"/>
                        <mei:rest dur="4"/>
                        <!-- m.2 -->
                        <mei:rest dur="1"/>
                        <!-- m.3 -->
                        <mei:rest dur="2" dots="1"/>
                        <mei:rest dur="4"/>
                        <!-- m.4 -->
                        <mei:rest dur="1"/>
                    </mei:layer>
                </mei:staff>
            </mei:section>
            ''')
        expected = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:measure n="1">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="4"/>
                            <mei:rest dur="2"/>
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="2">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="3">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="2" dots="1"/>
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="4">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
            </mei:section>
            ''')

        actual = lmei_to_mei.create_measures(initial)

        assert_elements_equal(expected, actual)

    def test_1b_dots(self):
        """Same as test_1a() but with a double-dotted note."""
        initial = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:rest dur="2" dots="2"/>
                        <mei:rest dur="8"/>
                        <!-- m.2 -->
                        <mei:rest dur="1"/>
                        <!-- m.3 -->
                        <mei:rest dur="2" dots="1"/>
                        <mei:rest dur="4"/>
                        <!-- m.4 -->
                        <mei:rest dur="1"/>
                    </mei:layer>
                </mei:staff>
            </mei:section>
            ''')
        expected = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:measure n="1">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="2" dots="2"/>
                            <mei:rest dur="8"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="2">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="3">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="2" dots="1"/>
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="4">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
            </mei:section>
            ''')

        actual = lmei_to_mei.create_measures(initial)

        assert_elements_equal(expected, actual)

    def test_assumes_4_4(self):
        """
        One staff, several measures, no time signature; should assume 4/4 metre.

        NB: it's the same as test_1() but the time signature is missing from the input.
        """
        initial = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:rest dur="4"/>
                        <mei:rest dur="2"/>
                        <mei:rest dur="4"/>
                        <!-- m.2 -->
                        <mei:rest dur="1"/>
                        <!-- m.3 -->
                        <mei:rest dur="2"/>
                        <mei:rest dur="4"/>
                        <mei:rest dur="4"/>
                        <!-- m.4 -->
                        <mei:rest dur="1"/>
                    </mei:layer>
                </mei:staff>
            </mei:section>
            ''')
        expected = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:measure n="1">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="4"/>
                            <mei:rest dur="2"/>
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="2">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="3">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="2"/>
                            <mei:rest dur="4"/>
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="4">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
            </mei:section>
            ''')

        actual = lmei_to_mei.create_measures(initial)

        assert_elements_equal(expected, actual)

    def test_6_8_metre(self):
        """
        One staff, several measures, 6/8 time signature given.

        NB: This test guarantees a whole note in 6/8 is only interpreted as taking up the duration
            of six eighth notes.
        """
        initial = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="6" meter.unit="8"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:rest dur="4"/>
                        <mei:rest dur="4"/>
                        <mei:rest dur="4"/>
                        <!-- m.2 -->
                        <mei:rest dur="8"/>
                        <mei:rest dur="8"/>
                        <mei:rest dur="8"/>
                        <mei:rest dur="8"/>
                        <mei:rest dur="8"/>
                        <mei:rest dur="8"/>
                        <!-- m.3 -->
                        <mei:rest dur="4" dots="1"/>
                        <mei:rest dur="8"/>
                        <mei:rest dur="8"/>
                        <mei:rest dur="8"/>
                        <!-- m.4 -->
                        <mei:rest dur="1"/>
                        <!-- m.5 -->
                        <mei:rest dur="8"/>
                    </mei:layer>
                </mei:staff>
            </mei:section>
            ''')
        expected = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="6" meter.unit="8"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:measure n="1">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="4"/>
                            <mei:rest dur="4"/>
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="2">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="8"/>
                            <mei:rest dur="8"/>
                            <mei:rest dur="8"/>
                            <mei:rest dur="8"/>
                            <mei:rest dur="8"/>
                            <mei:rest dur="8"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="3">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="4" dots="1"/>
                            <mei:rest dur="8"/>
                            <mei:rest dur="8"/>
                            <mei:rest dur="8"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="4">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="5">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="8"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
            </mei:section>
            ''')

        actual = lmei_to_mei.create_measures(initial)

        assert_elements_equal(expected, actual)

    def test_3_2_metre(self):
        """
        One staff, several measures, 3/2 time signature given.

        NB: This test guarantees a whole note on beat one in 3/2 will take up all three half notes,
            but a whole note on beat 0.5 will only use four quarter notes.
        """
        initial = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="3" meter.unit="2"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:rest dur="2"/>
                        <mei:rest dur="2"/>
                        <mei:rest dur="2"/>
                        <!-- m.2 -->
                        <mei:rest dur="4"/>
                        <mei:rest dur="4"/>
                        <mei:rest dur="4"/>
                        <mei:rest dur="4"/>
                        <mei:rest dur="4"/>
                        <mei:rest dur="4"/>
                        <!-- m.3 -->
                        <mei:rest dur="2" dots="1"/>
                        <mei:rest dur="4"/>
                        <mei:rest dur="4"/>
                        <mei:rest dur="4"/>
                        <!-- m.4 -->
                        <mei:rest dur="1"/>
                        <!-- m.5 -->
                        <mei:rest dur="4"/>
                        <mei:rest dur="1"/>
                        <mei:rest dur="4"/>
                        <!-- m.6 -->
                        <mei:rest dur="4"/>
                    </mei:layer>
                </mei:staff>
            </mei:section>
            ''')
        expected = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="3" meter.unit="2"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:measure n="1">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="2"/>
                            <mei:rest dur="2"/>
                            <mei:rest dur="2"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="2">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="4"/>
                            <mei:rest dur="4"/>
                            <mei:rest dur="4"/>
                            <mei:rest dur="4"/>
                            <mei:rest dur="4"/>
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="3">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="2" dots="1"/>
                            <mei:rest dur="4"/>
                            <mei:rest dur="4"/>
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="4">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="5">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="4"/>
                            <mei:rest dur="1"/>
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="6">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
            </mei:section>
            ''')

        actual = lmei_to_mei.create_measures(initial)

        assert_elements_equal(expected, actual)

    # def test_tuplets_3_4(self):
    #     """one staff, several measures, 3/4 time signature given; handles tuplets properly"""
    #     pass

    def test_multi_staff_polyphony(self):
        """
        Properly handles polyphony created in the <staff n="1"> <staff n="1"> LilyPond way.

        Change between monophony/polyphony on a barline.
        """
        initial = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:rest dur="1"/>
                        <!-- m.2 -->
                        <mei:rest dur="2"/>
                        <mei:rest dur="2"/>
                    </mei:layer>
                </mei:staff>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <!-- m.3 -->
                        <mei:rest dur="1"/>
                        <!-- m.4 -->
                        <mei:rest dur="2"/>
                        <mei:rest dur="2"/>
                    </mei:layer>
                    <mei:layer n="2">
                        <!-- m.3 -->
                        <mei:rest dur="2"/>
                        <mei:rest dur="2"/>
                        <!-- m.4 -->
                        <mei:rest dur="1"/>
                    </mei:layer>
                </mei:staff>
            </mei:section>
            ''')
        expected = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:measure n="1">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="2">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="2"/>
                            <mei:rest dur="2"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="3">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                        <mei:layer n="2">
                            <mei:rest dur="2"/>
                            <mei:rest dur="2"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="4">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="2"/>
                            <mei:rest dur="2"/>
                        </mei:layer>
                        <mei:layer n="2">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
            </mei:section>
            ''')

        actual = lmei_to_mei.create_measures(initial)

        assert_elements_equal(expected, actual)

    def test_three_staves(self):
        """three staves, several measures, 4/4 time signature given"""
        initial = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                            <mei:staffDef lines="5" n="2" meter.count="4" meter.unit="4"/>
                            <mei:staffDef lines="5" n="3" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:rest dur="2"/>
                        <mei:rest dur="2"/>
                        <!-- m.2 -->
                        <mei:rest dur="1"/>
                    </mei:layer>
                </mei:staff>
                <mei:staff n="2">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:rest dur="2"/>
                        <mei:rest dur="2"/>
                        <!-- m.2 -->
                        <mei:rest dur="1"/>
                    </mei:layer>
                </mei:staff>
                <mei:staff n="3">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:rest dur="2"/>
                        <mei:rest dur="2"/>
                        <!-- m.2 -->
                        <mei:rest dur="1"/>
                    </mei:layer>
                </mei:staff>
            </mei:section>
            ''')
        expected = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                            <mei:staffDef lines="5" n="2" meter.count="4" meter.unit="4"/>
                            <mei:staffDef lines="5" n="3" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:measure n="1">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="2"/>
                            <mei:rest dur="2"/>
                        </mei:layer>
                    </mei:staff>
                    <mei:staff n="2">
                        <mei:layer n="1">
                            <mei:rest dur="2"/>
                            <mei:rest dur="2"/>
                        </mei:layer>
                    </mei:staff>
                    <mei:staff n="3">
                        <mei:layer n="1">
                            <mei:rest dur="2"/>
                            <mei:rest dur="2"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="2">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                    <mei:staff n="2">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                    <mei:staff n="3">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
            </mei:section>
            ''')

        actual = lmei_to_mei.create_measures(initial)

        assert_elements_equal(expected, actual)

    def test_tuplets_1(self):
        """one measure, one tuplet, 4/4 time"""
        initial = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <mei:tupletSpan
                            endid="#tuplet-rest-3"
                            num="3"
                            numbase="2"
                            plist="#tuplet-rest-1 #tuplet-rest-2 #tuplet-rest-3"
                            startid="#tuplet-rest-1"
                        />
                        <!-- m.1 -->
                        <mei:rest dur="2" xml:id="tuplet-rest-1"/>
                        <mei:rest dur="2" xml:id="tuplet-rest-2"/>
                        <mei:rest dur="2" xml:id="tuplet-rest-3"/>
                        <!-- m.2 -->
                        <mei:rest dur="1"/>
                    </mei:layer>
                </mei:staff>
            </mei:section>
            ''')
        expected = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="4" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:measure n="1">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:tupletSpan
                                endid="#tuplet-rest-3"
                                num="3"
                                numbase="2"
                                plist="#tuplet-rest-1 #tuplet-rest-2 #tuplet-rest-3"
                                startid="#tuplet-rest-1"
                            />
                            <mei:rest dur="2" xml:id="tuplet-rest-1"/>
                            <mei:rest dur="2" xml:id="tuplet-rest-2"/>
                            <mei:rest dur="2" xml:id="tuplet-rest-3"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="2">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
            </mei:section>
            ''')

        actual = lmei_to_mei.create_measures(initial)
        etree.dump(actual)

        assert_elements_equal(expected, actual)

    def test_tuplets_2(self):
        """one measure, two tuplets, 3/4 time"""
        initial = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="3" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:tupletSpan
                            endid="#tuplet-rest-3"
                            num="3"
                            numbase="2"
                            plist="#tuplet-rest-1 #tuplet-rest-2 #tuplet-rest-3"
                            startid="#tuplet-rest-1"
                        />
                        <mei:rest dur="8" xml:id="tuplet-rest-1"/>
                        <mei:rest dur="8" xml:id="tuplet-rest-2"/>
                        <mei:rest dur="8" xml:id="tuplet-rest-3"/>
                        <mei:rest dur="4"/>
                        <mei:tupletSpan
                            endid="#tuplet-rest-6"
                            num="3"
                            numbase="2"
                            plist="#tuplet-rest-4 #tuplet-rest-5 #tuplet-rest-6"
                            startid="#tuplet-rest-4"
                        />
                        <mei:rest dur="8" xml:id="tuplet-rest-4"/>
                        <mei:rest dur="8" xml:id="tuplet-rest-5"/>
                        <mei:rest dur="8" xml:id="tuplet-rest-6"/>
                        <!-- m.2 -->
                        <mei:rest dur="1"/>
                    </mei:layer>
                </mei:staff>
            </mei:section>
            ''')
        expected = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="3" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:measure n="1">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:tupletSpan
                                endid="#tuplet-rest-3"
                                num="3"
                                numbase="2"
                                plist="#tuplet-rest-1 #tuplet-rest-2 #tuplet-rest-3"
                                startid="#tuplet-rest-1"
                            />
                            <mei:rest dur="8" xml:id="tuplet-rest-1"/>
                            <mei:rest dur="8" xml:id="tuplet-rest-2"/>
                            <mei:rest dur="8" xml:id="tuplet-rest-3"/>
                            <mei:rest dur="4"/>
                            <mei:tupletSpan
                                endid="#tuplet-rest-6"
                                num="3"
                                numbase="2"
                                plist="#tuplet-rest-4 #tuplet-rest-5 #tuplet-rest-6"
                                startid="#tuplet-rest-4"
                            />
                            <mei:rest dur="8" xml:id="tuplet-rest-4"/>
                            <mei:rest dur="8" xml:id="tuplet-rest-5"/>
                            <mei:rest dur="8" xml:id="tuplet-rest-6"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="2">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
            </mei:section>
            ''')

        actual = lmei_to_mei.create_measures(initial)
        etree.dump(actual)

        assert_elements_equal(expected, actual)

    def test_tuplets_3(self):
        """one measure, one-level nested tuplets, 3/4 time"""
        initial = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="3" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:staff n="1">
                    <mei:layer n="1">
                        <!-- m.1 -->
                        <mei:tupletSpan
                            endid="#tuplet-rest-5"
                            num="3"
                            numbase="2"
                            plist="#tuplet-rest-1 #tuplet-rest-2 #tuplet-rest-3 #tuplet-rest-4 #tuplet-rest-5"
                            startid="#tuplet-rest-1"
                        />
                        <mei:tupletSpan
                            endid="#tuplet-rest-5"
                            num="3"
                            numbase="2"
                            plist="#tuplet-rest-3 #tuplet-rest-4 #tuplet-rest-5"
                            startid="#tuplet-rest-3"
                        />
                        <mei:rest dur="4"/>
                        <mei:rest dur="8" xml:id="tuplet-rest-1"/>
                        <mei:rest dur="8" xml:id="tuplet-rest-2"/>
                        <mei:rest dur="8" xml:id="tuplet-rest-3"/>
                        <mei:rest dur="8" xml:id="tuplet-rest-4"/>
                        <mei:rest dur="8" xml:id="tuplet-rest-5"/>
                        <mei:rest dur="4"/>
                        <!-- m.2 -->
                        <mei:rest dur="1"/>
                    </mei:layer>
                </mei:staff>
            </mei:section>
            ''')
        expected = etree.fromstring('''
            <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:scoreDef>
                    <mei:staffGrp symbol="none">
                        <mei:staffGrp symbol="bracket">
                            <mei:staffDef lines="5" n="1" meter.count="3" meter.unit="4"/>
                        </mei:staffGrp>
                    </mei:staffGrp>
                </mei:scoreDef>
                <mei:measure n="1">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:tupletSpan
                                endid="#tuplet-rest-5"
                                num="3"
                                numbase="2"
                                plist="#tuplet-rest-1 #tuplet-rest-2 #tuplet-rest-3 #tuplet-rest-4 #tuplet-rest-5"
                                startid="#tuplet-rest-1"
                            />
                            <mei:tupletSpan
                                endid="#tuplet-rest-5"
                                num="3"
                                numbase="2"
                                plist="#tuplet-rest-3 #tuplet-rest-4 #tuplet-rest-5"
                                startid="#tuplet-rest-3"
                            />
                            <mei:rest dur="4"/>
                            <mei:rest dur="8" xml:id="tuplet-rest-1"/>
                            <mei:rest dur="8" xml:id="tuplet-rest-2"/>
                            <mei:rest dur="8" xml:id="tuplet-rest-3"/>
                            <mei:rest dur="8" xml:id="tuplet-rest-4"/>
                            <mei:rest dur="8" xml:id="tuplet-rest-5"/>
                            <mei:rest dur="4"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
                <mei:measure n="2">
                    <mei:staff n="1">
                        <mei:layer n="1">
                            <mei:rest dur="1"/>
                        </mei:layer>
                    </mei:staff>
                </mei:measure>
            </mei:section>
            ''')

        actual = lmei_to_mei.create_measures(initial)
        etree.dump(actual)

        assert_elements_equal(expected, actual)


class TestToVerovio:

    @mock.patch('lychee.converters.outbound.verovio.lmei_to_mei.change_measure_hierarchy')
    @mock.patch('lychee.converters.outbound.verovio.lmei_to_mei.wrap_section_element')
    def test_export_for_verovio(self, mock_wrap, mock_change):
        '''
        Make sure it works.
        '''
        document = 'hello'
        wrap_return = etree.fromstring('<mei:section xmlns:mei="http://www.music-encoding.org/ns/mei"></mei:section>')
        mock_wrap.return_value = wrap_return
        expected = '<?xml version="1.0" encoding="UTF-8"?><section xmlns:mei="http://www.music-encoding.org/ns/mei"/>'

        actual = verovio.export_for_verovio(document)

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

    def test_integration_to_mei_1(self):
        '''
        An integration test for the LMEI to MEI converter.
        '''
        # NOTE: this is the same input document as for test_change_measure_hierarchy_1
        initial = ('<mei:section xml:id="lol" xmlns:mei="http://www.music-encoding.org/ns/mei"><mei:scoreDef/>'
                   '<mei:staff n="1"><mei:measure n="1"/><mei:measure n="2"/></mei:staff>'
                   '<mei:staff n="2"><mei:measure n="1"/><mei:measure n="2"/></mei:staff>'
                   '</mei:section>'
                  )
        expected = ('<mei:mei xmlns:mei="http://www.music-encoding.org/ns/mei"><mei:music><mei:body>'
                    '<mei:mdiv><mei:score><mei:section xml:id="lol"><mei:scoreDef/><mei:measure n="1">'
                    '<mei:staff n="1"/><mei:staff n="2"/></mei:measure><mei:measure n="2">'
                    '<mei:staff n="1"/><mei:staff n="2"/></mei:measure></mei:section></mei:score>'
                    '</mei:mdiv></mei:body></mei:music></mei:mei>'
                   )
        document = etree.fromstring(initial)

        actual = lmei_to_mei.convert(document, method='c14n')

        assert expected == etree.tostring(actual)

    def test_integration_to_mei_2(self):
        '''
        For the LMEI to MEI converter. Input isn't an _Element at all.
        '''
        document = 'dddddddddddddd'
        with pytest.raises(exceptions.OutboundConversionError) as exc:
            lmei_to_mei.convert(document)
        assert lmei_to_mei._ERR_INPUT_NOT_SECTION == exc.value.args[0]

    def test_integration_to_mei_3(self):
        '''
        For the LMEI to MEI converter. Input is an _Element with the wrong tag.
        '''
        document = etree.Element('dddddddddddddd')
        with pytest.raises(exceptions.OutboundConversionError) as exc:
            lmei_to_mei.convert(document)
        assert lmei_to_mei._ERR_INPUT_NOT_SECTION == exc.value.args[0]

    def test_integration_to_verovio_1(self):
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
        document = etree.fromstring(initial)

        actual = verovio.convert(document)

        assert expected == actual

    def test_integration_to_verovio_2(self):
        '''
        For the LMEI to Verovio converer. Input isn't an _Element at all.
        '''
        document = 'dddddddddddddd'
        with pytest.raises(exceptions.OutboundConversionError) as exc:
            verovio.convert(document)
        assert verovio._ERR_INPUT_NOT_SECTION == exc.value.args[0]

    def test_integration_to_verovio_3(self):
        '''
        For the LMEI to Verovio converer. Input is an _Element with the wrong tag.
        '''
        document = etree.Element('dddddddddddddd')
        with pytest.raises(exceptions.OutboundConversionError) as exc:
            verovio.convert(document)
        assert verovio._ERR_INPUT_NOT_SECTION == exc.value.args[0]
