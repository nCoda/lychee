#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/utils/tests/test_lilypond.py
# Purpose:                Tests for LilyPond utilities
#
# Copyright (C) 2017 Nathan Ho and Jeffrey Treviño
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
Contain utilities for international conversion of pitch names in LilyPond.
'''
import pytest
from lychee import exceptions
from lychee.utils import lilypond_utils


class TestParsePitchName:

    def test_parse_pitch_name_1(self):
        """
        Dutch.
        """
        pitch_name = "ees"
        language = "nederlands"
        expected = ("e", "f")
        actual = lilypond_utils.parse_pitch_name(pitch_name, language)
        assert expected == actual


    def test_parse_pitch_name_2(self):
        """
        German.
        """
        pitch_name = "h"
        language = "deutsch"
        expected = ("b", "f")
        actual = lilypond_utils.parse_pitch_name(pitch_name, language)
        assert expected == actual


    def test_parse_pitch_name_error(self):
        """
        Nonexistent language.
        """
        pitch_name = "h"
        language = "nathan"
        with pytest.raises(exceptions.LilyPondError):
            lilypond_utils.parse_pitch_name(pitch_name, language)


class TestTranslatePitchName:

    def test_translate_pitch_name_1(self):
        """
        Dutch.
        """
        pitch_name = "e"
        accidental = "f"
        language = "nederlands"
        expected = "ees"
        actual = lilypond_utils.translate_pitch_name(pitch_name, accidental, language)
        assert expected == actual

    def test_translate_pitch_name_2(self):
        """
        German.
        """
        pitch_name = "b"
        accidental = "f"
        language = "deutsch"
        expected = "h"
        actual = lilypond_utils.translate_pitch_name(pitch_name, accidental, language)
        assert expected == actual

    def test_translate_pitch_name_error(self):
        """
        Nonexistent language.
        """
        pitch_name = "b"
        accidental = "f"
        language = "tacos"
        with pytest.raises(exceptions.LilyPondError):
            lilypond_utils.translate_pitch_name(pitch_name, accidental, language)

