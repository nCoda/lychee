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
from lychee.namespaces import mei, xml
import fractions


class TestKeySignatures:

    def test_key_signatures(self):
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


class TestDuration:

    def test_duration_1(self):
        '''Quarter note.'''
        thing = {'dur': '4'}
        expected = fractions.Fraction(1, 4)
        actual = music_utils.duration(thing)
        assert expected == actual

    def test_duration_2(self):
        '''Double dotted breve.'''
        thing = {'dur': 'breve', 'dots': 2}
        expected = fractions.Fraction(7, 2)
        actual = music_utils.duration(thing)
        assert expected == actual

    def test_duration_3(self):
        '''Triple-dotted sixteenth note.'''
        thing = {'dur': '16', 'dots': 3}
        expected = fractions.Fraction(15, 128)
        actual = music_utils.duration(thing)
        assert expected == actual


class TestTimeSignature:

    def test_time_signature_1(self):
        '''5/8.'''
        attrib = {'meter.count': '5', 'meter.unit': '8'}
        expected = (5, 8)
        actual = music_utils.time_signature(attrib)
        assert expected == actual

    def test_time_signature_2(self):
        '''3/4, but the unit is omitted.'''
        attrib = {'meter.count': '3'}
        expected = (3, 4)
        actual = music_utils.time_signature(attrib)
        assert expected == actual

    def test_time_signature_3(self):
        '''4/3, but the count is omitted.'''
        attrib = {'meter.unit': '3'}
        expected = (4, 3)
        actual = music_utils.time_signature(attrib)
        assert expected == actual


class TestMeasureDuration:

    def test_measure_duration(self):
        attrib = {'meter.count': '7', 'meter.unit': '8'}
        expected = fractions.Fraction(7, 8)
        actual = music_utils.measure_duration(attrib)
        assert expected == actual


class TestGetAutobeamStructure:

    def test_basic(self):
        '''2/4, four eighth notes.'''
        layer = etree.fromstring('''
            <mei:layer xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:note dur="8"/>
                <mei:note dur="8"/>
                <mei:note dur="8"/>
                <mei:note dur="8"/>
            </mei:layer>
            ''')
        staffdef = {'meter.count': '3', 'meter.unit': '4'}

        expected = [[layer[0], layer[1]], [layer[2], layer[3]]]
        actual = music_utils.get_autobeam_structure(layer, staffdef)
        assert expected == actual

    def test_triple_time(self):
        '''Triple time beams groups of 3.'''
        layer = etree.fromstring('''
            <mei:layer xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:note dur="8"/>
                <mei:note dur="8"/>
                <mei:note dur="8"/>
                <mei:note dur="8"/>
                <mei:note dur="8"/>
                <mei:note dur="8"/>
            </mei:layer>
            ''')
        staffdef = {'meter.count': '6', 'meter.unit': '8'}

        expected = [[layer[0], layer[1], layer[2]], [layer[3], layer[4], layer[5]]]
        actual = music_utils.get_autobeam_structure(layer, staffdef)
        assert expected == actual

    def test_chord(self):
        '''2/4, two eighth notes, one is a chord.'''
        layer = etree.fromstring('''
            <mei:layer xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:note dur="8"/>
                <mei:chord dur="8"/>
            </mei:layer>
            ''')
        staffdef = {'meter.count': '3', 'meter.unit': '4'}

        expected = [[layer[0], layer[1]]]
        actual = music_utils.get_autobeam_structure(layer, staffdef)
        assert expected == actual

    def test_nonbreaking_element(self):
        '''Elements other than rests and notes don't break beams.'''
        layer = etree.fromstring('''
            <mei:layer xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:note dur="8"/>
                <mei:staffDef n="3" clef.shape="F" clef.line="4"/>
                <mei:note dur="8"/>
            </mei:layer>
            ''')
        staffdef = {'n': '3', 'meter.count': '2', 'meter.unit': '4'}

        expected = [[layer[0], layer[2]]]
        actual = music_utils.get_autobeam_structure(layer, staffdef)
        assert expected == actual

    def test_quarter_note(self):
        '''Quarter notes don't form beams.'''
        layer = etree.fromstring('''
            <mei:layer xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:note dur="8"/>
                <mei:note dur="4"/>
                <mei:note dur="8"/>
            </mei:layer>
            ''')
        staffdef = {'meter.count': '2', 'meter.unit': '4'}

        expected = []
        actual = music_utils.get_autobeam_structure(layer, staffdef)
        assert expected == actual

    def test_rest(self):
        '''Rests break beams.'''
        layer = etree.fromstring('''
            <mei:layer xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:note dur="8"/>
                <mei:rest dur="8"/>
                <mei:note dur="8"/>
            </mei:layer>
            ''')
        staffdef = {'meter.count': '3', 'meter.unit': '8'}

        expected = []
        actual = music_utils.get_autobeam_structure(layer, staffdef)
        assert expected == actual


class TestAutoBeam:

    def test_make_beam(self):
        '''Three notes get beamed together.'''
        layer = etree.fromstring('''
            <mei:layer xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:note/>
                <mei:note/>
                <mei:note/>
            </mei:layer>
            ''')

        notes = layer.findall(mei.NOTE)
        music_utils.make_beam(notes, layer)

        # It assigns xml IDs to all notes.
        for note in notes:
            assert xml.ID in note.attrib

        xml_ids = [note.get(xml.ID) for note in notes]

        beam_span = layer.find(mei.BEAM_SPAN)
        assert beam_span is not None

        assert layer[:] == notes + [beam_span]

        assert beam_span.get('startid') == '#' + xml_ids[0]
        assert beam_span.get('endid') == '#' + xml_ids[-1]
        assert beam_span.get('plist') == ' '.join(['#' + x for x in xml_ids])

    def test_make_beam_one_note(self):
        '''One note does nothing.'''
        layer = etree.fromstring('''
            <mei:layer xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:note/>
            </mei:layer>
            ''')

        notes = layer.findall(mei.NOTE)
        music_utils.make_beam(notes, layer)

        assert layer[:] == notes

    def test_autobeam(self):
        '''Integration test of autobeam.'''
        layer = etree.fromstring('''
            <mei:layer xmlns:mei="http://www.music-encoding.org/ns/mei">
                <mei:note dur="8"/>
                <mei:note dur="8"/>
                <mei:note dur="8"/>
                <mei:note dur="8"/>
                <mei:note dur="8"/>
                <mei:note dur="8"/>
            </mei:layer>
            ''')
        staffdef = {'meter.count': '6', 'meter.unit': '8'}

        music_utils.autobeam(layer, staffdef)

        assert len(layer) == 8

        expected_tags = [
            mei.NOTE,
            mei.NOTE,
            mei.NOTE,
            mei.BEAM_SPAN,
            mei.NOTE,
            mei.NOTE,
            mei.NOTE,
            mei.BEAM_SPAN,
            ]
        assert [element.tag for element in layer] == expected_tags

        beam_span_1 = layer[3]
        assert beam_span_1.get('startid') == '#' + layer[0].get(xml.ID)
        assert beam_span_1.get('endid') == '#' + layer[2].get(xml.ID)

        plist_1 = ['#' + element.get(xml.ID) for element in layer[0:3]]
        assert beam_span_1.get('plist').split() == plist_1

        beam_span_2 = layer[7]
        assert beam_span_2.get('startid') == '#' + layer[4].get(xml.ID)
        assert beam_span_2.get('endid') == '#' + layer[6].get(xml.ID)

        plist_2 = ['#' + element.get(xml.ID) for element in layer[4:7]]
        assert beam_span_2.get('plist').split() == plist_2
