#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/lilypond_pitch_names.py
# Purpose:                b;a
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
from lychee import exceptions
from collections import OrderedDict

B_FLAT_INDEX = 6

# for pitch class conversion, start with lists of ordered tuples
dutch_pitch_tuples = [('c', 'c'), ('d', 'd'), ('e', 'e'), ('f', 'f'), ('g', 'g'), ('a', 'a'), ('bes', 'bf'), ('b', 'b')]
german_pitch_tuples = [('c', 'c'), ('d', 'd'), ('e', 'e'), ('f', 'f'), ('g', 'g'), ('a', 'a'), ('h', 'bf'), ('b', 'b')]
english_pitch_tuples = [('c', 'c'), ('d', 'd'), ('e', 'e'), ('f', 'f'), ('g', 'g'), ('a', 'a'), ('bf', 'bf'), ('b', 'b')]
romance_pitch_tuples = [('do', 'c'), ('re', 'd'), ('mi', 'e'), ('fa', 'f'), ('sol', 'g'), ('la', 'a'), ('sib', 'bf'), ('si', 'b')]

# convert ordered tuples to a dictionary of OrderedDicts
# (so we can keep track of pesky old B-flat in the penultimate spot)
pitch_name_dicts = {
    'nederlands': OrderedDict(dutch_pitch_tuples),
    'catalan': OrderedDict(romance_pitch_tuples),
    'deutsch': OrderedDict(german_pitch_tuples),
    'english': OrderedDict(english_pitch_tuples),
    'espanol': OrderedDict(romance_pitch_tuples),
    'español': OrderedDict(romance_pitch_tuples),
    'italiano': OrderedDict(romance_pitch_tuples),
    'français': OrderedDict(romance_pitch_tuples),
    'norsk': OrderedDict(german_pitch_tuples),
    'portugues': OrderedDict(romance_pitch_tuples),
    'suomi': OrderedDict(german_pitch_tuples),
    'svenska': OrderedDict(german_pitch_tuples),
    'vlaams': OrderedDict(romance_pitch_tuples),
    }

# make a dictionary of (unordered) accidental dictionaries
catalan_accid_dict = {'d': 's', 's': 's', 'b': 'b', 'dd': 'ss', 'ss': 'ss', 'bb': 'bb', '': ''}
dutch_accid_dict = finnish_accid_dict = german_accid_dict = {'es': 'f', 'is': 's', 'eses': 'ff', 'isis': 'ss', '': ''}
english_accid_dict = {'f': 'f', 's': 's', 'ff': 'ff', 'ss': 'ss', 'x': 'ss', '': ''}
spanish_accid_dict = {'s': 's', 'b': 'f', 'ss': 'ss', 'x': 'ss', 'bb': 'ff'}
italian_accid_dict = french_accid_dict = {'d': 's', 'b': 'b', 'dd': 'ss', 'bb': 'bb', '': ''}
norwegian_accid_dict = {'iss': 's', 'is': 's', 'ess': 'f', 'es': 'f', 'ississ': 'ss', 'isis': 'ss', 'essess': 'ff', 'eses': 'ff', '': ''}
portuguese_accid_dict = {'s': 's', 'b': 'b', 'ss': 'ss', 'bb': 'bb', '': ''}
swedish_accid_dict = {'iss': 's', 'es': 'f', 'isis': 'ss', 'eses': 'ff', '': ''}
flemish_accid_dict = {'k': 's', 'b': 'b', 'kk': 'ss', 'bb': 'bb', '': ''}
accidentals_dicts = {
    'nederlands': dutch_accid_dict,
    'catalan': catalan_accid_dict,
    'deutsch': german_accid_dict,
    'english': english_accid_dict,
    'espanol': spanish_accid_dict,
    'español': spanish_accid_dict,
    'italiano': italian_accid_dict,
    'français': french_accid_dict,
    'norsk': norwegian_accid_dict,
    'portugues': portuguese_accid_dict,
    'suomi': finnish_accid_dict,
    'svenska': swedish_accid_dict,
    'vlaams': flemish_accid_dict,
    }


def parse_pitch_name(pitch_name, language="nederlands"):
    if language not in pitch_name_dicts:
        raise exceptions.LilyPondError("Unrecognized language: '{}'".format(language))

    pitch_name_dict = pitch_name_dicts[language]
    accidentals_dict = accidentals_dicts[language]

    if pitch_name in pitch_name_dict.items()[B_FLAT_INDEX]:
        return ("b", "f")
    else:
        counter = 0
        comparator = pitch_name[:counter]
        while comparator not in pitch_name_dict:
            counter += 1
            comparator = pitch_name[:counter]
        pitch_name_string = pitch_name[:counter]
        accidental_string = pitch_name[counter:]

        try:
            pitch_pair = (pitch_name_dict[pitch_name_string], accidentals_dict[accidental_string])
        except KeyError:
            raise exceptions.LilyPondError("Pitch name '{}' is not valid in language '{}'"
                    .format(pitch_name, language))
        return pitch_pair
