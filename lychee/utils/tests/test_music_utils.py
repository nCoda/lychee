#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/utils/tests/test_music_utils.py
# Purpose:                Tests for music utilities
#
# Copyright (C) 2017 Nathan Ho
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
Unit tests for Lychee's music utilities.
'''
from lxml import etree
from lychee import exceptions
from lychee.utils import music_utils


def test_key_signatures():
    '''
    The KEY_SIGNATURES dictionary should fit the algorithm for key signatures.
    '''
    expected = ['n'] * 7
    next_flat = 6
    for i in range(8):
        key_signature_name = str(i) + ('' if i == 0 else 'f')
        key_signature = music_utils.KEY_SIGNATURES[key_signature_name]
        actual = [key_signature[note_name] for note_name in music_utils.NOTE_NAMES]
        assert expected == actual

        expected[next_flat] = 'f'
        next_flat = (next_flat + 3) % 7

    expected = ['n'] * 7
    next_sharp = 3
    for i in range(8):
        key_signature_name = str(i) + ('' if i == 0 else 's')
        key_signature = music_utils.KEY_SIGNATURES[key_signature_name]
        actual = [key_signature[note_name] for note_name in music_utils.NOTE_NAMES]
        assert expected == actual

        expected[next_sharp] = 's'
        next_sharp = (next_sharp - 3) % 7
