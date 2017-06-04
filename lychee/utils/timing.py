#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/utils/timing.py
# Purpose:                MEI timing utility functions
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
Contains utilities for MEI timing.
'''
from lychee import exceptions
import fractions

# See http://music-encoding.org/documentation/3.0.0/data.DURATION.cmn/
DURATIONS = [
    "long", "breve", "1", "2", "4", "8", "16",
    "32", "64", "128", "256", "512", "1024", "2048"
]


def duration(m_thing):
    duration = m_thing.get("dur", None)
    if duration not in DURATIONS:
        raise exceptions.LycheeMEIError("Unknown duration: '{}'".format(duration))
    negative_log2_duration = DURATIONS.index(duration) - 2
    if negative_log2_duration >= 0:
        duration = fractions.Fraction(1, int(duration))
    else:
        duration = fractions.Fraction(2 ** -negative_log2_duration, 1)

    dots = m_thing.get("dots", None)
    if dots:
        dots = int(dots)
        duration = duration * fractions.Fraction(2 ** (dots + 1) - 1, 2 ** dots)
    return duration
