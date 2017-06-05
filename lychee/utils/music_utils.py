#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/utils/music_utils.py
# Purpose:                Music utilities
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
Contains utilities that specifically concern LMEI as music notation. These tools are agnostic to any
inbound or outbound conversion formats, although they are useful in converters.
'''
from lychee import exceptions
import fractions

KEY_SIGNATURES = {
    '7f': {'c': 'f', 'd': 'f', 'e': 'f', 'f': 'f', 'g': 'f', 'a': 'f', 'b': 'f'},
    '6f': {'c': 'f', 'd': 'f', 'e': 'f', 'f': 'n', 'g': 'f', 'a': 'f', 'b': 'f'},
    '5f': {'c': 'n', 'd': 'f', 'e': 'f', 'f': 'n', 'g': 'f', 'a': 'f', 'b': 'f'},
    '4f': {'c': 'n', 'd': 'f', 'e': 'f', 'f': 'n', 'g': 'n', 'a': 'f', 'b': 'f'},
    '3f': {'c': 'n', 'd': 'n', 'e': 'f', 'f': 'n', 'g': 'n', 'a': 'f', 'b': 'f'},
    '2f': {'c': 'n', 'd': 'n', 'e': 'f', 'f': 'n', 'g': 'n', 'a': 'n', 'b': 'f'},
    '1f': {'c': 'n', 'd': 'n', 'e': 'n', 'f': 'n', 'g': 'n', 'a': 'n', 'b': 'f'},
    '0': {'c': 'n', 'd': 'n', 'e': 'n', 'f': 'n', 'g': 'n', 'a': 'n', 'b': 'n'},
    '1s': {'c': 'n', 'd': 'n', 'e': 'n', 'f': 's', 'g': 'n', 'a': 'n', 'b': 'n'},
    '2s': {'c': 's', 'd': 'n', 'e': 'n', 'f': 's', 'g': 'n', 'a': 'n', 'b': 'n'},
    '3s': {'c': 's', 'd': 'n', 'e': 'n', 'f': 's', 'g': 's', 'a': 'n', 'b': 'n'},
    '4s': {'c': 's', 'd': 's', 'e': 'n', 'f': 's', 'g': 's', 'a': 'n', 'b': 'n'},
    '6s': {'c': 's', 'd': 's', 'e': 's', 'f': 's', 'g': 's', 'a': 's', 'b': 'n'},
    '5s': {'c': 's', 'd': 's', 'e': 'n', 'f': 's', 'g': 's', 'a': 's', 'b': 'n'},
    '7s': {'c': 's', 'd': 's', 'e': 's', 'f': 's', 'g': 's', 'a': 's', 'b': 's'},
}

# See http://music-encoding.org/documentation/3.0.0/data.DURATION.cmn/
DURATIONS = [
    "long", "breve", "1", "2", "4", "8", "16",
    "32", "64", "128", "256", "512", "1024", "2048"
]


def duration(m_thing):
    duration = m_thing.get("dur")
    if duration not in DURATIONS:
        raise exceptions.LycheeMEIError("Unknown duration: '{}'".format(duration))
    negative_log2_duration = DURATIONS.index(duration) - 2
    if negative_log2_duration >= 0:
        duration = fractions.Fraction(1, int(duration))
    else:
        duration = fractions.Fraction(2 ** -negative_log2_duration, 1)

    dots = m_thing.get("dots")
    if dots:
        dots = int(dots)
        duration = duration * fractions.Fraction(2 ** (dots + 1) - 1, 2 ** dots)
    return duration


def measure_duration(m_staffdef):
    numerator = int(m_staffdef.get("meter.count", "4"))
    denominator = int(m_staffdef.get("meter.unit", "4"))
    return fractions.Fraction(numerator, denominator)
