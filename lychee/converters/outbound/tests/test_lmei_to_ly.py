#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/test/test_lmei_to_ly.py
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

from lychee.converters.outbound import lmei_to_ly
from lychee import exceptions
from lychee.namespaces import mei


class TestConvert(object):
    def test_convert_1(self):
        mei_thing = etree.fromstring(
            '<mei:note dur="4" oct="4" pname="d" xmlns:mei="http://www.music-encoding.org/ns/mei"/>')
        assert isinstance(lmei_to_ly.convert(mei_thing), str)

    def test_convert_2(self):
        mei_thing = etree.fromstring('<mei:joke xmlns:mei="http://www.music-encoding.org/ns/mei"/>')
        with pytest.raises(exceptions.OutboundConversionError):
            lmei_to_ly.convert(mei_thing)


class TestNoteRest(object):
    def test_note_1(self):
        m_note = etree.Element(mei.NOTE)
        m_note.set('pname', 'e')
        m_note.set('accid.ges', 'f')
        m_note.set('accid', 'f')
        m_note.set('oct', '6')
        m_note.set('dur', '2')
        assert lmei_to_ly.note(m_note) == "ees'''!2"

    def test_note_2(self):
        m_note = etree.Element(mei.NOTE)
        m_note.set('pname', 'e')
        m_note.set('oct', '2')
        assert lmei_to_ly.note(m_note) == "e,"

    def test_rest_1(self):
        m_rest = etree.Element(mei.REST)
        m_rest.set('dur', '32')
        assert lmei_to_ly.rest(m_rest) == "r32"

    def test_rest_2(self):
        m_rest = etree.Element(mei.REST)
        assert lmei_to_ly.rest(m_rest) == "r"


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
        assert lmei_to_ly.layer(m_layer) == expected

    def test_layer_2(self):
        m_layer = etree.fromstring('<mei:layer n="1" xmlns:mei="http://www.music-encoding.org/ns/mei"/>')
        expected = '%{ l.1 %}'
        assert lmei_to_ly.layer(m_layer) == expected

    def test_measure_0(self):
        "No layers."
        m_measure = etree.fromstring(
        '''<mei:measure n="5" xmlns:mei="http://www.music-encoding.org/ns/mei">
        </mei:measure>''')
        expected = "%{ m.5 %} |\n"
        assert lmei_to_ly.measure(m_measure) == expected

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
        assert lmei_to_ly.measure(m_measure) == expected

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
        assert lmei_to_ly.measure(m_measure) == expected

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
        assert lmei_to_ly.measure(m_measure) == expected


class TestStaffClefAndKey(object):
    def test_clef(self):
        # bass
        m_staffdef = etree.fromstring(
            '''<mei:staffDef clef.line="4" clef.shape="F" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lmei_to_ly.clef(m_staffdef) == '\\clef "bass"\n'
        # tenor
        m_staffdef = etree.fromstring(
            '''<mei:staffDef clef.line="4" clef.shape="C" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lmei_to_ly.clef(m_staffdef) == '\\clef "tenor"\n'
        # alto
        m_staffdef = etree.fromstring(
            '''<mei:staffDef clef.line="3" clef.shape="C" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lmei_to_ly.clef(m_staffdef) == '\\clef "alto"\n'
        # treble
        m_staffdef = etree.fromstring(
            '''<mei:staffDef clef.line="2" clef.shape="G" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lmei_to_ly.clef(m_staffdef) == '\\clef "treble"\n'
        # none
        m_staffdef = etree.fromstring(
            '''<mei:staffDef xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')

    def test_key(self):
        # 0 sharps or flats
        m_staffdef = etree.fromstring(
            '''<mei:staffDef key.sig="0" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lmei_to_ly.key(m_staffdef) == '\\key c \\major\n'
        # 3 flats
        m_staffdef = etree.fromstring(
            '''<mei:staffDef key.sig="3f" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lmei_to_ly.key(m_staffdef) == '\\key ees \\major\n'
        # 3 sharps
        m_staffdef = etree.fromstring(
            '''<mei:staffDef key.sig="3s" xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lmei_to_ly.key(m_staffdef) == '\\key a \\major\n'
        # none
        m_staffdef = etree.fromstring(
            '''<mei:staffDef xmlns:mei="http://www.music-encoding.org/ns/mei"/>''')
        assert lmei_to_ly.key(m_staffdef) == '\n'

    def test_meter_1(self):
        m_staffdef = etree.Element(mei.STAFF_DEF)
        assert lmei_to_ly.meter(m_staffdef) == '\n'

    def test_meter_2(self):
        m_staffdef = etree.Element(mei.STAFF_DEF)
        m_staffdef.set('meter.count', '3')
        m_staffdef.set('meter.unit', '2')
        assert lmei_to_ly.meter(m_staffdef) == '\\time 3/2\n'

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
        assert lmei_to_ly.staff(m_staff, m_staffdef) == expected

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
                    <mei:note dur="2" oct="2" pname="f" accid.ges="s"/>
                    <mei:note dur="2" oct="2" pname="f" accid.ges="s"/>
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
        assert lmei_to_ly.staff(m_staff, m_staffdef) == expected


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
        assert lmei_to_ly.section(m_section) == expected
