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
for the code that translated Grako's parse into Lychee-MEI.
"""

from __future__ import unicode_literals

from lxml import etree
import pytest

from lychee.converters.inbound import lilypond
from lychee import exceptions
from lychee.namespaces import mei


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
        l_score = {'ly_type': 'score',
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
        l_score = {'ly_type': 'score',
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
        l_score = {'ly_type': 'score',
            'staves': [{
                'ly_type': 'staff',
                'initial_settings': [{'ly_type': 'instr_name', 'name': 'Woo'}],
                'content': [{'layers': [[{'pitch_name': 'css', 'oct': ',',
                             'accid_force': None, 'dur': '4', 'dots': [], 'ly_type': 'note'}]]}],
            }]
        }
        actual = lilypond.do_score(l_score, context={'language': 'english'})
        note = actual.find('.//{}'.format(mei.NOTE))
        assert note.attrib.get('accid.ges') == 'ss'


class TestClef(object):
    """
    Setting the clef.
    """

    def test_invalid_clef(self):
        """The input isn't a clef."""
        l_time = {'ly_type': '', 'type': ''}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        with pytest.raises(exceptions.LilyPondError):
            lilypond.set_initial_clef(l_time, m_staffdef)

    def test_nonexistent_clef(self):
        """The clef type doesn't exist."""
        l_time = {'ly_type': 'clef', 'type': 'bullshit'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_initial_clef(l_time, m_staffdef)
        assert m_staffdef.get('clef.shape') is None
        assert m_staffdef.get('clef.line') is None

    def test_works(self):
        """It works."""
        l_time = {'ly_type': 'clef', 'type': 'bass'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_initial_clef(l_time, m_staffdef)
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
            lilypond.set_initial_time(l_time, m_staffdef)

    def test_works(self):
        """You know..."""
        l_time = {'ly_type': 'time', 'count': '23', 'unit': '64'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_initial_time(l_time, m_staffdef)
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
            lilypond.set_initial_key(l_key, m_staffdef)

    def test_major_key(self):
        """Major key."""
        l_key = {'ly_type': 'key', 'keynote': 'des', 'mode': 'major'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_initial_key(l_key, m_staffdef)
        assert m_staffdef.get('key.sig') == '5f'

    def test_minor_key(self):
        """Minor key."""
        l_key = {'ly_type': 'key', 'keynote': 'a', 'mode': 'minor'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_initial_key(l_key, m_staffdef)
        assert m_staffdef.get('key.sig') == '0'

    def test_language(self):
        """English language."""
        l_key = {'ly_type': 'key', 'keynote': 'ds', 'mode': 'minor'}
        m_staffdef = etree.Element(mei.STAFF_DEF)
        lilypond.set_initial_key(l_key, m_staffdef, context={'language': 'english'})
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

        assert m_staffdef.attrib == {'n': '8'}

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

        assert m_staffdef.attrib == {'n': '8', 'meter.count': '3', 'meter.unit': '4'}

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
                {'layers': [[{'pitch_name': 'bes', 'oct': ',', 'accid_force': None,
                             'dur': '128', 'dots': [], 'ly_type': 'note'}]],
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
                {'pitch_name': 'des', 'oct': ',,', 'accid_force': '!'},
                {'pitch_name': 'fis', 'oct': ',,', 'accid_force': None},
                {'pitch_name': 'a', 'oct': ',,', 'accid_force': None},
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


class TestPitchName(object):
    """
    For pitch name handling.
    """

    def test_no_accid(self):
        """When there is no accidental."""
        l_pitch_name = "c"
        attrib = {}
        expected = {"pname": "c"}
        actual = lilypond.process_pitch_name(l_pitch_name, attrib)
        assert expected == actual

    def test_double_sharp(self):
        """Double sharp."""
        l_pitch_name = "cisis"
        attrib = {}
        expected = {"pname": "c", "accid.ges": "ss"}
        actual = lilypond.process_pitch_name(l_pitch_name, attrib)
        assert expected == actual

    def test_single_flat(self):
        """Single flat."""
        l_pitch_name = "ees"
        attrib = {}
        expected = {"pname": "e", "accid.ges": "f"}
        actual = lilypond.process_pitch_name(l_pitch_name, attrib)
        assert expected == actual

    def test_language(self):
        """German."""
        l_pitch_name = "h"
        attrib = {}
        context = {"language": "deutsch"}
        expected = {"pname": "b", "accid.ges": "f"}
        actual = lilypond.process_pitch_name(l_pitch_name, attrib, context)
        assert expected == actual

    def test_sharpflat(self):
        """Sharpflat (invalid accidental)."""
        l_pitch_name = "cises"
        attrib = {}
        with pytest.raises(exceptions.LilyPondError):
            lilypond.process_pitch_name(l_pitch_name, attrib)


class TestForcedAccidentals(object):
    """
    For the forced accidental stuff.
    """

    def test_dont_add_it(self):
        """The note doesn't have a forced accidental."""
        l_note = {'accid_force': None}  # this is enough to trick it
        attrib = {}

        actual = lilypond.process_forced_accid(l_note, attrib)

        assert actual == {}

    def test_add_a_flat(self):
        """The note has a forced flat."""
        l_note = {'accid_force': '!'}  # this is enough to trick it
        attrib = {'accid.ges': 'f'}

        actual = lilypond.process_forced_accid(l_note, attrib)

        assert actual == {'accid.ges': 'f', 'accid': 'f'}

    def test_add_a_natural(self):
        """The note has a forced natural."""
        l_note = {'accid_force': '!'}  # this is enough to trick it
        attrib = {'dur': '4'}  # check it doesn't erase unrelated keys

        actual = lilypond.process_forced_accid(l_note, attrib)

        assert actual == {'dur': '4', 'accid': 'n'}


class TestCautionaryAccidentals(object):
    """
    For the cautionary accidental garbage.
    """

    def test_dont_add_it(self):
        """The note doesn't have a cautionary accidental."""
        l_note = {'accid_force': None}  # this is enough to trick it
        m_note = etree.Element(mei.NOTE)

        actual = lilypond.process_caut_accid(l_note, m_note)

        assert len(actual) == 0  # includes child elements only

    def test_add_a_flat(self):
        """The note has a cautionary flat."""
        l_note = {'accid_force': '?'}  # this is enough to trick it
        m_note = etree.Element(mei.NOTE, {'accid.ges': 'f'})

        actual = lilypond.process_caut_accid(l_note, m_note)

        assert len(actual) == 1  # includes child elements only
        assert actual[0].tag == mei.ACCID
        assert actual[0].get('accid') == 'f'
        assert actual[0].get('func') == 'caution'

    def test_add_a_natural(self):
        """The note has a cautionary natural."""
        l_note = {'accid_force': '?'}  # this is enough to trick it
        m_note = etree.Element(mei.NOTE)

        actual = lilypond.process_caut_accid(l_note, m_note)

        assert len(actual) == 1  # includes child elements only
        assert actual[0].tag == mei.ACCID
        assert actual[0].get('accid') == 'n'
        assert actual[0].get('func') == 'caution'


class TestProcesssDots(object):
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
            {'pitch_name': 'des', 'oct': ',,', 'accid_force': '?'},
        ]}
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_chord(l_chord, m_layer)

        assert len(actual) == 1
        assert actual[0].get('pname') == 'd'
        assert actual[0].get('oct') == '1'
        assert actual[0].get('accid.ges') == 'f'
        assert actual[0][0].tag == mei.ACCID
        assert actual[0][0].get('accid') == 'f'

    def test_three_noteheads(self):
        """When the chord has three noteheads, the first with a forced accidental."""
        l_chord = {'ly_type': 'chord', 'dur': '2', 'dots': ['.'], 'notes': [
            {'pitch_name': 'des', 'oct': ',,', 'accid_force': '!'},
            {'pitch_name': 'fis', 'oct': ',,', 'accid_force': None},
            {'pitch_name': 'a', 'oct': ',,', 'accid_force': None},
        ]}
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_chord(l_chord, m_layer)

        assert len(actual) == 3
        #
        assert actual[0].get('pname') == 'd'
        assert actual[0].get('oct') == '1'
        assert actual[0].get('accid.ges') == 'f'
        assert actual[0].get('accid') == 'f'
        #
        assert actual[1].get('pname') == 'f'
        assert actual[1].get('oct') == '1'
        assert actual[1].get('accid.ges') == 's'
        assert actual[1].get('accid') is None
        #
        assert actual[2].get('pname') == 'a'
        assert actual[2].get('oct') == '1'
        assert actual[2].get('accid.ges') is None
        assert actual[2].get('accid') is None

    def test_language(self):
        """Italiano."""
        l_chord = {'ly_type': 'chord', 'dur': '2', 'dots': [], 'notes': [
            {'pitch_name': 'do', 'oct': '', 'accid_force': '!'},
            {'pitch_name': 'red', 'oct': '', 'accid_force': None},
            {'pitch_name': 'mibb', 'oct': '', 'accid_force': None},
        ]}
        m_layer = etree.Element(mei.LAYER)
        context = {'language': 'italiano'}
        actual = lilypond.do_chord(l_chord, m_layer, context)

        assert len(actual) == 3
        #
        assert actual[0].get('pname') == 'c'
        assert actual[0].get('oct') == '3'
        assert actual[0].get('accid.ges') is None
        assert actual[0].get('accid') == 'n'
        #
        assert actual[1].get('pname') == 'd'
        assert actual[1].get('oct') == '3'
        assert actual[1].get('accid.ges') == 's'
        assert actual[1].get('accid') is None
        #
        assert actual[2].get('pname') == 'e'
        assert actual[2].get('oct') == '3'
        assert actual[2].get('accid.ges') == 'ff'
        assert actual[2].get('accid') is None


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

        assert actual.get('accid.ges') == 's'
        assert actual.get('accid') == 's'
        assert actual.get('dots') == '2'

    def test_children(self):
        """Note has sub-elements added by process_x() functions after Element creation."""
        l_note = {'ly_type': 'note', 'pitch_name': 'fis', 'oct': "''", 'accid_force': '?',
            'dur': '256', 'dots': []}
        m_layer = etree.Element(mei.LAYER)
        actual = lilypond.do_note(l_note, m_layer)

        assert actual.get('accid.ges') == 's'
        assert actual.get('accid') is None
        assert actual[0].tag == mei.ACCID


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
