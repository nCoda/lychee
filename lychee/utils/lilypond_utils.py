#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/utils/lilypond.py
# Purpose:                LilyPond utility functions
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
from lychee.utils import lilypond_note_names
from lychee import exceptions


def parse_pitch_name(pitch_name, language="nederlands"):
    """
    Convert a pitch name in another language to an English pair (name, accidental).
    """
    if language not in lilypond_note_names.inbound:
        raise exceptions.LilyPondError("Unrecognized language: '{}'".format(language))
    language_dict = lilypond_note_names.inbound[language]
    if pitch_name not in language_dict:
        raise exceptions.LilyPondError(
            "Pitch name '{}' is not valid in language '{}'".format(pitch_name, language))
    return language_dict[pitch_name]


def translate_pitch_name(pitch_name, accidental, language="nederlands"):
    """
    Convert the English pair (name, accidental) to a pitch name in another language.
    """
    if language not in lilypond_note_names.outbound:
        raise exceptions.LilyPondError("Unrecognized language: '{}'".format(language))
    language_dict = lilypond_note_names.outbound[language]
    if accidental == 'n':
        accidental = ''
    pitch_string = pitch_name + accidental
    if pitch_string not in language_dict:
        raise exceptions.LilyPondError(
            "Pitch name '{}' is not valid in language '{}'".format(pitch_string, language))
    return language_dict[pitch_string]
