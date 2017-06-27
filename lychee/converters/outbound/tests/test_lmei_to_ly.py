#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/test/test_lilypond.py
# Purpose:                Converts an MEI document to a LilyPond document.
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
Tests for converting an MEI document to a LilyPond document.
'''

from lxml import etree

import pytest

from lychee.converters.outbound import lilypond
from lychee import exceptions
from lychee.namespaces import mei


def container(tag, children, **attributes):
    '''
    Helper function for convenient one-liner creation of XML containers.
    '''
    element = etree.Element(tag, attributes)
    element.extend(children)
    return element


class TestConvert(object):
    def test_convert_1(self):
        mei_thing = etree.fromstring(
            '<mei:note dur="4" oct="4" pname="d" xmlns:mei="http://www.music-encoding.org/ns/mei"/>')
        assert type(lilypond.convert(mei_thing)) == unicode

    def test_convert_2(self):
        mei_thing = etree.fromstring('<mei:joke xmlns:mei="http://www.music-encoding.org/ns/mei"/>')
        with pytest.raises(exceptions.OutboundConversionError):
            lilypond.convert(mei_thing)


class TestDuration(object):
    def test_duration_1(self):
        m_note = etree.Element(mei.NOTE)
        assert lilypond.duration(m_note) == ""

    def test_duration_2(self):
        m_note = etree.Element(mei.NOTE)
        m_note.set("dur", "2")
        m_note.set("dots", "2")
        assert lilypond.duration(m_note) == "2.."

    def test_duration_3(self):
        m_note = etree.Element(mei.NOTE)
        m_note.set("dur", "16")
        assert lilypond.duration(m_note) == "16"

    def test_duration_4(self):
        m_note = etree.Element(mei.NOTE)
        m_note.set("dots", "2")
        assert lilypond.duration(m_note) == "4.."


class TestNoteRest(object):
    def test_note_1(self):
        m_note = etree.Element(mei.NOTE)
        m_note.set('pname', 'e')
        m_note.set('oct', '6')
        m_note.set('dur', '2')
        m_accid = etree.SubElement(m_note, mei.ACCID)
        m_accid.set('accid', 'f')
        assert lilypond.note(m_note) == "es'''2"

    def test_note_2(self):
        m_note = etree.Element(mei.NOTE)
        m_note.set('pname', 'e')
        m_note.set('oct', '2')
        assert lilypond.note(m_note) == "e,"

    def test_note_language(self):
        m_note = etree.Element(mei.NOTE)
        m_note.set('pname', 'g')
        m_note.set('oct', '4')
        m_note.set('dur', '4')
        m_accid = etree.SubElement(m_note, mei.ACCID)
        m_accid.set('accid', 's')
        context = {'language': 'italiano'}
        assert lilypond.note(m_note, context) == "sold'4"

    def test_rest_1(self):
        m_rest = etree.Element(mei.REST)
        m_rest.set('dur', '32')
        assert lilypond.rest(m_rest) == "r32"

    def test_rest_2(self):
        m_rest = etree.Element(mei.REST)
        assert lilypond.rest(m_rest) == "r"

    def test_measure_rest_1(self):
        m_measure_rest = etree.Element(mei.M_REST)
        m_measure_rest.set('dur', '32')
        assert lilypond.measure_rest(m_measure_rest) == 'R32'

    def test_measure_rest_2(self):
        m_measure_rest = etree.Element(mei.M_REST)
        assert lilypond.measure_rest(m_measure_rest) == 'R'


