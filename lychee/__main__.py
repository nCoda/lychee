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

from lxml import etree as ETree

from lychee import signals
from signals import outbound

_MEINS = '{http://www.music-encoding.org/ns/mei}'
_MEINS_URL = 'http://www.music-encoding.org/ns/mei'


# register these fake "listeners" that will pretend they want data in whatever formats
def generic_listener(dtype):
    #print("I'm listening for {}!".format(dtype))
    outbound.I_AM_LISTENING.emit(dtype=dtype)

def abj_listener(**kwargs):
    generic_listener('abjad')

def ly_listener(**kwargs):
    generic_listener('lilypond')

def mei_listener(**kwargs):
    generic_listener('mei')

def mei_through_verovio(dtype, placement, document, **kwargs):
    '''
    Outputs a document to a file, then runs Verovio on it. Parameters work as per the
    :const:`outbound.CONVERSION_FINISHED` signal.
    '''

    if 'mei' != dtype:
        return

    # Verovio likes to have the initial clef in the <staffDef> or else it will print a "Verovio
    # default clef," being a G clef on the staff's top line.
    for each_staff in document.find('.//{}staff'.format(_MEINS)):
        first_clef = each_staff.find('.//{}clef'.format(_MEINS))
        staff_def = document.find('.//{}staffDef[@n="{}"]'.format(_MEINS, each_staff.get('n')))
        staff_def.set('clef.shape', first_clef.get('shape'))
        staff_def.set('clef.line', first_clef.get('line'))
        # and remove that <clef> so it won't appear any more
        first_clef.getparent().remove(first_clef)

    # Verovio can only deal with MEI as the default namespace, which "lxml" doesn like to output,
    # so this weird hack removes the MEI namespace prefix from all the tag names.
    output_filename = 'testrepo/mei_for_verovio.xml'
    document.set('xmlns', _MEINS_URL)
    for elem in document.iter():
        elem.tag = elem.tag.replace(_MEINS, '')

    # then we'll just make an ElementTree and output it
    chree = ETree.ElementTree(document)
    chree.write_c14n(output_filename, exclusive=False, inclusive_ns_prefixes=['mei'])
    #chree.write(output_filename, encoding='UTF-8', xml_declaration=True, pretty_print=True)

    # and call Verovio!
    subprocess.call(['verovio', '-f', 'mei', '-o', 'testrepo/verovio_output', output_filename])

#outbound.WHO_IS_LISTENING.connect(abj_listener)
#outbound.WHO_IS_LISTENING.connect(ly_listener)
outbound.WHO_IS_LISTENING.connect(mei_listener)
outbound.CONVERSION_FINISHED.connect(mei_through_verovio)

# this is what starts a test "action"
input_ly = "\clef treble a''4( b'16 c''2)  | \clef \"bass\" d?2 e!2  | f,,2( fis,2)  |"
signals.ACTION_START.emit(dtype='LilyPond', doc=input_ly)
