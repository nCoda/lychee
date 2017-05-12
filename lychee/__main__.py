#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/__main__.py
# Purpose:                Module the runs Lychee as a program.
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
Module that runs Lychee as a program.
'''

import json
import subprocess

import lychee.signals
import lychee.workflow.session
signals = lychee.signals
outbound = lychee.signals.outbound
# NB: it's weird, but this guarantees we won't accidentally reinitialize any of the signals

# test_which_format = 'outbound only'
test_which_format = 'lilypond'
# test_which_format = 'abjad'


session = lychee.workflow.session.InteractiveSession()
session.set_repo_dir('testrepo')


def mei_through_verovio(dtype, placement, document, **kwargs):
    '''
    Outputs a document to a file, then runs Verovio on it. Parameters work as per the
    :const:`outbound.CONVERSION_FINISHED` signal.
    '''

    repodir = session.get_repo_dir()

    if 'verovio' != dtype:
        return

    output_filename = '{}/verovio_input'.format(repodir)

    with open(output_filename, 'w') as the_file:
        the_file.write(document)

    subprocess.call([
        'verovio',
        '--all-pages',
        '-f', 'mei',
        '-o', '{}/verovio_output'.format(repodir),
        output_filename,
        ])


def print_outbound_json(dtype, placement, document, **kwargs):
    '''
    For the outbound data formats that output JSON strings, print them to the console.
    '''
    if dtype == 'document':
        with open('scratch-doc_outbound.json', 'w') as the_file:
            the_file.write(json.dumps(document, sort_keys=True, indent=4, separators=(',', ': ')))
    elif dtype == 'vcs':
        with open('scratch-vcs_outbound.json', 'w') as the_file:
            the_file.write(json.dumps(document, sort_keys=True, indent=4, separators=(',', ': ')))


outbound.REGISTER_FORMAT.emit(dtype='verovio', who='lychee.__main__')
outbound.REGISTER_FORMAT.emit(dtype='vcs', who='lychee.__main__')
outbound.REGISTER_FORMAT.emit(dtype='document', who='lychee.__main__')
outbound.CONVERSION_FINISHED.connect(mei_through_verovio)
outbound.CONVERSION_FINISHED.connect(print_outbound_json)


print('this is the repodir: {}'.format(session.get_repo_dir()))


# this is what starts a test "action"
if 'lilypond' == test_which_format:
    input_ly = """
    \\version "2.18.2"
    \\score {
        <<
            \\new Staff {
                %{ staff 1 %}
                \\set Staff.instrumentName = "Flutes"
                \\clef "treble"
                \\key ees \\major
                %{ m.1 %} %{ l.1 %} r4 <f'' f'''>4 |
                %{ m.2 %} %{ l.1 %} <f'' f'''>2 |
                %{ m.3 %} %{ l.1 %} <f'' f'''>4 <g'' g'''>4 |
                %{ m.4 %} %{ l.1 %} <bes'' bes'''>4 <aes'' aes'''>4 |
                %{ m.5 %} %{ l.1 %} <g'' g'''>4 <f'' f'''>4 |
            }
            \\new Staff {
                %{ staff 2 %}
                \\set Staff.instrumentName = "Oboes"
                \\clef "treble"
                \\key ees \\major
                %{ m.1 %} %{ l.1 %} r4 <f' f''>4 |
                %{ m.2 %} %{ l.1 %} <f' f''>2 |
                %{ m.3 %} %{ l.1 %} <f' f''>4 <g' g''>4 |
                %{ m.4 %} %{ l.1 %} <bes' bes''>4 <aes' aes''>4 |
                %{ m.5 %} %{ l.1 %} <g' g''>4 <f' f''>4 |
            }
            \\new Staff {
                %{ staff 3 %}
                \\set Staff.instrumentName = "Clarinets"
                \\clef "treble"
                \\key f \\major
                %{ m.1 %} %{ l.1 %} r4 g''4 |
                %{ m.2 %} %{ l.1 %} g''2 |
                %{ m.3 %} %{ l.1 %} g''4 a''4 |
                %{ m.4 %} %{ l.1 %} c'''4 bes''4 |
                %{ m.5 %} %{ l.1 %} a''4 g''4 |
            }
            \\new Staff {
                %{ staff 4 %}
                \\set Staff.instrumentName = "Bassoons"
                \\clef "bass"
                \\key ees \\major
                %{ m.1 %} %{ l.1 %} bes,2 |
                %{ m.2 %} %{ l.1 %} bes,2 |
                %{ m.3 %} %{ l.1 %} bes,4 r8 |
                %{ m.4 %} %{ l.1 %} d,2 |
                %{ m.5 %} %{ l.1 %} d,2 |
            }
            \\new Staff {
                %{ staff 5 %}
                \\set Staff.instrumentName = "Horns 1 & 3"
                \\clef "treble"
                %{ m.1 %} << { %{ l.1 %} bes'!2 } \\\\ { %{ l.2 %} g'2 } >> |
                %{ m.2 %} << { %{ l.1 %} f''2 } \\\\ { %{ l.2 %} d''2 } >> |
                %{ m.3 %} << { %{ l.1 %} bes'!2 } \\\\ { %{ l.2 %} g'2 } >> |
                %{ m.4 %} << { %{ l.1 %} a'2 } \\\\ { %{ l.2 %} f'2 } >> |
                %{ m.5 %} << { %{ l.1 %} r2 } \\\\ { %{ l.2 %} r2 } >> |
            }
            \\new Staff {
                %{ staff 6 %}
                \\set Staff.instrumentName = "Horns 2 & 4"
                \\clef "treble"
                %{ m.1 %} << { %{ l.1 %} bes'!2 } \\\\ { %{ l.2 %} g'2 } >> |
                %{ m.2 %} << { %{ l.1 %} r2 } \\\\ { %{ l.2 %} r2 } >> |
                %{ m.3 %} << { %{ l.1 %} r2 } \\\\ { %{ l.2 %} r2 } >> |
                %{ m.4 %} << { %{ l.1 %} a'2 } \\\\ { %{ l.2 %} f'2 } >> |
                %{ m.5 %} << { %{ l.1 %} f''2 } \\\\ { %{ l.2 %} d''2 } >> |
            }
            \\new Staff {
                %{ staff 7 %}
                \\set Staff.instrumentName = "Violin I"
                \\clef "treble"
                \\key ees \\major
                %{ m.1 %} << { %{ l.1 %} ees'2 } \\\\ { %{ l.2 %} c'2 } >> |
                %{ m.2 %} << { %{ l.1 %} ees'2 } \\\\ { %{ l.2 %} c'2 } >> |
                %{ m.3 %} << { %{ l.1 %} ees'2 } \\\\ { %{ l.2 %} c'2 } >> |
                %{ m.4 %} << { %{ l.1 %} bes'2 } \\\\ { %{ l.2 %} g'2 } >> |
                %{ m.5 %} << { %{ l.1 %} bes'2 } \\\\ { %{ l.2 %} g'2 } >> |
            }
            \\new Staff {
                %{ staff 8 %}
                \\set Staff.instrumentName = "Violin II"
                \\clef "treble"
                \\key ees \\major
                %{ m.1 %} << { %{ l.1 %} ees'2 } \\\\ { %{ l.2 %} c'2 } >> |
                %{ m.2 %} << { %{ l.1 %} bes'2 } \\\\ { %{ l.2 %} g'2 } >> |
                %{ m.3 %} << { %{ l.1 %} bes'2 } \\\\ { %{ l.2 %} g'2 } >> |
                %{ m.4 %} << { %{ l.1 %} d'2 } \\\\ { %{ l.2 %} bes2 } >> |
                %{ m.5 %} << { %{ l.1 %} d'2 } \\\\ { %{ l.2 %} bes2 } >> |
            }
            \\new Staff {
                %{ staff 9 %}
                \\set Staff.instrumentName = "Viola"
                \\clef "alto"
                \\key ees \\major
                %{ m.1 %} << { %{ l.1 %} bes'2 } \\\\ { %{ l.2 %} g'2 } >> |
                %{ m.2 %} << { %{ l.1 %} bes'2 } \\\\ { %{ l.2 %} g'2 } >> |
                %{ m.3 %} << { %{ l.1 %} ees'2 } \\\\ { %{ l.2 %} c'2 } >> |
                %{ m.4 %} << { %{ l.1 %} bes'2 } \\\\ { %{ l.2 %} d'2 } >> |
                %{ m.5 %} << { %{ l.1 %} bes'2 } \\\\ { %{ l.2 %} d'2 } >> |
            }
            \\new Staff {
                %{ staff 10 %}
                \\set Staff.instrumentName = "Cello"
                \\clef "tenor"
                \\key ees \\major
                %{ m.1 %} %{ l.1 %} r4 f'4 |
                %{ m.2 %} %{ l.1 %} f'2 |
                %{ m.3 %} %{ l.1 %} f'4 g'4 |
                %{ m.4 %} %{ l.1 %} bes'4 aes'4 |
                %{ m.5 %} %{ l.1 %} g'4 f'4 |
            }
            \\new Staff {
                %{ staff 5 %}
                \\set Staff.instrumentName = "Double Bass"
                \\clef "bass"
                \\key ees \\major
                %{ m.1 %} << { %{ l.1 %} bes'!2 } \\\\ { %{ l.2 %} g'2 } >> |
                %{ m.2 %} << { %{ l.1 %} f''2 } \\\\ { %{ l.2 %} d''2 } >> |
                %{ m.3 %} << { %{ l.1 %} bes'!2 } \\\\ { %{ l.2 %} g'2 } >> |
                %{ m.4 %} << { %{ l.1 %} a'2 } \\\\ { %{ l.2 %} f'2 } >> |
                %{ m.5 %} << { %{ l.1 %} r2 } \\\\ { %{ l.2 %} r2 } >> |
            }
        >>
        \\layout { }
    }
    """
    session.run_workflow(dtype='LilyPond', doc=input_ly, sect_id='Sme-s-m-l-e5811068')
elif 'abjad' == test_which_format:
    print('(starting to make Abjad score)')
    from abjad import *
    # Sibelius' 7th symphony, pg.5 m.6 through B
    violins_1_1 = Staff([
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r2 e'' b''"),
        Measure((3, 2), "c'''4 d''' b'' g'' a''4. b''8"), Measure((2, 2), "b''2 c'''"),
    ])
    attach(Clef('treble'), violins_1_1)
    violins_1_2 = Staff([
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r2 e' b'"),
        Measure((3, 2), "c''4 d'' b' g' a'4. b'8"), Measure((2, 2), "b'2 c''"),
    ])
    attach(Clef('treble'), violins_1_2)

    violins_2_1 = Staff([
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r2 d''2 a''"),
        Measure((3, 2), "a''1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r4 g'' d'' e'' f''4. f''8"), Measure((2, 2), "f''2 e''"),
    ])
    attach(Clef('treble'), violins_2_1)
    violins_2_2 = Staff([
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r2 d'2 a'"),
        Measure((3, 2), "a'1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r4 g' d' e' f'4. f'8"), Measure((2, 2), "f'2 e'"),
    ])
    attach(Clef('treble'), violins_2_2)

    alti_1 = Staff([
        Measure((3, 2), "r2 g' a'"), Measure((3, 2), "b'2. a'4 b'2"),
        Measure((3, 2), "c''2 d'' a'"), Measure((3, 2), "b'2 d'' g''"),
        Measure((3, 2), "d''1."), Measure((3, 2), "c''1 d''4 c''"),
        Measure((3, 2), "b'2. c''2 f''4"), Measure((3, 2), "g''1 g'2"),
        Measure((3, 2), "g'4 a' bf'2 a'4 g'"), Measure((3, 2), "a'1 a'2"),
        Measure((3, 2), "a'4 b' c''2 b'4 a'"), Measure((3, 2), "b'1 b'2"),
        Measure((3, 2), "c''4 b' g' g' f' g'"), Measure((2, 2), "a'1"),
    ])
    attach(Clef('alto'), alti_1)
    alti_2 = Staff([
        Measure((3, 2), "r2 g g"), Measure((3, 2), "f1."),
        Measure((3, 2), "g2 a fs"), Measure((3, 2), "g2 b1"),
        Measure((3, 2), "b1 b2"), Measure((3, 2), "c'2. g"),
        Measure((3, 2), "g4 g2 g a4"), Measure((3, 2), "a4 b c' d' ef'2"),
        Measure((3, 2), "ef'1 f'4 ef'4"), Measure((3, 2), "d'4 d'2 d' d'4"),
        Measure((3, 2), "f'1 g'4 f'"), Measure((3, 2), "e'4 fs'4 g'2 fs'4 e'"),
        Measure((3, 2), "c'4 b a a g a"), Measure((2, 2), "a1"),
    ])
    attach(Clef('alto'), alti_2)

    celli_1 = Staff([
        Measure((3, 2), "r2 b2 c'2"), Measure((3, 2), "d'1."),
        Measure((3, 2), "e'2 fs'2 c'2"), Measure((3, 2), "g'2 a'1"),
        Measure((3, 2), "a'1 g'4.( a'8)"), Measure((3, 2), "g'2( c'2) c'2"),
        Measure((3, 2), "f'1( e'4) c'4"), Measure((3, 2), "c'4 d' ef' g' bf2"),
        Measure((3, 2), "bf2. bf"), Measure((3, 2), "a2 d a"),  # TODO: bass clef start of 2nd measure here
        Measure((3, 2), "a4 b c'2 b4 a"), Measure((3, 2), "b2 e b"),
        Measure((3, 2), "a4 g f e d d'"), Measure((2, 2), "d'4 c' b a g"),
    ])
    attach(Clef('tenor'), celli_1)
    celli_2 = Staff([
        Measure((3, 2), "r2 f2 e2"), Measure((3, 2), "d2 g2 d2"),
        Measure((3, 2), "c1 b,4 a,4"), Measure((3, 2), "g4 f1"),
        Measure((3, 2), "f2 g2 f2"), Measure((3, 2), "e2 f2 e2"),
        Measure((3, 2), "d2. c4 c4 a4"), Measure((3, 2), "g4 f ef2 ef"),
        Measure((3, 2), "ef1 f4 ef"), Measure((3, 2), "d4 d2 d d4"),
        Measure((3, 2), "f1 g4 f"), Measure((3, 2), "e4 f g2 f4 e"),
        Measure((3, 2), "a4 g f e d d"), Measure((2, 2), "d4 c b, a, g,"),  # TODO: tuplet at end
    ])
    attach(Clef('bass'), celli_2)

    bassi = Staff([
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r1."), Measure((3, 2), "r1."),
        Measure((3, 2), "r4 d'2 c'4 c' a"), Measure((3, 2), "g4 f ef2 ef"),
        Measure((3, 2), "ef4 f g2 f4 ef"), Measure((3, 2), "f4 f2 f f4"),
        Measure((3, 2), "f4 g a2 a"), Measure((3, 2), "g4 a b2 a4 g"),
        Measure((3, 2), "a4 g f e d2"), Measure((2, 2), "d4 r r2"),
    ])
    attach(Clef('bass'), bassi)

    score = Score([violins_1_1, violins_1_2, violins_2_1, violins_2_2, alti_1, alti_2, celli_1, celli_2, bassi])
    print('(finished making Abjad score)')
    session.run_workflow(dtype='abjad', doc=score, sect_id='Sme-s-m-l-e8151068')
elif 'outbound only' == test_which_format:
    session.run_outbound()
else:
    raise RuntimeError('you must choose a format in lychee.__main__')


# be sure to clean up!
session.unset_repo_dir()
