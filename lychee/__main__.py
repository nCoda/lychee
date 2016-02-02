#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/__main__.py
# Purpose:                Module the runs Lychee as a program.
#
# Copyright (C) 2015 Christopher Antila
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

import subprocess

import lychee
signals = lychee.signals
outbound = lychee.signals.outbound
# NB: it's weird, but this guarantees we won't accidentally reinitialize any of the signals

# test_which_format = 'outbound only'
test_which_format = 'lilypond'
# test_which_format = 'abjad'


def mei_through_verovio(dtype, placement, document, **kwargs):
    '''
    Outputs a document to a file, then runs Verovio on it. Parameters work as per the
    :const:`outbound.CONVERSION_FINISHED` signal.
    '''

    if 'verovio' != dtype:
        return

    output_filename = 'testrepo/verovio_input'

    with open(output_filename, 'w') as the_file:
        the_file.write(document)

    subprocess.call(['verovio', '-f', 'mei', '-o', 'testrepo/verovio_output', output_filename])


outbound.REGISTER_FORMAT.emit(dtype='verovio', who='lychee.__main__')
outbound.CONVERSION_FINISHED.connect(mei_through_verovio)


# this is what starts a test "action"
if 'lilypond' == test_which_format:
    input_ly = "\clef treble a''4( b'16 c''2)  | \clef \"bass\" d?2 e!2  | f,,2( fis,2)  |"
    signals.ACTION_START.emit(dtype='LilyPond', doc=input_ly)
elif 'abjad' == test_which_format:
    from abjad import *
    s = Voice("a''4 r4 <a'' b''> b'' a''4. r4.")
    a = Voice("d' d' d' d' d' cs' d' d'")
    top = Staff([s, a])
    top.is_simultaneous = True
    t = Voice("fs''  fs''8 g'' a''4  g''8 fs''  e'' d'' e''4  d'' d''")
    b = Voice("d'4 b' fs' g' a' a' d' d'")
    bottom = Staff([t,b])
    bottom.is_simultaneous = True
    group = StaffGroup([top,bottom])
    tuba = Staff("c''''1 r c''''")
    score = Score([group,tuba])
    signals.ACTION_START.emit(dtype='abjad', doc=score)
elif 'outbound only' == test_which_format:
    signals.ACTION_START.emit()
else:
    raise RuntimeError('you must choose a format in lychee.__main__')