class TestTie(object):
    def test_tie_1(self):
        '''
        A tie between two notes.
        '''
        m_notes = [
            etree.Element(mei.NOTE, pname='c', oct='3', tie='i'),
            etree.Element(mei.NOTE, pname='c', oct='3', tie='t'),
            ]
        m_layer = container(mei.LAYER, m_notes, n='1')
        assert lilypond.layer(m_layer) == '%{ l.1 %} c~ c'

    def test_tie_2(self):
        '''
        A three-note tie.
        '''
        m_notes = [
            etree.Element(mei.NOTE, pname='c', oct='3', tie='i'),
            etree.Element(mei.NOTE, pname='c', oct='3', tie='m'),
            etree.Element(mei.NOTE, pname='c', oct='3', tie='t'),
            ]
        m_layer = container(mei.LAYER, m_notes, n='1')
        assert lilypond.layer(m_layer) == '%{ l.1 %} c~ c~ c'

    def test_tie_3(self):
        '''
        A tie between chords.
        '''
        m_chord_1 = container(
            mei.CHORD,
            [
                etree.Element(mei.NOTE, pname='c', oct='3'),
                etree.Element(mei.NOTE, pname='g', oct='3'),
                ],
            tie='i',
            )
        m_chord_2 = container(
            mei.CHORD,
            [
                etree.Element(mei.NOTE, pname='c', oct='3'),
                etree.Element(mei.NOTE, pname='g', oct='3'),
                ],
            tie='t',
            )
        m_layer = container(mei.LAYER, [m_chord_1, m_chord_2], n='1')
        assert lilypond.layer(m_layer) == '%{ l.1 %} <c g>~ <c g>'

    def test_tie_3(self):
        '''
        A tie between two notes in different chords.
        '''
        m_chord_1 = container(
            mei.CHORD,
            [
                etree.Element(mei.NOTE, pname='c', oct='3', tie='i'),
                etree.Element(mei.NOTE, pname='g', oct='3'),
                ],
            )
        m_chord_2 = container(
            mei.CHORD,
            [
                etree.Element(mei.NOTE, pname='c', oct='3', tie='t'),
                etree.Element(mei.NOTE, pname='g', oct='3'),
                ],
            )
        m_layer = container(mei.LAYER, [m_chord_1, m_chord_2], n='1')
        assert lilypond.layer(m_layer) == '%{ l.1 %} <c~ g> <c g>'


class TestSlur(object):
    def test_slur_1(self):
        '''
        Four notes slurred.
        '''
        m_layer = etree.fromstring(
        '''<mei:layer n="1" xmlns:mei="http://www.music-encoding.org/ns/mei">
            <mei:note dur="4" oct="3" pname="c" slur="i1" />
            <mei:note dur="4" oct="3" pname="d" slur="m1" />
            <mei:note dur="4" oct="3" pname="e" slur="m1" />
            <mei:note dur="4" oct="3" pname="f" slur="t1" />
        </mei:layer>''')
        assert lilypond.layer(m_layer) == '%{ l.1 %} c4( d4 e4 f4)'


class TestLayerMeasure(object):
    def test_layer_1(self):
        m_layer = etree.fromstring(
        '''<mei:layer n="22" xmlns:mei="http://www.music-encoding.org/ns/mei">
            <mei:note dur="4" oct="4" pname="d"/>
            <mei:note dur="4" oct="3" pname="d"/>
            <mei:note dur="4" oct="3" pname="e"/>
            <mei:note dur="4" oct="3" pname="f"/>
            <mei:note dur="4" oct="3" pname="g"/>
            <mei:note dur="4" oct="3" pname="b"/>
        </mei:layer>''')
        expected = "%{ l.22 %} d'4 d4 e4 f4 g4 b4"
        assert lilypond.layer(m_layer) == expected

    def test_layer_2(self):
        m_layer = etree.fromstring('<mei:layer n="1" xmlns:mei="http://www.music-encoding.org/ns/mei"/>')
        expected = '%{ l.1 %}'
        assert lilypond.layer(m_layer) == expected

    def test_measure_0(self):
        "No layers."
        m_measure = etree.fromstring(
        '''<mei:measure n="5" xmlns:mei="http://www.music-encoding.org/ns/mei">
        </mei:measure>''')
        expected = "%{ m.5 %} |\n"
        assert lilypond.measure(m_measure) == expected

    def test_measure_1(self):
        "One layer."
        m_measure = etree.fromstring(
        '''<mei:measure n="5" xmlns:mei="http://www.music-encoding.org/ns/mei">
            <mei:layer n="1">
                <mei:note dur="2" oct="4" pname="d"/>
                <mei:note dur="2" oct="3" pname="d"/>
            </mei:layer>
        </mei:measure>''')
        expected = "%{ m.5 %} %{ l.1 %} d'2 d2 |\n"
        assert lilypond.measure(m_measure) == expected

    def test_measure_2(self):
        "Two layers."
        m_measure = etree.fromstring(
        '''<mei:measure n="5" xmlns:mei="http://www.music-encoding.org/ns/mei">
            <mei:layer n="1">
                <mei:note dur="2" oct="4" pname="d"/>
                <mei:note dur="2" oct="3" pname="d"/>
            </mei:layer>
            <mei:layer n="2">
                <mei:note dur="2" oct="4" pname="e"/>
                <mei:note dur="2" oct="3" pname="e"/>
            </mei:layer>
        </mei:measure>''')
        expected = "%{ m.5 %} << { %{ l.1 %} d'2 d2 } \\\\ { %{ l.2 %} e'2 e2 } >> |\n"
        assert lilypond.measure(m_measure) == expected

    def test_measure_3(self):
        "Three layers."
        m_measure = etree.fromstring(
        '''<mei:measure n="5" xmlns:mei="http://www.music-encoding.org/ns/mei">
            <mei:layer n="1">
                <mei:note dur="2" oct="4" pname="d"/>
                <mei:note dur="2" oct="3" pname="d"/>
            </mei:layer>
            <mei:layer n="2">
                <mei:note dur="2" oct="4" pname="e"/>
                <mei:note dur="2" oct="3" pname="e"/>
            </mei:layer>
            <mei:layer n="3">
                <mei:note dur="2" oct="4" pname="f"/>
                <mei:note dur="2" oct="3" pname="f"/>
            </mei:layer>
        </mei:measure>''')
        expected = "%{ m.5 %} << { %{ l.1 %} d'2 d2 } \\\\ { %{ l.2 %} e'2 e2 } \\\\ { %{ l.3 %} f'2 f2 } >> |\n"
        assert lilypond.measure(m_measure) == expected


