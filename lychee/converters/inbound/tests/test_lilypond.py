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
