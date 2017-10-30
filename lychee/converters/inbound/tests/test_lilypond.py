#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/tests/test_lilypond.py
# Purpose:                Tests for the "lilypond" module.
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
"""
Tests for the "lilypond" module.

The tests in this file are only for the translator, not the parser. In other words, these tests are
for the code that translated TatSu's parse into Lychee-MEI.

A few of the more complicated tests do use the LilyPond parser to improve readability.
"""

from __future__ import unicode_literals

from lxml import etree
import pytest

from lychee.converters.inbound import lilypond
from lychee.converters.inbound import lilypond_parser
from lychee import exceptions
from lychee.namespaces import mei

parser = lilypond_parser.LilyPondParser()


class TestScore(object):
    """
    Converting a whole score.
    """

    def test_not_a_score(self):
        """The input is not a score."""
        l_score = {'ly_type': 'pizza'}
        with pytest.raises(exceptions.LilyPondError):
            lilypond.do_score(l_score)

    def test_no_staves(self):
        """No staves."""
        l_score = {'ly_type': 'score', 'staves': []}
        actual = lilypond.do_score(l_score)
        assert actual.tag == mei.SECTION
        assert len(actual) == 1
        assert actual[0].tag == mei.SCORE_DEF
        assert len(actual[0]) == 1
        assert actual[0][0].tag == mei.STAFF_GRP
        assert len(actual[0][0]) == 0

    def test_one_staff(self):
        """One staff."""
        l_score = {
            'ly_type': 'score',
            'staves': [{
                'ly_type': 'staff',
                'initial_settings': [{'ly_type': 'instr_name', 'name': 'Woo'}],
                'content': [{'layers': [[{'pitch_name': 'bes', 'oct': ',',
                             'accid_force': None, 'dur': '128', 'dots': [], 'ly_type': 'note'}]]}],
            }]
        }
        actual = lilypond.do_score(l_score)
        # in the <StaffGrp>
        assert len(actual[0][0]) == 1
        assert actual[0][0][0].tag == mei.STAFF_DEF
        assert actual[0][0][0].get('n') == '1'
        assert actual[0][0][0].get('lines') == '5'
        assert actual[0][0][0].get('label') == 'Woo'
        # the <staff> itself
        assert actual[1].tag == mei.STAFF
        assert actual[1].get('n') == '1'

    def test_three_staves(self):
        """Three staves."""
        # shout-out to 女孩与机器人
        l_score = {
            'ly_type': 'score',
            'staves': [
                {
                    'ly_type': 'staff',
                    'initial_settings': [{'ly_type': 'instr_name', 'name': 'Riin'}],
                    'content': [{'layers': [[{'pitch_name': 'bes', 'oct': ',',
                                 'accid_force': None, 'dur': '128', 'dots': [], 'ly_type': 'note'}]]}],
                },
                {
                    'ly_type': 'staff',
                    'initial_settings': [{'ly_type': 'instr_name', 'name': '蛋'}],
                    'content': [{'layers': [[{'pitch_name': 'bes', 'oct': ',',
                                 'accid_force': None, 'dur': '128', 'dots': [], 'ly_type': 'note'}]]}],
                },
                {
                    'ly_type': 'staff',
                    'initial_settings': [{'ly_type': 'instr_name', 'name': 'Jungle'}],
                    'content': [{'layers': [[{'pitch_name': 'bes', 'oct': ',',
                                 'accid_force': None, 'dur': '128', 'dots': [], 'ly_type': 'note'}]]}],
                },
            ]
        }
        actual = lilypond.do_score(l_score)
        # in the <StaffGrp>
        assert len(actual[0][0]) == 3
        assert actual[0][0][0].tag == mei.STAFF_DEF
        assert actual[0][0][0].get('n') == '1'
        assert actual[0][0][0].get('lines') == '5'
        assert actual[0][0][0].get('label') == 'Riin'
        assert actual[0][0][1].tag == mei.STAFF_DEF
        assert actual[0][0][1].get('n') == '2'
        assert actual[0][0][1].get('lines') == '5'
        assert actual[0][0][1].get('label') == '蛋'
        assert actual[0][0][2].tag == mei.STAFF_DEF
        assert actual[0][0][2].get('n') == '3'
        assert actual[0][0][2].get('lines') == '5'
        assert actual[0][0][2].get('label') == 'Jungle'
        # the <staff> itself
        assert actual[1].tag == mei.STAFF
        assert actual[1].get('n') == '1'
        assert actual[2].tag == mei.STAFF
        assert actual[2].get('n') == '2'
        assert actual[3].tag == mei.STAFF
        assert actual[3].get('n') == '3'

    def test_language(self):
        """At a distance, make sure that language gets correctly passed down
        all the way to the pitch name converter."""
        l_score = {
            'ly_type': 'score',
            'staves': [{
                'ly_type': 'staff',
                'initial_settings': [{'ly_type': 'instr_name', 'name': 'Woo'}],
                'content': [{'layers': [[{'pitch_name': 'css', 'oct': ',',
                             'accid_force': None, 'dur': '4', 'dots': [], 'ly_type': 'note'}]]}],
            }]
        }
        actual = lilypond.do_score(l_score, context={'language': 'english'})
        accid = actual.find('.//{}'.format(mei.ACCID))
        assert accid.attrib.get('accid') == 'x'