class TestStaffClefAndKey(object):
    def test_clef(self):
        # bass
        m_staffdef = etree.fromstring(
            '''<mei:staffDef clef.line="4" clef.shape="F" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lilypond.clef(m_staffdef) == '\\clef "bass"'
        # tenor
        m_staffdef = etree.fromstring(
            '''<mei:staffDef clef.line="4" clef.shape="C" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lilypond.clef(m_staffdef) == '\\clef "tenor"'
        # alto
        m_staffdef = etree.fromstring(
            '''<mei:staffDef clef.line="3" clef.shape="C" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lilypond.clef(m_staffdef) == '\\clef "alto"'
        # treble
        m_staffdef = etree.fromstring(
            '''<mei:staffDef clef.line="2" clef.shape="G" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lilypond.clef(m_staffdef) == '\\clef "treble"'
        # none
        m_staffdef = etree.fromstring(
            '''<mei:staffDef xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')

    def test_key(self):
        # 0 sharps or flats
        m_staffdef = etree.fromstring(
            '''<mei:staffDef key.sig="0" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lilypond.key(m_staffdef) == '\\key c \\major'
        # 3 flats
        m_staffdef = etree.fromstring(
            '''<mei:staffDef key.sig="3f" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lilypond.key(m_staffdef) == '\\key es \\major'
        # 3 sharps
        m_staffdef = etree.fromstring(
            '''<mei:staffDef key.sig="3s" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lilypond.key(m_staffdef) == '\\key a \\major'
        # none
        m_staffdef = etree.fromstring(
            '''<mei:staffDef xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lilypond.key(m_staffdef) == ''

    def test_meter_1(self):
        m_staffdef = etree.Element(mei.STAFF_DEF)
        assert lilypond.meter(m_staffdef) == ''

    def test_meter_2(self):
        m_staffdef = etree.Element(mei.STAFF_DEF)
        m_staffdef.set('meter.count', '3')
        m_staffdef.set('meter.unit', '2')
        assert lilypond.meter(m_staffdef) == '\\time 3/2'

    def test_staff_1(self):
        "One measure."
        m_staff = etree.fromstring(
        '''<mei:staff n="4" xmlns:mei="http://www.music-encoding.org/ns/mei">
            <mei:measure n="9">
                <mei:layer n="6">
                    <mei:note dur="2" oct="2" pname="d"/>
                    <mei:note dur="2" oct="2" pname="d"/>
                </mei:layer>
            </mei:measure>
        </mei:staff>''')
        m_staffdef = etree.fromstring(
        '''
        <mei:staffDef xmlns:mei="http://www.music-encoding.org/ns/mei"
            label="Tuba"
            clef.line="4"
            clef.shape="F"
            n="4"
            key.sig="3s"
            meter.count="2"
            meter.unit="2"
        />
        ''')
        expected = ''.join([
            "\\new Staff {\n",
            "%{ staff 4 %}\n",
            '\\set Staff.instrumentName = "Tuba"\n',
            "\\clef \"bass\"\n",
            "\\key a \\major\n",
            "\\time 2/2\n",
            "%{ m.9 %} %{ l.6 %} d,2 d,2 |\n",
            "}\n",
        ])
        assert lilypond.staff(m_staff, m_staffdef) == expected

    def test_staff_2(self):
        "Three measures."
        m_staff = etree.fromstring(
        '''<mei:staff n="420" xmlns:mei="http://www.music-encoding.org/ns/mei">
            <mei:measure n="9">
                <mei:layer n="1">
                    <mei:note dur="2" oct="2" pname="d"/>
                    <mei:note dur="2" oct="2" pname="d"/>
                </mei:layer>
            </mei:measure>
            <mei:measure n="10">
                <mei:layer n="1">
                    <mei:note dur="2" oct="2" pname="e"/>
                    <mei:note dur="2" oct="2" pname="e"/>
                </mei:layer>
            </mei:measure>
            <mei:measure n="11">
                <mei:layer n="1">
                    <mei:note dur="2" oct="2" pname="f">
                        <mei:accid accid="s"/>
                    </mei:note>
                    <mei:note dur="2" oct="2" pname="f">
                        <mei:accid accid="s"/>
                    </mei:note>
                </mei:layer>
            </mei:measure>
        </mei:staff>''')
        m_staffdef = etree.fromstring(
        '''
        <mei:staffDef xmlns:mei="http://www.music-encoding.org/ns/mei"
            label="Tuba"
            clef.line="4"
            clef.shape="F"
            n="4"
            key.sig="3s"
            meter.count="4"
            meter.unit="4"
        />
        ''')
        expected = ''.join([
            "\\new Staff {\n",
            "%{ staff 420 %}\n",  # blaze it
            '\\set Staff.instrumentName = "Tuba"\n',
            "\\clef \"bass\"\n",
            "\\key a \\major\n",
            "\\time 4/4\n",
            "%{ m.9 %} %{ l.1 %} d,2 d,2 |\n",
            "%{ m.10 %} %{ l.1 %} e,2 e,2 |\n",
            "%{ m.11 %} %{ l.1 %} fis,2 fis,2 |\n",
            "}\n",
        ])
        assert lilypond.staff(m_staff, m_staffdef) == expected

    def test_staff_without_measures(self):
        "Music without measures, but with layers."
        m_staff = etree.fromstring(
        '''<mei:staff n="4" xmlns:mei="http://www.music-encoding.org/ns/mei">
            <mei:layer n="1">
                <mei:note dur="2" oct="2" pname="d"/>
                <mei:note dur="2" oct="2" pname="d"/>
            </mei:layer>
        </mei:staff>''')
        m_staffdef = etree.fromstring(
        '''
        <mei:staffDef xmlns:mei="http://www.music-encoding.org/ns/mei"
            label="Tuba"
            clef.line="4"
            clef.shape="F"
            n="4"
            key.sig="3s"
            meter.count="2"
            meter.unit="2"
        />
        ''')
        expected = ''.join([
            "\\new Staff {\n",
            "%{ staff 4 %}\n",
            '\\set Staff.instrumentName = "Tuba"\n',
            "\\clef \"bass\"\n",
            "\\key a \\major\n",
            "\\time 2/2\n",
            "%{ l.1 %} d,2 d,2\n",
            "}\n",
        ])
        assert lilypond.staff(m_staff, m_staffdef) == expected

    def test_clef_key_time_change(self):
        "Clef, key, and time signature change mid-measure."
        m_staff = etree.fromstring(
        '''<mei:staff n="4" xmlns:mei="http://www.music-encoding.org/ns/mei">
            <mei:layer n="1">
                <mei:note dur="2" oct="2" pname="d"/>
                <mei:staffDef xmlns:mei="http://www.music-encoding.org/ns/mei"
                    n="4"
                    clef.line="4"
                    clef.shape="F"
                    key.sig="3s"
                    meter.count="2"
                    meter.unit="2" />
                <mei:note dur="2" oct="2" pname="d"/>
            </mei:layer>
        </mei:staff>''')
        m_staffdef = etree.fromstring(
        '''
        <mei:staffDef xmlns:mei="http://www.music-encoding.org/ns/mei"
            n="4" />
        ''')
        expected = ''.join([
            "\\new Staff {\n",
            "%{ staff 4 %}\n",
            '\\set Staff.instrumentName = ""\n',
            "\n",
            "\n",
            "\n",
            "%{ l.1 %} d,2 \\clef \"bass\" \\key a \\major \\time 2/2 d,2\n",
            "}\n",
        ])
        assert lilypond.staff(m_staff, m_staffdef) == expected

class TestSection(object):
    def test_section_1(self):
        "Two staves."
        m_section = etree.fromstring(
        '''
        <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
            <mei:scoreDef>
                <mei:staffGrp>
                    <mei:staffDef n="1" label="Clarinet" clef.line="2" clef.shape="G" meter.count="8" meter.unit="8"/>
                    <mei:staffDef n="2" label="Tuba" clef.line="4" clef.shape="F" meter.count="2" meter.unit="2"/>
                </mei:staffGrp>
            </mei:scoreDef>
            <mei:staff n="1">
                <mei:measure n="1">
                    <mei:layer n="1">
                        <mei:note dur="2" oct="5" pname="a"/>
                        <mei:note dur="2" oct="5" pname="a"/>
                    </mei:layer>
                </mei:measure>
            </mei:staff>
            <mei:staff n="2">
                <mei:measure n="1">
                    <mei:layer n="1">
                        <mei:note dur="2" oct="2" pname="d"/>
                        <mei:note dur="2" oct="2" pname="d"/>
                    </mei:layer>
                </mei:measure>
            </mei:staff>
        </mei:section>
        ''')
        expected = ''.join([
            '\\version "2.18.2"\n',
            '\\language "nederlands"\n',
            "\\score {\n",
            "<<\n",
            # clarinet
            "\\new Staff {\n",
            "%{ staff 1 %}\n",
            '\\set Staff.instrumentName = "Clarinet"\n',
            '\\clef "treble"\n',
            "\n",
            '\\time 8/8\n',
            "%{ m.1 %} %{ l.1 %} a''2 a''2 |\n",
            "}\n",
            # tuba
            "\\new Staff {\n",
            "%{ staff 2 %}\n",
            '\\set Staff.instrumentName = "Tuba"\n',
            '\\clef "bass"\n',
            "\n"
            '\\time 2/2\n',
            "%{ m.1 %} %{ l.1 %} d,2 d,2 |\n",
            "}\n",
            #
            ">>\n",
            "\\layout { }\n",
            "}\n",
        ])
        assert lilypond.section(m_section) == expected

    def test_language(self):
        '''
        Integration test of language -- make sure it gets passed down from <section> all the way
        down to <note>.
        '''
        m_section = etree.fromstring(
        '''
        <mei:section xmlns:mei="http://www.music-encoding.org/ns/mei">
            <mei:scoreDef>
                <mei:staffGrp>
                    <mei:staffDef n="1" clef.line="2" clef.shape="G" meter.count="8" meter.unit="8"/>
                </mei:staffGrp>
            </mei:scoreDef>
            <mei:staff n="1">
                <mei:measure n="1">
                    <mei:layer n="1">
                        <mei:note dur="2" oct="2" pname="d" accid.ges="f"/>
                    </mei:layer>
                </mei:measure>
            </mei:staff>
        </mei:section>
        ''')
        context = {'language': 'english'}
        expected = ''.join([
            '\\version "2.18.2"\n',
            '\\language "english"\n',
            "\\score {\n",
            "<<\n",
            # clarinet
            "\\new Staff {\n",
            "%{ staff 1 %}\n",
            '\\set Staff.instrumentName = ""\n',
            '\\clef "treble"\n',
            "\n",
            '\\time 8/8\n',
            '%{ m.1 %} %{ l.1 %} df,2 |\n',
            "}\n",
            #
            ">>\n",
            "\\layout { }\n",
            "}\n",
        ])
        assert lilypond.section(m_section, context) == expected
