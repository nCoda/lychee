#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/__init__.py
# Purpose:                Initialization for converters module.
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
Initialization for :mod:`converters` module.
'''

# Jeff: "Well, a universal converter is, by definition, a pretty slutty thing."

__all__ = ['mei_to_ly', 'ly_to_mei', 'lmei_to_abjad', 'abjad_to_lmei', 'mei_to_lmei', 'lmei_to_mei',
    'lmei_to_verovio', 'registrar', 'vcs_outbound', 'document_outbound']

from lychee.converters import *


# NOTE: please keep the keys in lowercase
INBOUND_CONVERTERS = {'lilypond': ly_to_mei.convert,
                      'abjad': abjad_to_lmei.convert,
                      'mei': mei_to_lmei.convert
                     }
'''
Mapping from the lowercase name of an inbound converter format to the :func:`convert` function that
converts from that format to Lychee-MEI.
'''

# NOTE: please keep the keys in lowercase
OUTBOUND_CONVERTERS = {'lilypond': mei_to_ly.convert,
                       'abjad': lmei_to_abjad.convert,
                       'mei': lmei_to_mei.convert,
                       'verovio': lmei_to_verovio.convert,
                       'vcs': vcs_outbound.convert,
                       'document': document_outbound.convert,
                      }
'''
Mapping from the lowercase name of an outbound converter format to the :func:`convert` function that
converts from Lychee-MEI into hat format.
'''
