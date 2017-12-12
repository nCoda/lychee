#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/__init__.py
# Purpose:                Initialization for converters module.
#
# Copyright (C) 2016, 2017 Christopher Antila
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
.. note:: The dictionaries may be changed before version 1.0.
'''

# Jeff: "Well, a universal converter is, by definition, a pretty slutty thing."

from lychee.converters import inbound, outbound


# NOTE: please keep the keys in lowercase
INBOUND_CONVERTERS = {'lilypond': inbound.lilypond.convert,
                      'abjad': inbound.abjad.convert,
                      'mei': inbound.mei.convert
                     }
'''
Mapping from the lowercase name of an inbound converter format to the :func:`convert` function that
converts from that format to Lychee-MEI.
'''

# NOTE: please keep the keys in lowercase
OUTBOUND_CONVERTERS = {'abjad': outbound.abjad.convert,
                       'document': outbound.document.convert,
                       'lilypond': outbound.lilypond.convert,
                       'mei': outbound.mei.convert,
                       'python': outbound.python.convert,
                       'vcs': outbound.vcs.convert,
                       'verovio': outbound.verovio.convert,
                      }
'''
Mapping from the lowercase name of an outbound converter format to the :func:`convert` function that
converts from Lychee-MEI into hat format.
'''
