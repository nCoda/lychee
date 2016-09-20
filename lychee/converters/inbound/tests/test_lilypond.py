#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/tests/test_lilypond.py
# Purpose:                Tests for the "lilypond" module.
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
"""
Tests for the "lilypond" module.

The tests in this file are only for the translator, not the parser. In other words, these tests are
for the code that translated Grako's parse into Lychee-MEI.
"""

from lxml import etree
import pytest

from lychee.converters.inbound import lilypond
from lychee import exceptions
from lychee.namespaces import mei


class TestProcessOctave(object):
    """
    For the octave thing.
    """

    def test_works(self):
        """It's an octave."""
        assert '1' == lilypond.process_octave(',,')

    def test_none(self):
        """It's given ``None``."""
        assert '3' == lilypond.process_octave(None)

    def test_invalid(self):
        """The octave is invalid."""
        assert lilypond.process_octave(None) == lilypond.process_octave('celery')


class TestAccidentals(object):
    """
    For regular accidental handling.
    """

    def test_no_accid(self):
        """When there is no accidental."""
        l_accid = []
        attrib = {}
        expected = {}
        actual = lilypond.process_accidental(l_accid, attrib)
        assert expected == actual

    def test_double_sharp(self):
        """Double sharp."""
        l_accid = ['is', 'is']
        attrib = {}
        expected = {'accid.ges': 'ss'}
        actual = lilypond.process_accidental(l_accid, attrib)
        assert expected == actual

    def test_single_flat(self):
        """Single flat."""
        l_accid = ['es']
        attrib = {}
        expected = {'accid.ges': 'f'}
        actual = lilypond.process_accidental(l_accid, attrib)
        assert expected == actual

    def test_sharpflat(self):
        """Sharpflat (invalid accidental)."""
        l_accid = ['is', 'es']
        attrib = {}
        expected = {}
        actual = lilypond.process_accidental(l_accid, attrib)
        assert expected == actual


class TestForcedAccidentals(object):
    """
    For the forced accidental stuff.
    """

    def test_dont_add_it(self):
        """The note doesn't have a forced accidental."""
        l_note = {'accid_force': None}  # this is enough to trick it
        attrib = {}

        actual = lilypond.process_forced_accid(l_note, attrib)

        assert actual == {}

    def test_add_a_flat(self):
        """The note has a forced flat."""
        l_note = {'accid_force': '!'}  # this is enough to trick it
        attrib = {'accid.ges': 'f'}

        actual = lilypond.process_forced_accid(l_note, attrib)

        assert actual == {'accid.ges': 'f', 'accid': 'f'}

    def test_add_a_natural(self):
        """The note has a forced natural."""
        l_note = {'accid_force': '!'}  # this is enough to trick it
        attrib = {'dur': '4'}  # check it doesn't erase unrelated keys

        actual = lilypond.process_forced_accid(l_note, attrib)

        assert actual == {'dur': '4', 'accid': 'n'}


class TestCautionaryAccidentals(object):
    """
    For the cautionary accidental garbage.
    """

    def test_dont_add_it(self):
        """The note doesn't have a cautionary accidental."""
        l_note = {'accid_force': None}  # this is enough to trick it
        m_note = etree.Element(mei.NOTE)

        actual = lilypond.process_caut_accid(l_note, m_note)

        assert len(actual) == 0  # includes child elements only

    def test_add_a_flat(self):
        """The note has a cautionary flat."""
        l_note = {'accid_force': '?'}  # this is enough to trick it
        m_note = etree.Element(mei.NOTE, {'accid.ges': 'f'})

        actual = lilypond.process_caut_accid(l_note, m_note)

        assert len(actual) == 1  # includes child elements only
        assert actual[0].tag == mei.ACCID
        assert actual[0].get('accid') == 'f'
        assert actual[0].get('func') == 'caution'

    def test_add_a_natural(self):
        """The note has a cautionary natural."""
        l_note = {'accid_force': '?'}  # this is enough to trick it
        m_note = etree.Element(mei.NOTE)

        actual = lilypond.process_caut_accid(l_note, m_note)

        assert len(actual) == 1  # includes child elements only
        assert actual[0].tag == mei.ACCID
        assert actual[0].get('accid') == 'n'
        assert actual[0].get('func') == 'caution'


class TestProcesssDots(object):
    """
    For the @dots attribute.
    """

    def test_dots_1(self):
        """No dots."""
        l_node = {'dots': []}
        attrib = {}
        actual = lilypond.process_dots(l_node, attrib)
        assert 'dots' not in attrib

    def test_dots_2(self):
        """Three dots."""
        l_node = {'dots': ['.', '.', '.']}
        attrib = {}
        actual = lilypond.process_dots(l_node, attrib)
        assert attrib['dots'] == '3'

    def test_dots_3(self):
        """No "dots" member in "l_node"."""
        l_node = {'clots': ['.']}
        attrib = {}
        actual = lilypond.process_dots(l_node, attrib)
        assert 'dots' not in attrib


class TestRestSpacer(object):
    """
    For rests and spacers.
    """

    def test_rest_1(self):
        """When it works fine, no dots."""
        l_rest = {'ly_type': 'rest', 'dur': '2', 'dots': []}
        m_layer = etree.Element(mei.LAYER)

        actual = lilypond.do_rest(l_rest, m_layer)

        assert actual.tag == mei.REST
        assert m_layer[0] is actual
        assert actual.get('dur') == '2'
        assert actual.get('dots') is None

    def test_rest_2(self):
        """When it works fine, two dots."""
        l_rest = {'ly_type': 'rest', 'dur': '2', 'dots': ['.', '.']}
        m_layer = etree.Element(mei.LAYER)

        actual = lilypond.do_rest(l_rest, m_layer)

        assert actual.get('dur') == '2'
        assert actual.get('dots') == '2'

    def test_rest_3(self):
        """When it receives a spacer, should fail."""
        l_rest = {'ly_type': 'spacer', 'dur': '2', 'dots': []}
        m_layer = etree.Element(mei.LAYER)

        with pytest.raises(exceptions.LilyPondError):
            lilypond.do_rest(l_rest, m_layer)

    def test_spacer_1(self):
        """When it works fine, no dots."""
        l_rest = {'ly_type': 'spacer', 'dur': '2', 'dots': []}
        m_layer = etree.Element(mei.LAYER)

        actual = lilypond.do_spacer(l_rest, m_layer)

        assert actual.tag == mei.SPACE
        assert m_layer[0] is actual
        assert actual.get('dur') == '2'
        assert actual.get('dots') is None

    def test_spacer_2(self):
        """When it works fine, two dots."""
        l_rest = {'ly_type': 'spacer', 'dur': '2', 'dots': ['.', '.']}
        m_layer = etree.Element(mei.LAYER)

        actual = lilypond.do_spacer(l_rest, m_layer)

        assert actual.get('dur') == '2'
        assert actual.get('dots') == '2'

    def test_spacer_3(self):
        """When it receives a rest, should fail."""
        l_rest = {'ly_type': 'rest', 'dur': '2', 'dots': []}
        m_layer = etree.Element(mei.LAYER)

        with pytest.raises(exceptions.LilyPondError):
            lilypond.do_spacer(l_rest, m_layer)
