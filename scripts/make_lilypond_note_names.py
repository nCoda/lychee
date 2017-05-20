#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               scripts/make_lilypond_note_names.py
# Purpose:                Generates code for LilyPond note name translation.
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
'''
import argparse
import copy
import sys
import re

re_language_line = re.compile(r'    \((.*) . \($')

scheme_to_mei_accidentals = {
    'DOUBLE-FLAT': 'ff',
    'THREE-Q-FLAT': '3qf',
    'FLAT': 'f',
    'SEMI-FLAT': '1qf',
    'NATURAL': '',
    'SEMI-SHARP': '1qs',
    'SHARP': 's',
    'THREE-Q-SHARP': '3qs',
    'DOUBLE-SHARP': 'x'
    }


pitch_names = ['c', 'd', 'e', 'f', 'g', 'a', 'b']


preamble = """
# -*- coding: utf-8 -*-
'''
Contains dictionaries for translating LilyPond pitch names to
MEI pitch names and back in all languages. This file is generated
by lychee/scripts/make_lilypond_note_names.py.
'''
"""[1:]


def parse_languages(lines):
    inbound_languages = {}
    outbound_languages = {}
    inbound_language = None
    outbound_language = None
    for line in lines:
        line = unicode(line, "utf-8")
        match = re_language_line.match(line)
        if match:
            current_language = match.group(1)
            inbound_language = {}
            inbound_languages[current_language] = inbound_language
            outbound_language = {}
            outbound_languages[current_language] = outbound_language
        elif 'ly:make-pitch' in line:
            split_line = line.split()
            # split_line looks like this:
            # ["(fes", ".", ",(ly:make-pitch", "-1", "3", "FLAT))"]
            lilypond_pitch = split_line[0][1:]
            pitch_name_number = int(split_line[4])
            pitch_name = pitch_names[pitch_name_number]
            accidental = split_line[5][:-2]
            mei_pitch_tuple = pitch_name, scheme_to_mei_accidentals[accidental]
            mei_pitch_string = "".join(mei_pitch_tuple)
            inbound_language[lilypond_pitch] = mei_pitch_tuple
            if (mei_pitch_string not in outbound_language or
                    len(outbound_language[mei_pitch_string]) > len(lilypond_pitch)):
                outbound_language[mei_pitch_string] = lilypond_pitch
    inbound_languages[u"español"] = copy.deepcopy(
        inbound_languages[u"espanol"])
    outbound_languages[u"español"] = copy.deepcopy(
        outbound_languages[u"espanol"])
    return inbound_languages, outbound_languages


def pretty_print(dictionary, stream, indent="    "):
    """
    Pretty print a set of nested dictionaries using Abjad's
    indentation conventions. Everything that isn't a dictionary
    is printed using repr().
    """
    stream.write("{\n")
    for key in sorted(dictionary.keys()):
        value = dictionary[key]
        stream.write("{}{}: ".format(indent, repr(key)))
        if isinstance(value, dict):
            pretty_print(value, stream, indent="    " + indent)
        else:
            stream.write(repr(value))
        stream.write(",\n")
    stream.write(indent + "}")

parser = argparse.ArgumentParser()
parser.add_argument("infile", type=str, help="A copy of scm/define-note-names.scm from the LilyPond source.")
parser.add_argument("outfile", type=str)

args = parser.parse_args()

with open(args.infile, 'r') as input_file:
    with open(args.outfile, 'w') as output_file:
        output_file.write(preamble)

        inbound_languages, outbound_languages = parse_languages(input_file)
        output_file.write("inbound = ")
        pretty_print(inbound_languages, output_file)
        output_file.write("\n\noutbound = ")
        pretty_print(outbound_languages, output_file)
        output_file.write("\n")