class TestClef(object):
    """
    Setting the clef.
    """

    def test_invalid_clef(self):
        """The input isn't a clef."""
        l_time = {'ly_type': '', 'type': ''}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        with pytest.raises(exceptions.LilyPondError):
            lilypond.set_clef(l_time, m_staffdef)

    def test_nonexistent_clef(self):
        """The clef type doesn't exist."""
        l_time = {'ly_type': 'clef', 'type': 'bullshit'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_clef(l_time, m_staffdef)
        assert m_staffdef.get('clef.shape') is None
        assert m_staffdef.get('clef.line') is None

    def test_works(self):
        """It works."""
        l_time = {'ly_type': 'clef', 'type': 'bass'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_clef(l_time, m_staffdef)
        assert m_staffdef.get('clef.shape') == 'F'
        assert m_staffdef.get('clef.line') == '4'

    def test_change(self):
        """Clef change in the context of a staff. The @n should match."""
        l_staff = {
            'ly_type': 'staff',
            'initial_settings': [],
            'content': [{'layers': [[
                {'dur': '2', 'dots': [], 'ly_type': 'rest'},
                {'ly_type': 'clef', 'type': 'treble'},
                {'dur': '4', 'dots': [], 'ly_type': 'rest'},
            ]]}],
        }
        m_staff = etree.Element(mei.STAFF)
        m_staffdef = etree.Element(mei.STAFF_DEF)
        m_staffdef.set('n', '888')
        lilypond.do_staff(l_staff, m_staff, m_staffdef)
        m_staffdef = m_staff.find('.//{}'.format(mei.STAFF_DEF))
        assert m_staffdef.get('n') == '888'


class TestTime(object):
    """
    Setting the time signature.
    """

    def test_invalid_time(self):
        """The input isn't a time signature."""
        l_time = {'ly_type': 'intro', 'count': '23', 'unit': '64'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        with pytest.raises(exceptions.LilyPondError):
            lilypond.set_time(l_time, m_staffdef)

    def test_works(self):
        """You know..."""
        l_time = {'ly_type': 'time', 'count': '23', 'unit': '64'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_time(l_time, m_staffdef)
        assert m_staffdef.get('meter.count') == '23'
        assert m_staffdef.get('meter.unit') == '64'

    def test_change(self):
        """Time change in the context of a staff. The @n should match."""
        l_staff = {
            'ly_type': 'staff',
            'initial_settings': [],
            'content': [{'layers': [[
                {'dur': '2', 'dots': [], 'ly_type': 'rest'},
                {'ly_type': 'time', 'count': '4', 'unit': '4'},
                {'dur': '4', 'dots': [], 'ly_type': 'rest'},
            ]]}],
        }
        m_staff = etree.Element(mei.STAFF)
        m_staffdef = etree.Element(mei.STAFF_DEF)
        m_staffdef.set('n', '888')
        lilypond.do_staff(l_staff, m_staff, m_staffdef)
        m_staffdef = m_staff.find('.//{}'.format(mei.STAFF_DEF))
        assert m_staffdef.get('n') == '888'


class TestKeySignature(object):
    """
    Setting the key signature from the LilyPond key.
    """

    def test_invalid_key(self):
        """The input isn't a key."""
        l_key = {'ly_type': 'rawr', 'keynote': '', 'accid': '', 'mode': ''}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        with pytest.raises(exceptions.LilyPondError):
            lilypond.set_key(l_key, m_staffdef)

    def test_major_key(self):
        """Major key."""
        l_key = {'ly_type': 'key', 'keynote': 'des', 'mode': 'major'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_key(l_key, m_staffdef)
        assert m_staffdef.get('key.sig') == '5f'

    def test_minor_key(self):
        """Minor key."""
        l_key = {'ly_type': 'key', 'keynote': 'a', 'mode': 'minor'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_key(l_key, m_staffdef)
        assert m_staffdef.get('key.sig') == '0'

    def test_language(self):
        """English language."""
        l_key = {'ly_type': 'key', 'keynote': 'ds', 'mode': 'minor'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_key(l_key, m_staffdef, context={'language': 'english'})
        assert m_staffdef.get('key.sig') == '6s'

    def test_change(self):
        """Key change in the context of a staff. The @n should match."""
        l_staff = {
            'ly_type': 'staff',
            'initial_settings': [],
            'content': [{'layers': [[
                {'dur': '2', 'dots': [], 'ly_type': 'rest'},
                {'ly_type': 'key', 'keynote': 'd', 'accid': '', 'mode': 'major'},
                {'dur': '4', 'dots': [], 'ly_type': 'rest'},
            ]]}],
        }
        m_staff = etree.Element(mei.STAFF)
        m_staffdef = etree.Element(mei.STAFF_DEF)
        m_staffdef.set('n', '888')
        lilypond.do_staff(l_staff, m_staff, m_staffdef)
        m_staffdef = m_staff.find('.//{}'.format(mei.STAFF_DEF))
        assert m_staffdef.get('n') == '888'


class TestInstrumentName(object):
    """
    Setting the instrument name.
    """

    def test_invalid_name(self):
        """The input isn't an instrument name."""
        l_name = {'ly_type': '', 'name': 'FFFFFFF'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        with pytest.raises(exceptions.LilyPondError):
            lilypond.set_instrument_name(l_name, m_staffdef)

    def test_works(self):
        """It works."""
        l_name = {'ly_type': 'instr_name', 'name': 'Clarinet'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_instrument_name(l_name, m_staffdef)
        assert m_staffdef.get('label') == 'Clarinet'


class TestStaves(object):
    """
    For staves.
    """

    def test_error_1(self):
        """When 'l_staff' is not a staff."""
        l_staff = {'ly_type': 'job application'}
        m_section = etree.Element(mei.SECTION)
        m_staffdef = etree.Element(mei.STAFF_DEF, {'n': '8'})
        with pytest.raises(exceptions.LilyPondError):
            lilypond.do_staff(l_staff, m_section, m_staffdef)

    def test_error_2(self):
        """When 'm_staffdef' is missing @n."""
        l_staff = {'ly_type': 'staff'}
        m_section = etree.Element(mei.SECTION)
        m_staffdef = etree.Element(mei.STAFF_DEF)
        with pytest.raises(exceptions.LilyPondError):
            lilypond.do_staff(l_staff, m_section, m_staffdef)

    def test_settings_1(self):
        """
        No staff settings; the <staffDef> isn't changed.
        """
        l_staff = {
            'ly_type': 'staff',
            'initial_settings': [],
            'content': [],
        }
        m_section = etree.Element(mei.SECTION)
        m_staffdef = etree.Element(mei.STAFF_DEF, {'n': '8'})
        lilypond.do_staff(l_staff, m_section, m_staffdef)

        assert m_staffdef.attrib == {
            'n': '8',
            'clef.shape': 'G',
            'clef.line': '2',
            'meter.count': '4',
            'meter.unit': '4',
            }

    def test_settings_2(self):
        """
        One staff setting; handled properly.
        """
        l_staff = {
            'ly_type': 'staff',
            'initial_settings': [{'ly_type': 'time', 'count': '3', 'unit': '4'}],
            'content': [],
        }
        m_section = etree.Element(mei.SECTION)
        m_staffdef = etree.Element(mei.STAFF_DEF, {'n': '8'})
        lilypond.do_staff(l_staff, m_section, m_staffdef)

        assert m_staffdef.attrib == {
            'n': '8',
            'clef.shape': 'G',
            'clef.line': '2',
            'meter.count': '3',
            'meter.unit': '4',
            }

    def test_settings_3(self):
        """
        All possible staff settings; handled properly.
        """
        l_staff = {
            'ly_type': 'staff',
            'initial_settings': [
                {'ly_type': 'time', 'count': '3', 'unit': '4'},
                {'ly_type': 'clef', 'type': 'bass'},
                {'ly_type': 'key', 'keynote': 'des', 'mode': 'major'},
                {'ly_type': 'instr_name', 'name': 'Broccoliphone'},
            ],
            'content': [],
        }
        m_section = etree.Element(mei.SECTION)
        m_staffdef = etree.Element(mei.STAFF_DEF, {'n': '8'})
        lilypond.do_staff(l_staff, m_section, m_staffdef)

        assert m_staffdef.attrib == {
            'n': '8',
            'meter.count': '3', 'meter.unit': '4',
            'clef.shape': 'F', 'clef.line': '4',
            'key.sig': '5f',
            'label': 'Broccoliphone',
        }

    def test_staff_1(self):
        """
        A staff a monophonic passage.

        Parsed version of this:
        r'\new Staff { s2 s4 | s2 }'
        """
        l_staff = {
            'ly_type': 'staff',
            'initial_settings': [],
            'content': [{'layers': [[
                {'dur': '2', 'dots': [], 'ly_type': 'spacer'},
                {'dur': '4', 'dots': [], 'ly_type': 'spacer'},
                {'ly_type': 'barcheck'},
                {'dur': '2', 'dots': [], 'ly_type': 'spacer'},
            ]]}],
        }
        m_section = etree.Element(mei.SECTION)
        m_staffdef = etree.Element(mei.STAFF_DEF, {'n': '8'})
        lilypond.do_staff(l_staff, m_section, m_staffdef)

        # one <staff>
        assert len(m_section) == 1
        assert m_section[0].tag == mei.STAFF
        assert m_section[0].get('n') == '8'
        # one <layer>
        assert len(m_section[0]) == 1
        assert m_section[0][0].tag == mei.LAYER
        assert len(m_section[0][0]) == 3  # two spacer rests

    def test_staff_2(self):
        """
        A staff with a polyphonic passage.

        Parsed version of this:
        r'\new Staff { << { s2 s4 } \\ { r2 r4 } >> }'
        """
        l_staff = {
            'ly_type': 'staff',
            'initial_settings': [],
            'content': [{'layers': [
                [
                    {'dur': '2', 'dots': [], 'ly_type': 'spacer'},
                    {'dur': '4', 'dots': [], 'ly_type': 'spacer'},
                ],
                [
                    {'dur': '2', 'dots': [], 'ly_type': 'rest'},
                    {'dur': '4', 'dots': [], 'ly_type': 'rest'},
                ],
            ]}],
        }
        m_section = etree.Element(mei.SECTION)
        m_staffdef = etree.Element(mei.STAFF_DEF, {'n': '16'})
        lilypond.do_staff(l_staff, m_section, m_staffdef)

        assert len(m_section) == 1  # one <staff>
        assert m_section[0].tag == mei.STAFF
        assert m_section[0].get('n') == '16'
        assert len(m_section[0]) == 2  # two <layer>s
        assert m_section[0][0].tag == mei.LAYER
        assert len(m_section[0][0]) == 2  # two spacer rests
        assert m_section[0][1].tag == mei.LAYER
        assert len(m_section[0][1]) == 2  # two spacer rests

    def test_staff_3(self):
        """
        A staff with a polyphonic passage then a monophonic passage.

        Parsed version of this:
        r'\new Staff { << { s2 s4 } \\ { r2 r4 } >> bes,128 }'
        """
        l_staff = {
            'ly_type': 'staff',
            'initial_settings': [],
            'content': [
                {'layers': [
                    [
                        {'dur': '2', 'dots': [], 'ly_type': 'spacer'},
                        {'dur': '4', 'dots': [], 'ly_type': 'spacer'},
                    ],
                    [
                        {'dur': '2', 'dots': [], 'ly_type': 'rest'},
                        {'dur': '4', 'dots': [], 'ly_type': 'rest'},
                    ],
                ]},
                {
                    'layers': [
                        [
                            {'pitch_name': 'bes', 'oct': ',', 'accid_force': None,
                                'dur': '128', 'dots': [], 'ly_type': 'note'}
                        ]
                    ]
                },
            ],
        }
        m_section = etree.Element(mei.SECTION)
        m_staffdef = etree.Element(mei.STAFF_DEF, {'n': '32'})
        lilypond.do_staff(l_staff, m_section, m_staffdef)

        assert len(m_section) == 2  # two <staff>s
        assert m_section[0].tag == mei.STAFF
        assert m_section[0].get('n') == '32'
        assert m_section[1].tag == mei.STAFF
        assert m_section[1].get('n') == '32'
        # first <staff>
        assert len(m_section[0]) == 2  # two <layer>s
        assert m_section[0][0].tag == mei.LAYER
        assert len(m_section[0][0]) == 2  # two spacer rests
        assert m_section[0][1].tag == mei.LAYER
        assert len(m_section[0][1]) == 2  # two spacer rests
        # second <staff>
        assert len(m_section[1]) == 1  # one <layer>
        assert m_section[1][0].tag == mei.LAYER
        assert len(m_section[1][0]) == 1  # one <note>


class TestLayers(object):
    """
    For Voice contexts converting to layers.
    """

    def test_empty(self):
        """The Voice context is empty."""
        l_layer = []
        m_container = etree.Element(mei.MEASURE)
        layer_n = 42

        actual = lilypond.do_layer(l_layer, m_container, layer_n)

        assert m_container[0] is actual
        assert actual.tag == mei.LAYER
        assert actual.get('n') == str(layer_n)
        assert len(actual) == 0

    def test_unknown_nodes(self):
        """The Voice context only has two unknown nodes and a rest."""
        l_layer = [
            {'ly_type': 'broccoli'},
            {'ly_type': 'rest', 'dur': '2', 'dots': []},
            {'ly_type': 'cabbage'},
        ]
        m_container = etree.Element(mei.STAFF)
        layer_n = 42

        actual = lilypond.do_layer(l_layer, m_container, layer_n)

        assert len(actual) == 1
        assert actual[0].tag == mei.REST

    def test_mixed_nodes(self):
        """The Voice context has nodes of every type."""
        l_layer = [
            {'ly_type': 'rest', 'dur': '2', 'dots': []},
            {'ly_type': 'spacer', 'dur': '2', 'dots': []},
            {'ly_type': '白菜'},
            {'ly_type': 'note', 'pitch_name': 'f', 'oct': "''", 'accid_force': None,
             'dur': '256', 'dots': []},
            {'ly_type': 'chord', 'dur': '2', 'dots': ['.'], 'notes': [
                {'ly_type': 'note', 'pitch_name': 'des', 'oct': ',,', 'accid_force': '!'},
                {'ly_type': 'note', 'pitch_name': 'fis', 'oct': ',,', 'accid_force': None},
                {'ly_type': 'note', 'pitch_name': 'a', 'oct': ',,', 'accid_force': None},
            ]},
        ]
        m_container = etree.Element(mei.STAFF)
        layer_n = 42

        actual = lilypond.do_layer(l_layer, m_container, layer_n)

        assert len(actual) == 4
        assert actual[0].tag == mei.REST
        assert actual[1].tag == mei.SPACE
        assert actual[2].tag == mei.NOTE
        assert actual[3].tag == mei.CHORD


class TestProcessOctave(object):
    """
    For the octave thing.
    """

    def test_works(self):
        """It's an octave."""
        assert '1' == lilypond.process_octave(',,')

    def test_none(self):
        """It's given ``None``."""
        assert '3' == lilypond.process_octave(None)

    def test_invalid(self):
        """The octave is invalid."""
        assert lilypond.process_octave(None) == lilypond.process_octave('celery')


class TestPitch(object):
    """
    For pitch name, accidental, and accidental force handling.
    """

    def test_no_accid(self):
        """When there is no accidental."""
        l_note = {"pitch_name": "c"}
        attrib, accid_attrib = {}, {}
        expected = ({"pname": "c"}, {})
        actual = lilypond.process_pitch(l_note, attrib, accid_attrib)
        assert expected == actual

    def test_double_sharp(self):
        """Double sharp."""
        l_note = {"pitch_name": "cisis"}
        attrib, accid_attrib = {}, {}

        expected = ({"pname": "c"}, {"accid.ges": "x"})
        actual = lilypond.process_pitch(l_note, attrib, accid_attrib)
        assert expected == actual

    def test_single_flat(self):
        """Single flat."""
        l_note = {"pitch_name": "ees"}
        attrib, accid_attrib = {}, {}
        expected = ({"pname": "e"}, {"accid.ges": "f"})
        actual = lilypond.process_pitch(l_note, attrib, accid_attrib)
        assert expected == actual

    def test_language(self):
        """German."""
        l_note = {"pitch_name": "h"}
        attrib, accid_attrib = {}, {}
        context = {"language": "deutsch"}
        expected = ({"pname": "b"}, {})
        actual = lilypond.process_pitch(l_note, attrib, accid_attrib, context)
        assert expected == actual

    def test_sharpflat(self):
        """Sharpflat (invalid accidental)."""
        l_note = {"pitch_name": "cises"}
        attrib, accid_attrib = {}, {}
        with pytest.raises(exceptions.LilyPondError):
            lilypond.process_pitch(l_note, attrib, accid_attrib)


class TestProcessDots(object):
    """
    For the @dots attribute.
    """

    def test_dots_1(self):
        """No dots."""
        l_node = {'dots': []}
        attrib = {}
        actual = lilypond.process_dots(l_node, attrib)
        assert 'dots' not in attrib

    def test_dots_2(self):
        """Three dots."""
        l_node = {'dots': ['.', '.', '.']}
        attrib = {}
        actual = lilypond.process_dots(l_node, attrib)
        assert attrib['dots'] == '3'

    def test_dots_3(self):
        """No "dots" member in "l_node"."""
        l_node = {'clots': ['.']}
        attrib = {}
        actual = lilypond.process_dots(l_node, attrib)
        assert 'dots' not in attrib


class TestChord(object):
    """
    For chords.
    """

    def test_not_a_chord(self):
        """When it receives something other than a chord, raise exceptions.LilyPondError."""
        l_chord = {'ly_type': 'broccoli'}
        m_layer = etree.Element(mei.LAYER)
        with pytest.raises(exceptions.LilyPondError):
            lilypond.do_chord(l_chord, m_layer)

    def test_empty_chord(self):
        """When the chord has no noteheads."""
        l_chord = {'ly_type': 'chord', 'dur': '2', 'dots': ['.'], 'notes': []}
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_chord(l_chord, m_layer)

        assert actual.tag == mei.CHORD
        assert actual is m_layer[0]
        assert actual.get('dur') == '2'
        assert actual.get('dots') == '1'
        assert len(actual) == 0

    def test_one_notehead(self):
        """When the chord has one notehead, with a cautionary accidental."""
        l_chord = {'ly_type': 'chord', 'dur': '2', 'dots': ['.'], 'notes': [
            {'ly_type': 'note', 'pitch_name': 'des', 'oct': ',,', 'accid_force': '?'},
        ]}
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_chord(l_chord, m_layer)

        assert len(actual) == 1
        assert actual[0].get('pname') == 'd'
        assert actual[0].get('oct') == '1'
        assert actual[0][0].tag == mei.ACCID
        assert actual[0][0].get('accid.ges') == 'f'
        assert actual[0][0].get('accid.force') == '?'

    def test_three_noteheads(self):
        """When the chord has three noteheads, the first with a forced accidental."""
        l_chord = {'ly_type': 'chord', 'dur': '2', 'dots': ['.'], 'notes': [
            {'ly_type': 'note', 'pitch_name': 'des', 'oct': ',,', 'accid_force': '!'},
            {'ly_type': 'note', 'pitch_name': 'fis', 'oct': ',,', 'accid_force': None},
            {'ly_type': 'note', 'pitch_name': 'a', 'oct': ',,', 'accid_force': None},
        ]}
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_chord(l_chord, m_layer)

        assert len(actual) == 3
        #
        assert actual[0].get('pname') == 'd'
        assert actual[0].get('oct') == '1'
        assert actual[0][0].tag == mei.ACCID
        assert actual[0][0].get('accid.ges') == 'f'
        assert actual[0][0].get('accid.force') == '!'
        #
        assert actual[1].get('pname') == 'f'
        assert actual[1].get('oct') == '1'
        assert actual[1][0].tag == mei.ACCID
        assert actual[1][0].get('accid.ges') == 's'
        assert actual[1][0].get('accid.force') is None
        #
        assert actual[2].get('pname') == 'a'
        assert actual[2].get('oct') == '1'
        assert actual[2][0].tag == mei.ACCID
        assert actual[2][0].get('accid.ges') is None
        assert actual[2][0].get('accid.force') is None

    def test_language(self):
        """Italiano."""
        l_chord = {'ly_type': 'chord', 'dur': '2', 'dots': [], 'notes': [
            {'ly_type': 'note', 'pitch_name': 'do', 'oct': '', 'accid_force': '!'},
            {'ly_type': 'note', 'pitch_name': 'red', 'oct': '', 'accid_force': None},
            {'ly_type': 'note', 'pitch_name': 'mibb', 'oct': '', 'accid_force': None},
        ]}
        m_layer = etree.Element(mei.LAYER)
        context = {'language': 'italiano'}
        actual = lilypond.do_chord(l_chord, m_layer, context)

        assert len(actual) == 3
        #
        assert actual[0].get('pname') == 'c'
        assert actual[0].get('oct') == '3'
        assert actual[0][0].tag == mei.ACCID
        assert actual[0][0].get('accid.ges') is None
        assert actual[0][0].get('accid.force') == '!'
        #
        assert actual[1].get('pname') == 'd'
        assert actual[1].get('oct') == '3'
        assert actual[1][0].tag == mei.ACCID
        assert actual[1][0].get('accid.ges') == 's'
        assert actual[1][0].get('accid.force') is None
        #
        assert actual[2].get('pname') == 'e'
        assert actual[2].get('oct') == '3'
        assert actual[2][0].tag == mei.ACCID
        assert actual[2][0].get('accid.ges') == 'ff'
        assert actual[2][0].get('accid.force') is None


class TestNote(object):
    """
    For notes.
    """

    def test_not_a_note(self):
        """When it receives something other than a note, raise exceptions.LilyPondError."""
        l_note = {'ly_type': 'broccoli'}
        m_layer = etree.Element(mei.LAYER)
        with pytest.raises(exceptions.LilyPondError):
            lilypond.do_note(l_note, m_layer)

    def test_basic_attribs(self):
        """Note only has @pname, @oct, and @dur."""
        l_note = {'ly_type': 'note', 'pitch_name': 'f', 'oct': "''", 'accid_force': None,
                  'dur': '256', 'dots': []}
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_note(l_note, m_layer)

        assert actual.tag == mei.NOTE
        assert actual is m_layer[0]
        assert actual.get('dur') == '256'
        assert actual.get('pname') == 'f'
        assert actual.get('oct') == '5'

    def test_external_attribs(self):
        """Note has attributes handled by process_x() functions before Element creation."""
        l_note = {'ly_type': 'note', 'pitch_name': 'fis', 'oct': "''", 'accid_force': '!',
                  'dur': '256', 'dots': ['.', '.']}
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_note(l_note, m_layer)

        assert actual.get('dots') == '2'
        assert actual[0].tag == mei.ACCID
        assert actual[0].get('accid.ges') == 's'
        assert actual[0].get('accid.force') == '!'

    def test_children(self):
        """Note has sub-elements added by process_x() functions after Element creation."""
        l_note = {'ly_type': 'note', 'pitch_name': 'fis', 'oct': "''", 'accid_force': '?',
                  'dur': '256', 'dots': []}
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_note(l_note, m_layer)

        assert actual[0].tag == mei.ACCID
        assert actual[0].get('accid.ges') == 's'
        assert actual[0].get('accid.force') == '?'


class TestRestSpacer(object):
    """
    For rests and spacers.
    """

    def test_rest_1(self):
        """When it works fine, no dots."""
        l_rest = {'ly_type': 'rest', 'dur': '2', 'dots': []}
        m_layer = etree.Element(mei.LAYER)

        actual = lilypond.do_rest(l_rest, m_layer)

        assert actual.tag == mei.REST
        assert m_layer[0] is actual
        assert actual.get('dur') == '2'
        assert actual.get('dots') is None

    def test_rest_2(self):
        """When it works fine, two dots."""
        l_rest = {'ly_type': 'rest', 'dur': '2', 'dots': ['.', '.']}
        m_layer = etree.Element(mei.LAYER)

        actual = lilypond.do_rest(l_rest, m_layer)

        assert actual.get('dur') == '2'
        assert actual.get('dots') == '2'

    def test_rest_3(self):
        """When it receives a spacer, should fail."""
        l_rest = {'ly_type': 'spacer', 'dur': '2', 'dots': []}
        m_layer = etree.Element(mei.LAYER)

        with pytest.raises(exceptions.LilyPondError):
            lilypond.do_rest(l_rest, m_layer)

    def test_measure_rest_1(self):
        """When it works fine, no dots."""
        l_measure_rest = {'ly_type': 'measure_rest', 'dur': '2', 'dots': []}
        m_layer = etree.Element(mei.LAYER)

        actual = lilypond.do_measure_rest(l_measure_rest, m_layer)

        assert actual.tag == mei.M_REST
        assert m_layer[0] is actual
        assert actual.get('dur') == '2'
        assert actual.get('dots') is None

    def test_measure_rest_2(self):
        """When it works fine, two dots."""
        l_measure_rest = {'ly_type': 'measure_rest', 'dur': '2', 'dots': ['.', '.']}
        m_layer = etree.Element(mei.LAYER)

        actual = lilypond.do_measure_rest(l_measure_rest, m_layer)

        assert actual.get('dur') == '2'
        assert actual.get('dots') == '2'

    def test_measure_rest_3(self):
        """When it receives a rest, should fail."""
        l_rest = {'ly_type': 'rest', 'dur': '2', 'dots': []}
        m_layer = etree.Element(mei.LAYER)

        with pytest.raises(exceptions.LilyPondError):
            lilypond.do_measure_rest(l_rest, m_layer)

    def test_spacer_1(self):
        """When it works fine, no dots."""
        l_rest = {'ly_type': 'spacer', 'dur': '2', 'dots': []}
        m_layer = etree.Element(mei.LAYER)

        actual = lilypond.do_spacer(l_rest, m_layer)

        assert actual.tag == mei.SPACE
        assert m_layer[0] is actual
        assert actual.get('dur') == '2'
        assert actual.get('dots') is None

    def test_spacer_2(self):
        """When it works fine, two dots."""
        l_rest = {'ly_type': 'spacer', 'dur': '2', 'dots': ['.', '.']}
        m_layer = etree.Element(mei.LAYER)

        actual = lilypond.do_spacer(l_rest, m_layer)

        assert actual.get('dur') == '2'
        assert actual.get('dots') == '2'

    def test_spacer_3(self):
        """When it receives a rest, should fail."""
        l_rest = {'ly_type': 'rest', 'dur': '2', 'dots': []}
        m_layer = etree.Element(mei.LAYER)

        with pytest.raises(exceptions.LilyPondError):
            lilypond.do_spacer(l_rest, m_layer)


class TestTie(object):

    def test_basic_tie(self):
        '''
        Test the equivalent of the LilyPond code "c c~ c~ c c". This covers
        four cases involving tied and untied notes:

        - Untied note before tied note
        - Tied note before tied note
        - Tied note before untied note
        - Untied note before untied note
        '''
        l_layer = [
            {'ly_type': 'note', 'pitch_name': 'c', 'oct': '', 'dur': '4',
                'accid_force': None, 'dots': [], 'post_events': []},
            {'ly_type': 'note', 'pitch_name': 'c', 'oct': '', 'dur': '4',
                'accid_force': None, 'dots': [], 'post_events': [{'ly_type': 'tie'}]},
            {'ly_type': 'note', 'pitch_name': 'c', 'oct': '', 'dur': '4',
                'accid_force': None, 'dots': [], 'post_events': [{'ly_type': 'tie'}]},
            {'ly_type': 'note', 'pitch_name': 'c', 'oct': '', 'dur': '4',
                'accid_force': None, 'dots': [], 'post_events': []},
            {'ly_type': 'note', 'pitch_name': 'c', 'oct': '', 'dur': '4',
                'accid_force': None, 'dots': [], 'post_events': []}
        ]
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_layer(l_layer, m_layer, 1)
        tie_attributes = [node.get('tie') for node in actual]
        assert tie_attributes == [None, 'i', 'm', 't', None]


class TestSlur(object):

    def test_basic_slur(self):
        '''
        Test the equivalent of the LilyPond code "c c( c c) c"
        '''
        l_layer = [
            {'ly_type': 'note', 'pitch_name': 'c', 'oct': '', 'dur': '4',
                'accid_force': None, 'dots': [], 'post_events': []},
            {'ly_type': 'note', 'pitch_name': 'c', 'oct': '', 'dur': '4',
                'accid_force': None, 'dots': [], 'post_events': [{'ly_type': 'slur', 'slur': '('}]},
            {'ly_type': 'note', 'pitch_name': 'c', 'oct': '', 'dur': '4',
                'accid_force': None, 'dots': [], 'post_events': []},
            {'ly_type': 'note', 'pitch_name': 'c', 'oct': '', 'dur': '4',
                'accid_force': None, 'dots': [], 'post_events': [{'ly_type': 'slur', 'slur': ')'}]},
            {'ly_type': 'note', 'pitch_name': 'c', 'oct': '', 'dur': '4',
                'accid_force': None, 'dots': [], 'post_events': []}
        ]
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_layer(l_layer, m_layer, 1)
        slur_attributes = [node.get('slur') for node in actual]
        assert slur_attributes == [None, 'i1', 'm1', 't1', None]


class TestAccidentalRendering(object):

    def test_basic(self):
        '''
        Within a bar, there are five basic cases to consider with accidentals:

        1. C C - non-accidental note followed by a non-accidental note. No accidentals should be
        produced at all.

        2. C C# - Non-accidental note followed by an accidental note. The second note should produce
        an accidental, but not the first.

        3. C# C - Accidental note followed by a non-accidental note. The second note should produce
        a natural.

        4. C# C# - Accidental note followed by the same accidental note. The second note should not
        display an accidental.

        4. C# Cb - Accidental note followed by a different accidental note. Both notes should
        display accidentals.

        These five cases multiply even further when combined with considerations of chords, ties
        accidental forcing, and key signature and time signature changes. Not all possible cases are
        tested here...
        '''
        lilypond_source = '''
            c2 c2
            d2 dis2
            es2 e2
            fis2 fis2
            geses2 gis2
        '''
        l_layer = parser.parse(lilypond_source, rule_name='unmarked_layer')
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_layer(l_layer, m_layer, 1)

        assert actual[0].find(mei.ACCID) is None
        assert actual[1].find(mei.ACCID) is None

        assert actual[2].find(mei.ACCID) is None
        assert actual[3].find(mei.ACCID).get('accid') == 's'

        assert actual[4].find(mei.ACCID).get('accid') == 'f'
        assert actual[5].find(mei.ACCID).get('accid') == 'n'

        assert actual[6].find(mei.ACCID).get('accid') == 's'
        assert actual[7].find(mei.ACCID) is None

        assert actual[8].find(mei.ACCID).get('accid') == 'ff'
        assert actual[9].find(mei.ACCID).get('accid') == 's'

    def test_measure(self):
        '''
        The same five cases above, but with a barline between each pair of notes.
        '''
        lilypond_source = '''
            c1 c1
            d1 dis1
            es1 e1
            fis1 fis1
            geses1 gis1
        '''
        l_layer = parser.parse(lilypond_source, rule_name='unmarked_layer')
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_layer(l_layer, m_layer, 1)

        assert actual[0].find(mei.ACCID) is None
        assert actual[1].find(mei.ACCID) is None

        assert actual[2].find(mei.ACCID) is None
        assert actual[3].find(mei.ACCID).get('accid') == 's'

        assert actual[4].find(mei.ACCID).get('accid') == 'f'
        assert actual[5].find(mei.ACCID) is None

        assert actual[6].find(mei.ACCID).get('accid') == 's'
        assert actual[7].find(mei.ACCID).get('accid') == 's'

        assert actual[8].find(mei.ACCID).get('accid') == 'ff'
        assert actual[9].find(mei.ACCID).get('accid') == 's'

    def test_chords(self):
        '''
        The same five cases above, but each note in a chord.
        '''
        lilypond_source = '''
            <c f>2 <c g b>2
            <d as>2 <dis e>2
            <es g>2 <e f>2
            <fis a>2 <fis g>2
            <geses c'>2 <gis d>2
        '''
        l_layer = parser.parse(lilypond_source, rule_name='unmarked_layer')
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_layer(l_layer, m_layer, 1)

        assert actual[0][0].find(mei.ACCID) is None
        assert actual[1][0].find(mei.ACCID) is None

        assert actual[2][0].find(mei.ACCID) is None
        assert actual[3][0].find(mei.ACCID).get('accid') == 's'

        assert actual[4][0].find(mei.ACCID).get('accid') == 'f'
        assert actual[5][0].find(mei.ACCID).get('accid') == 'n'

        assert actual[6][0].find(mei.ACCID).get('accid') == 's'
        assert actual[7][0].find(mei.ACCID) is None

        assert actual[8][0].find(mei.ACCID).get('accid') == 'ff'
        assert actual[9][0].find(mei.ACCID).get('accid') == 's'

    def test_interruption(self):
        '''
        The same five cases above, but with another object in between each pair of notes.

        This ensures that rests, spacers, and other notes don't interfere with other notes.
        '''
        lilypond_source = '''
            c4 r4 c2
            d4 e4 dis2
            es4 c4 e2
            fis4 s4 fis2
            geses4 a4 gis2
        '''
        l_layer = parser.parse(lilypond_source, rule_name='unmarked_layer')
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_layer(l_layer, m_layer, 1)

        assert actual[0].find(mei.ACCID) is None
        assert actual[2].find(mei.ACCID) is None

        assert actual[3].find(mei.ACCID) is None
        assert actual[5].find(mei.ACCID).get('accid') == 's'

        assert actual[6].find(mei.ACCID).get('accid') == 'f'
        assert actual[8].find(mei.ACCID).get('accid') == 'n'

        assert actual[9].find(mei.ACCID).get('accid') == 's'
        assert actual[11].find(mei.ACCID) is None

        assert actual[12].find(mei.ACCID).get('accid') == 'ff'
        assert actual[14].find(mei.ACCID).get('accid') == 's'

    def test_force(self):
        '''
        The same five cases above, but the second accidental in each measure is forced.
        '''
        lilypond_source = '''
            c2 c!2
            d2 dis!2
            es2 e!2
            fis2 fis!2
            geses2 gis!2
        '''
        l_layer = parser.parse(lilypond_source, rule_name='unmarked_layer')
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_layer(l_layer, m_layer, 1)

        assert actual[0].find(mei.ACCID) is None
        assert actual[1].find(mei.ACCID).get('accid') == 'n'

        assert actual[2].find(mei.ACCID) is None
        assert actual[3].find(mei.ACCID).get('accid') == 's'

        assert actual[4].find(mei.ACCID).get('accid') == 'f'
        assert actual[5].find(mei.ACCID).get('accid') == 'n'

        assert actual[6].find(mei.ACCID).get('accid') == 's'
        assert actual[7].find(mei.ACCID).get('accid') == 's'

        assert actual[8].find(mei.ACCID).get('accid') == 'ff'
        assert actual[9].find(mei.ACCID).get('accid') == 's'

    def test_tie_across_barline(self):
        '''
        The same five cases above, but with the first note tying across a barline. In all five
        cases, the tied-in note should display no accidental, but it should affect other notes in
        its bar.

        The exception is case 4, where the note should force an accidental for the next note in the
        bar.
        '''
        lilypond_source = '''
            c1~ c2 c2
            d1~ d2 dis2
            es1~ es2 e2
            fis1~ fis2 fis2
            geses1~ geses2 gis2
        '''
        l_layer = parser.parse(lilypond_source, rule_name='unmarked_layer')
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_layer(l_layer, m_layer, 1)

        assert actual[0].find(mei.ACCID) is None
        assert actual[1].find(mei.ACCID) is None
        assert actual[2].find(mei.ACCID) is None

        assert actual[3].find(mei.ACCID) is None
        assert actual[4].find(mei.ACCID) is None
        assert actual[5].find(mei.ACCID).get('accid') == 's'

        assert actual[6].find(mei.ACCID).get('accid') == 'f'
        assert actual[7].find(mei.ACCID) is None
        assert actual[8].find(mei.ACCID).get('accid') == 'n'

        assert actual[9].find(mei.ACCID).get('accid') == 's'
        assert actual[10].find(mei.ACCID) is None
        assert actual[11].find(mei.ACCID).get('accid') == 's'

        assert actual[12].find(mei.ACCID).get('accid') == 'ff'
        assert actual[13].find(mei.ACCID) is None
        assert actual[14].find(mei.ACCID).get('accid') == 's'
