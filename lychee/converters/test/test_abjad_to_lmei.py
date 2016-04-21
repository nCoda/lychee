#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/test/test_abjad_to_lmei.py
# Purpose:                Tests conversion from abjad to lmei.
#
# Copyright (C) 2016 Jeffrey Treviño, Christopher Antila
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
from lxml import etree
import pytest
from abjad.tools.indicatortools import Clef
from abjad.tools.scoretools.Note import Note
from abjad.tools.scoretools.Rest import Rest
from abjad.tools.scoretools.Chord import Chord
from abjad.tools.scoretools.Skip import Skip
from abjad.tools.scoretools.Measure import Measure
from abjad.tools.scoretools.NoteHead import NoteHead
from abjad.tools.scoretools.FixedDurationTuplet import FixedDurationTuplet
from abjad.tools.scoretools.Tuplet import Tuplet
from abjad.tools.durationtools.Duration import Duration
from abjad.tools.durationtools.Multiplier import Multiplier
from abjad.tools.scoretools.Voice import Voice
from abjad.tools.scoretools.Staff import Staff
from abjad.tools.scoretools.StaffGroup import StaffGroup
from abjad.tools.scoretools.Score import Score
from abjad.tools.topleveltools.inspect_ import inspect_
from abjad.tools.topleveltools.attach import attach
from lychee.converters import abjad_to_lmei
from lychee import exceptions
from lychee.namespaces import mei, xml
import unittest
import abjad_test_case

try:
    from unittest import mock
except ImportError:
    import mock


class TestAddXmlIds(object):
    '''
    Tests for add_xml_ids().
    '''

    def test_sameness(self):
        '''
        When different Python objects are inputted but share the same music data, the generated ID
        is the same both times.
        '''
        note_1 = Note("d,,2")
        note_2 = Note("d,,2")
        elem_1 = etree.Element(mei.NOTE)
        elem_2 = elem_1.makeelement(mei.NOTE)

        abjad_to_lmei.add_xml_ids(note_1, elem_1)
        abjad_to_lmei.add_xml_ids(note_2, elem_2)

        assert elem_1.get(xml.ID) == elem_2.get(xml.ID)

    def test_difference(self):
        '''
        When the same Python objects are inputted but have different music data, the generated ID
        is different each time.
        '''
        note = Note("d,,2")
        elem = etree.Element(mei.NOTE)
        abjad_to_lmei.add_xml_ids(note, elem)
        xmlid_1 = elem.get(xml.ID)

        elem.tag = mei.REST
        abjad_to_lmei.add_xml_ids(note, elem)
        xmlid_2 = elem.get(xml.ID)

        assert xmlid_1 != xmlid_2

    def test_n_attr(self):
        '''
        A different @n attribute is sufficient to produce different @xml:id values.
        '''
        note_1 = Note("d,,2")
        note_2 = Note("d,,2")
        elem_1 = etree.Element(mei.NOTE, {'n': '1'})
        elem_2 = elem_1.makeelement(mei.NOTE, {'n': '2'})

        abjad_to_lmei.add_xml_ids(note_1, elem_1)
        abjad_to_lmei.add_xml_ids(note_2, elem_2)

        assert elem_1.get(xml.ID) != elem_2.get(xml.ID)

    def test_underfull_container(self):
        '''
        When given an underfull container, we should still be able to produce an @xml:id for it.
        '''
        a_meas = Measure((4, 4), "{}")
        m_meas = etree.Element(mei.MEASURE)

        abjad_to_lmei.add_xml_ids(a_meas, m_meas)

        assert m_meas.get(xml.ID) is not None


class TestLeafToElement(abjad_test_case.AbjadTestCase):
    '''
    Tests for leaf_to_element().
    '''

    def test_is_a_leaf(self):
        '''
        When the Abjad object is indeed a "leaf" object, it is converted.
        '''
        a_note = Note("es'8")
        m_note = abjad_to_lmei.leaf_to_element(a_note)
        assert m_note.tag == mei.NOTE

    def test_not_a_lef(self):
        '''
        When the Abjad object is not a "leaf" object, InboundConversionError is raised.
        '''
        a_staff = Staff()
        with pytest.raises(exceptions.InboundConversionError) as exc:
            abjad_to_lmei.leaf_to_element(a_staff)
        assert exc.value.args[0] == abjad_to_lmei._NOT_A_LEAF_NODE.format(str(type(a_staff)))


class TestMeasureToMeasure(abjad_test_case.AbjadTestCase):
    '''
    Tests for measure_to_measure().
    '''

    def test_meticulous_basic_stuff(self):
        '''
        Abjad Measure with four Notes, make sure it's perfectly correct.

        Assert the outputted element:
        - has the right tag
        - has @n of 1
        - has an @xml:id set
        - has a single <layer> child element...
        - ... with @n of 1...
        - ... and four <note> child elements
        '''
        a_meas = Measure((4, 4), "c'4 d'4 e'4 f'4")
        m_meas = abjad_to_lmei.measure_to_measure(a_meas)

        assert m_meas.tag == mei.MEASURE
        assert m_meas.get('n') == '1'
        assert m_meas.get(xml.ID) is not None
        assert len(m_meas) == 1
        m_layer = m_meas[0]
        assert m_layer.tag == mei.LAYER
        assert m_layer.get('n') == '1'
        assert m_layer.get(xml.ID) is not None
        assert len(m_layer) == 4
        for m_note in m_layer:
            assert m_note.tag == mei.NOTE

    def test_meticulous_empty(self):
        '''
        Emtpy Abjad Measure.

        Assert the outputted element:
        - has the right tag
        - has @n of 1
        - has an @xml:id set
        - has a single <layer> child element...
        - ... with @n of 1...
        - ... and nothing inside
        '''
        a_meas = Measure((4, 4))
        m_meas = abjad_to_lmei.measure_to_measure(a_meas)

        assert m_meas.tag == mei.MEASURE
        assert m_meas.get('n') == '1'
        assert m_meas.get(xml.ID) is not None
        assert len(m_meas) == 1
        m_layer = m_meas[0]
        assert m_layer.tag == mei.LAYER
        assert m_layer.get('n') == '1'
        assert m_layer.get(xml.ID) is not None
        assert len(m_layer) == 0


class TestStaffToStaff(abjad_test_case.AbjadTestCase):
    '''
    Tests for staff_to_staff().
    '''

    def test_empty(self):
        '''
        precondition: empty abjad Staff
        postcondition: empty mei layer Element
        '''
        abjad_staff = Staff()

        mei_staff = abjad_to_lmei.staff_to_staff(abjad_staff)

        assert mei_staff.tag == mei.STAFF
        assert mei_staff.get(xml.ID) is None
        assert mei_staff.get('n') is None
        assert len(mei_staff) == 0

    # staff with one voice
    def test_one_voice(self):
        '''
        precondition: abjad Staff containing only one Voice
        postcondition: mei staff Element containing one layer Element
        '''
        voice = Voice("r4 c'4 <c' d'>4")
        abjad_staff = Staff([voice])

        mei_staff = abjad_to_lmei.staff_to_staff(abjad_staff)

        assert mei_staff.tag == mei.STAFF
        assert mei_staff.get(xml.ID) is None
        assert mei_staff.get('n') is None
        assert len(mei_staff) == 1
        assert mei_staff[0].tag == mei.LAYER

    @mock.patch("lychee.converters.abjad_to_lmei.voice_to_layer")
    def test_one_voice_mock(self,mock_layer):
        '''
        precondition: abjad Staff containing only one Voice
        postcondition: mei staff Element containing one layer Element
        '''
        voice = Voice("r4 c'4 <c' d'>4")
        abjad_staff = Staff([voice])
        mock_layer.return_value = etree.Element(mei.LAYER)

        mei_staff = abjad_to_lmei.staff_to_staff(abjad_staff)

        assert mei_staff.tag == mei.STAFF
        assert mei_staff.get(xml.ID) is None
        assert mei_staff.get('n') is None
        assert len(mei_staff) == 1
        assert mei_staff[0].tag == mei.LAYER

    # staff with parallel voices (enumerate n based on staff n)
    def test_parallel(self):
        '''
        precondition: abjad Staff containing two or more parallel voices
        postcondition: mei staff Element containing two or more layer Elements
        '''
        voice_one = Voice("r4 c'4 <c' d'>4")
        voice_two = Voice("r4 d'4 <d' e'>4")
        abjad_staff = Staff([voice_one, voice_two])
        abjad_staff.is_simultaneous = True

        mei_staff = abjad_to_lmei.staff_to_staff(abjad_staff)

        assert len(mei_staff) == 2
        assert mei_staff[0].tag == mei.LAYER
        assert mei_staff[0].get('n') == '1'
        assert mei_staff[1].tag == mei.LAYER
        assert mei_staff[1].get('n') == '2'

    @mock.patch("lychee.converters.abjad_to_lmei.voice_to_layer")
    def test_parallel_mock(self,mock_layer):
        '''
        precondition: abjad Staff containing two or more parallel voices
        postcondition: mei staff Element containing two or more layer Elements
        '''
        voice_one = Voice("r4 c'4 <c' d'>4")
        voice_two = Voice("r4 d'4 <d' e'>4")
        abjad_staff = Staff([voice_one, voice_two])
        abjad_staff.is_simultaneous = True
        mock_layer.side_effect = lambda x: etree.Element(mei.LAYER)

        mei_staff = abjad_to_lmei.staff_to_staff(abjad_staff)

        assert len(mei_staff) == 2
        assert mei_staff[0].tag == mei.LAYER
        assert mei_staff[0].get('n') == '1'
        assert mei_staff[1].tag == mei.LAYER
        assert mei_staff[1].get('n') == '2'

    # staff with consecutive voices
    def test_consecutive(self):
        '''
        precondition: abjad Staff containing two or more consecutive Voices
        postcondition: mei staff Element containing one layer Element
        '''
        voice_one = Voice("r4 c'4 <c' d'>4")
        voice_two = Voice("r4 d'4 <d' e'>4")
        abjad_staff = Staff([voice_one, voice_two])

        mei_staff = abjad_to_lmei.staff_to_staff(abjad_staff)

        assert len(mei_staff) == 1
        assert mei_staff[0].tag == mei.LAYER
        assert mei_staff[0].get('n') == '1'

    @mock.patch("lychee.converters.abjad_to_lmei.voice_to_layer")
    def test_consecutive_mock(self,mock_layer):
        '''
        precondition: abjad Staff containing two or more consecutive Voices
        postcondition: mei staff Element containing one layer Element
        '''
        voice_one = Voice("r4 c'4 <c' d'>4")
        voice_two = Voice("r4 d'4 <d' e'>4")
        abjad_staff = Staff([voice_one, voice_two])
        mock_layer.return_value = etree.Element(mei.LAYER, n='1')

        mei_staff = abjad_to_lmei.staff_to_staff(abjad_staff)

        assert len(mei_staff) == 1
        assert mei_staff[0].tag == mei.LAYER
        assert mei_staff[0].get('n') == '1'

    # staff with leaves and no voice(s)
    def test_leaves(self):
        '''
        precondition: abjad Staff containing leaves and no Voices
        postcondition: mei layer Element containing children leaf Elements
        '''
        abjad_staff = Staff("r4 c'4 <c' d'>4")

        mei_staff = abjad_to_lmei.staff_to_staff(abjad_staff)

        assert len(mei_staff) == 1
        assert mei_staff[0].tag == mei.LAYER
        assert mei_staff[0].get('n') == '1'

    @mock.patch("lychee.converters.abjad_to_lmei.voice_to_layer")
    def test_leaves_mock(self, mock_layer):
        '''
        precondition: abjad Staff containing leaves and no Voices
        postcondition: mei layer Element containing children leaf Elements
        '''
        abjad_staff = Staff("r4 c'4 <c' d'>4")
        mock_layer.return_value = etree.Element(mei.LAYER, n='1')

        mei_staff = abjad_to_lmei.staff_to_staff(abjad_staff)

        assert len(mei_staff) == 1
        assert mei_staff[0].tag == mei.LAYER
        assert mei_staff[0].get('n') == '1'

    # staff with some combination of leaves and voices
    def test_leaves_and_voices(self):
        '''
        precondition: abjad Staff containing both leaves and Voices as siblings
        postcondition: mei staff Element containing one layer Element
        '''
        abjad_staff = Staff("r4 c'4")
        voice = Voice("r4 c'4")
        abjad_staff.append(voice)
        abjad_staff.append("<c' d'>4")
        voice_two = Voice("r4 d'4")
        abjad_staff.append(voice_two)
        abjad_staff.append(Note("c''4"))

        mei_staff = abjad_to_lmei.staff_to_staff(abjad_staff)

        assert len(mei_staff) == 1
        assert mei_staff[0].tag == mei.LAYER
        assert mei_staff[0].get('n') == '1'
        assert len(mei_staff[0]) == 8

    @mock.patch("lychee.converters.abjad_to_lmei.voice_to_layer")
    def test_leaves_and_voices_mock(self, mock_layer):
        '''
        precondition: abjad Staff containing both leaves and Voices as siblings
        postcondition: mei staff Element containing one layer Element with eight siblings
        '''
        abjad_staff = Staff("r4 c'4")
        voice_one = Voice("r4 c'4")
        abjad_staff.append(voice_one)
        abjad_staff.append("<c' d'>4")
        voice_two = Voice("r4 d'4")
        abjad_staff.append(voice_two)
        abjad_staff.append(Note("c''4"))
        dummy = etree.Element(mei.LAYER,n='1')
        for _ in range(8):
            etree.SubElement(dummy, mei.NOTE)
        mock_layer.return_value = dummy

        mei_staff = abjad_to_lmei.staff_to_staff(abjad_staff)

        assert mock_layer.call_count == 1
        assert len(mei_staff) == 1
        assert mei_staff[0].tag == mei.LAYER
        assert mei_staff[0].get('n') == '1'
        assert len(mei_staff[0]) == 8

    def test_measures(self):
        '''
        precondition: abjad Staff that contains a series of Measure objects
        postcondition: MEI <staff> element contains a series of <measure> elements
        '''
        a_staff = Staff([
            Measure((4, 4), "c'4 d'4 e'4 f'4"),
            Measure((4, 4), "e'4 f'4 e'4 f'4"),
        ])

        m_staff = abjad_to_lmei.staff_to_staff(a_staff)

        etree.dump(m_staff)


class TestSetInitialClef(abjad_test_case.AbjadTestCase):
    '''
    Tests for set_initial_clef().
    '''

    def test_no_clef(self):
        '''
        When there is no clef, expect do nothing.
        '''
        staff = Staff([Measure((2, 2), "f1")])
        scoredef = etree.Element(mei.SCORE_DEF)
        abjad_to_lmei.set_initial_clef(staff, scoredef)
        assert scoredef.get('clef.shape') is None
        assert scoredef.get('clef.line') is None

    def test_unknown_clef(self):
        '''
        When there is a currently-unknown clef, expect do nothing.
        '''
        staff = Staff([Measure((2, 2), "f1")])
        attach(Clef('soprano'), staff)
        scoredef = etree.Element(mei.SCORE_DEF)
        abjad_to_lmei.set_initial_clef(staff, scoredef)
        assert scoredef.get('clef.shape') is None
        assert scoredef.get('clef.line') is None

    def test_treble_clef(self):
        '''
        When there is a treble clef, put it in.
        '''
        staff = Staff([Measure((2, 2), "f1")])
        attach(Clef('treble'), staff)
        scoredef = etree.Element(mei.SCORE_DEF)
        abjad_to_lmei.set_initial_clef(staff, scoredef)
        assert scoredef.get('clef.shape') == 'G'
        assert scoredef.get('clef.line') == '2'

    def test_alto_clef(self):
        '''
        When there is an alto clef, put it in.
        '''
        staff = Staff([Measure((2, 2), "f1")])
        attach(Clef('alto'), staff)
        scoredef = etree.Element(mei.SCORE_DEF)
        abjad_to_lmei.set_initial_clef(staff, scoredef)
        assert scoredef.get('clef.shape') == 'C'
        assert scoredef.get('clef.line') == '3'

    def test_tenor_clef(self):
        '''
        When there is a tenor clef, put it in.
        '''
        staff = Staff([Measure((2, 2), "f1")])
        attach(Clef('tenor'), staff)
        scoredef = etree.Element(mei.SCORE_DEF)
        abjad_to_lmei.set_initial_clef(staff, scoredef)
        assert scoredef.get('clef.shape') == 'C'
        assert scoredef.get('clef.line') == '4'

    def test_bass_clef(self):
        '''
        When there is a bass clef, put it in.
        '''
        staff = Staff([Measure((2, 2), "f1")])
        attach(Clef('bass'), staff)
        scoredef = etree.Element(mei.SCORE_DEF)
        abjad_to_lmei.set_initial_clef(staff, scoredef)
        assert scoredef.get('clef.shape') == 'F'
        assert scoredef.get('clef.line') == '4'


class TestAbjadToLmeiConversions(abjad_test_case.AbjadTestCase):

    # note conversion

    def test_note_basic(self):
        '''
        precondition: abjad note with duration, pitch name, and octave string
        postcondition: mei element
        '''
        abjad_note = Note("c'4")
        mei_note = abjad_to_lmei.note_to_note(abjad_note)
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(mei_note.attrib, {'dur': '4', 'pname': 'c', 'oct': '4'})
        self.assertIsNotNone(mei_note.get(xml.ID))

    def test_note_dotted(self):
        '''
        precondition: abjad note with dot
        postcondition: mei element with dots attribute
        '''
        abjad_note = Note("c'4.")
        mei_note = abjad_to_lmei.note_to_note(abjad_note)
        self.assertIsNotNone(mei_note.get(xml.ID))
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(mei_note.attrib, {'dots': '1', 'dur': '4', 'pname': 'c', 'oct': '4'})

    def test_note_accid(self):
        '''
        precondition: abjad note with accidental, neither forced nor cautionary
        postcondition: mei element with gestural accidental
        '''
        abjad_note = Note("cf'4")
        mei_note = abjad_to_lmei.note_to_note(abjad_note)
        self.assertIsNotNone(mei_note.get(xml.ID))
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(mei_note.attrib, {'accid.ges': 'f', 'dur': '4', 'pname': 'c', 'oct': '4'})

    def test_note_accid_and_cautionary(self):
        '''
        preconditions: abjad note with cautionary accidental
        postconditions: mei element containing cautionary accidental subelement
        '''
        abjad_note = Note("cf'?4")
        mei_note = abjad_to_lmei.note_to_note(abjad_note)
        self.assertAttribsEqual(mei_note.attrib, {'dur': '4', 'pname': 'c', 'oct': '4'})
        accid = mei_note.findall('./'+mei.ACCID)
        accid = accid[0]
        self.assertIsNotNone(mei_note.get(xml.ID))
        self.assertEqual(accid.tag, mei.ACCID)
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(accid.attrib, {'accid': 'f', 'func': 'cautionary'})

    def test_note_accid_and_forced(self):
        '''
        preconditions: abjad note with forced accidental
        postconditions: mei element with both written and gestural accidentals
        '''
        abjad_note = Note("cf'!4")
        mei_note = abjad_to_lmei.note_to_note(abjad_note)
        self.assertIsNotNone(mei_note.get(xml.ID))
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(mei_note.attrib, {'accid.ges': 'f', 'accid': 'f', 'dur': '4', 'pname': 'c', 'oct': '4'})

    def test_note_cautionary(self):
        '''
        precondition: abjad note with no accidental and cautionary natural
        postcondition: mei element containing cautionary accidental subelement set to natural
        '''
        abjad_note = Note("c'?4")
        mei_note = abjad_to_lmei.note_to_note(abjad_note)
        self.assertAttribsEqual(mei_note.attrib, {'dur': '4', 'pname': 'c', 'oct': '4'})
        accid = mei_note.findall('./' + mei.ACCID)
        accid = accid[0]
        self.assertEqual(accid.tag, mei.ACCID)
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(accid.attrib, {'accid': 'n', 'func': 'cautionary'})
        self.assertIsNotNone(mei_note.get(xml.ID))

    def test_note_forced(self):
        '''
        precondition: abjad note with no accidental and forced accidental
        postcondition: mei element with both accid.ges and accid attributes set
        '''
        abjad_note = Note("c'!4")
        mei_note = abjad_to_lmei.note_to_note(abjad_note)
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(mei_note.attrib, {'accid.ges': 'n', 'accid': 'n', 'dur': '4', 'pname': 'c', 'oct': '4'} )
        self.assertIsNotNone(mei_note.get(xml.ID))

    def test_notehead(self):
        '''
        precondition: Abjad NoteHead
        postcondition: mei note
        '''
        head = NoteHead("c'")
        mei_note = abjad_to_lmei.note_to_note(head)
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(mei_note.attrib, {'pname': 'c', 'oct': '4'})

    def test_notehead_cautionary(self):
        '''
        precondition: Abjad NoteHead with cautionary natural
        postcondition: mei note Element with cautionary natural
        '''
        head = NoteHead("c'")
        head.is_cautionary = True
        mei_note = abjad_to_lmei.note_to_note(head)
        self.assertAttribsEqual(mei_note.attrib, {'pname': 'c', 'oct': '4'})
        accid = mei_note.findall('./' + mei.ACCID)
        accid = accid[0]
        self.assertEqual(accid.tag, mei.ACCID)
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(accid.attrib, {'accid': 'n', 'func': 'cautionary'})

    def test_notehead_forced(self):
        head = NoteHead("c'")
        head.is_forced = True
        mei_note = abjad_to_lmei.note_to_note(head)
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(mei_note.attrib, {'pname': 'c', 'oct': '4', 'accid.ges': 'n', 'accid': 'n'})

    def test_notehead_accid(self):
        '''
        precondition: abjad NoteHead with accidental
        postcondition: mei note Element with accidental
        '''
        head = NoteHead("cf'")
        mei_note = abjad_to_lmei.note_to_note(head)
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(mei_note.attrib, {'pname': 'c', 'oct': '4', 'accid.ges': 'f'})

    def test_notehead_accid_cautionary(self):
        '''
        precondition: Abjad NoteHead with cautionary accidental
        postcondition: mei note Element with cautionary accidental
        '''
        head = NoteHead("cf'")
        head.is_cautionary = True
        mei_note = abjad_to_lmei.note_to_note(head)
        self.assertAttribsEqual(mei_note.attrib, {'pname': 'c', 'oct': '4'})
        accid = mei_note.findall('./' + mei.ACCID)
        accid = accid[0]
        self.assertEqual(accid.tag, mei.ACCID)
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(accid.attrib, {'accid': 'f', 'func': 'cautionary'})

    def test_notehead_accid_forced(self):
        head = NoteHead("cf'")
        head.is_forced = True
        mei_note = abjad_to_lmei.note_to_note(head)
        self.assertEqual(mei_note.tag, mei.NOTE)
        self.assertAttribsEqual(mei_note.attrib, {'pname': 'c', 'oct': '4', 'accid.ges': 'f', 'accid': 'f'})

    def test_rest(self):
        '''
        precondition: abjad Rest with no dots.
        postcondition: mei rest Element with no dots.
        '''
        abjad_rest = Rest("r32")

        mei_rest = abjad_to_lmei.rest_to_rest(abjad_rest)

        self.assertEqual(mei_rest.tag, mei.REST)
        self.assertAttribsEqual(mei_rest.attrib, {'dur': '32'} )
        self.assertIsNotNone(mei_rest.get(xml.ID))

    def test_rest_dotted(self):
        '''
        precondition: dotted abjad Rest.
        postcondition: dotted mei rest Element.
        '''
        abjad_rest = Rest("r32..")

        mei_rest = abjad_to_lmei.rest_to_rest(abjad_rest)

        self.assertEqual(mei_rest.tag, mei.REST)
        self.assertAttribsEqual(mei_rest.attrib, {'dots': '2', 'dur': '32'})
        self.assertIsNotNone(mei_rest.get(xml.ID))

    def test_skip_to_space(self):
        '''
        precondition: abjad Skip with no dots.
        postcondition: mei space Element with no dots.
        '''
        abjad_skip = Skip("s32")

        mei_space = abjad_to_lmei.skip_to_space(abjad_skip)

        self.assertEqual(mei_space.tag, mei.SPACE)
        self.assertAttribsEqual(mei_space.attrib, {'dur': '32'} )
        self.assertIsNotNone(mei_space.get(xml.ID))

    def test_skip_to_space_dotted(self):
        '''
        precondition: dotted abjad Skip.
        postcondition: dotted mei space Element.
        '''
        abjad_skip = Skip("s32..")

        mei_space = abjad_to_lmei.skip_to_space(abjad_skip)

        self.assertEqual(mei_space.tag, mei.SPACE)
        self.assertAttribsEqual(mei_space.attrib, {'dots': '2', 'dur': '32'})
        self.assertIsNotNone(mei_space.get(xml.ID))

    def test_chord_empty(self):
        '''
        precondition: abjad Chord with duration and no NoteHeads
        postcondition: mei chord Element with duration and no contained note Elements
        '''
        abjad_chord = Chord([],(1,4))
        mei_chord = abjad_to_lmei.chord_to_chord(abjad_chord)
        self.assertAttribsEqual(mei_chord.attrib, {'dur': '4'})
        self.assertEqual(mei_chord.tag, mei.CHORD)
        self.assertEqual(len(mei_chord), 0)
        self.assertIsNotNone(mei_chord.get(xml.ID))

    def test_chord_empty_dotted(self):
        '''
        precondition: abjad Chord with dotted duration and no NoteHeads
        postcondition: mei chord Element with dotted duration and no contained note Elements
        '''
        abjad_chord = Chord([],(3,8))
        mei_chord = abjad_to_lmei.chord_to_chord(abjad_chord)
        self.assertAttribsEqual(mei_chord.attrib, {'dur': '4','dots': '1'})
        self.assertEqual(mei_chord.tag, mei.CHORD)
        self.assertEqual(len(mei_chord), 0)
        self.assertIsNotNone(mei_chord.get(xml.ID))

    def test_chord_full(self):
        '''
        precondition: abjad Chord with duration and one or more NoteHeads
        postcondition: mei chord Element with duration and one or more contained note Elements
        '''
        abjad_chord = Chord("<c' d'>4")
        mei_chord = abjad_to_lmei.chord_to_chord(abjad_chord)
        self.assertAttribsEqual(mei_chord.attrib, {'dur': '4'})
        self.assertEqual(mei_chord.tag, mei.CHORD)
        self.assertAttribsEqual(mei_chord[0].attrib, {'pname': 'c', 'oct': '4'})
        self.assertAttribsEqual(mei_chord[1].attrib, {'pname': 'd', 'oct': '4'})
        self.assertIsNotNone(mei_chord.get(xml.ID))

    def test_chord_full_dotted(self):
        '''
        precondition: abjad Chord with dotted duration and one or more NoteHeads
        postcondition: mei chord Element with dotted duration and one or more contained note Elements
        '''
        abjad_chord = Chord("<c' d'>4.")
        mei_chord = abjad_to_lmei.chord_to_chord(abjad_chord)
        self.assertEqual(mei_chord.tag, mei.CHORD)
        self.assertAttribsEqual(mei_chord.attrib, {'dur': '4', 'dots': '1'})
        self.assertAttribsEqual(mei_chord[0].attrib, {'pname': 'c', 'oct': '4'})
        self.assertAttribsEqual(mei_chord[1].attrib, {'pname': 'd', 'oct': '4'})
        self.assertIsNotNone(mei_chord.get(xml.ID))

    def test_voice_to_layer_empty(self):
        '''
        precondition: empty abjad Voice
        postcondition: empty mei layer Element
        '''
        abjad_voice = Voice()
        mei_layer = abjad_to_lmei.voice_to_layer(abjad_voice)
        self.assertEqual(mei_layer.tag, mei.LAYER)
        self.assertAttribsEqual(mei_layer.attrib, {'n': '1'})
        self.assertEqual(len(mei_layer),0)
        self.assertIsNotNone(mei_layer.get(xml.ID))

    def test_voice_to_layer_full(self):
        '''
        precondition: abjad Voice containing rest, note, chord, skip, and Tuplet.
        postcondition: mei layer Element containing rest, note, chord, space, and tupletspan
        '''
        abjad_voice = Voice()
	abjad_voice.append( Tuplet((2,3), "c' c' c'"))
	abjad_voice.append(Skip("s4"))
	mei_layer = abjad_to_lmei.voice_to_layer(abjad_voice)
        self.assertAttribsEqual(mei_layer.attrib, {'n': '1'})
        self.assertEqual(mei_layer.tag, mei.LAYER)
	self.assertEqual(len(mei_layer), 5)
	self.assertEqual(mei_layer[0].tag, mei.TUPLET_SPAN)
	self.assertEqual(mei_layer[-1].tag, mei.SPACE)
	self.assertIsNotNone(mei_layer.get(xml.ID))

    @mock.patch("lychee.converters.abjad_to_lmei.tuplet_to_tupletspan")
    @mock.patch("lychee.converters.abjad_to_lmei.leaf_to_element")
    @mock.patch("lychee.converters.abjad_to_lmei.add_xml_ids")
    def test_voice_to_layer_full_mock(self, mock_xml_id, mock_element, mock_tupletspan):
        '''
        precondition: abjad Voice containing rest, note, chord, skip, and Tuplet.
        postcondition: mei layer Element containing rest, note, chord, space, and tupletspan.
        '''
        abjad_voice = Voice("r4 c'4 <c' d'>4")
	skip = Skip((1,4))
	abjad_voice.append(skip)
	tuplet = Tuplet((2,3), "c' r4 c'")
	abjad_voice.append(tuplet)

        mock_element.return_value = etree.Element(mei.SPACE)


        mei_layer = abjad_to_lmei.voice_to_layer(abjad_voice)
        self.assertAttribsEqual(mei_layer.attrib, {'n': '1'})
        mock_element.assert_called_with(skip)
	mock_tupletspan.assert_called_with(tuplet)
	mock_xml_id.assert_called_with(abjad_voice, mei_layer)

    # inconsistencies:
    # layer added en route to mei; shouldn't be there when translated back to abjad
    # sequential layers flattened into one layer; can't be recuperated
    # measures don't yet exist

    def test_section_empty(self):
        '''
        precondition: empty abjad Score
        postcondition: empty mei section Element
        '''
        abjad_score = Score()
        mei_section = abjad_to_lmei.score_to_section(abjad_score)
        self.assertEqual(mei_section.tag, mei.SECTION)
        self.assertEqual(mei_section.get('n'), '1')
        self.assertEqual(len(mei_section), 0)
        self.assertIsNotNone(mei_section.get(xml.ID))

    def test_section_full(self):
        '''
        precondition: abjad Score containing Staff, StaffGroup containing two Staffs, and Staff
        postcondition: mei section Element containing scoreDef element and four staff Elements
        with staff Elements two and three of four grouped

        '''
        abjad_score = Score()
        abjad_score.append(Staff())
        abjad_score.append( StaffGroup([Staff(), Staff()]) )
        abjad_score.append(Staff())

        mei_section = abjad_to_lmei.score_to_section(abjad_score)

        self.assertEqual(mei_section.tag, mei.SECTION)
        self.assertEqual(len(mei_section), 5)
        self.assertEqual(mei_section[0].tag, mei.SCORE_DEF)
        self.assertEqual(len(mei_section[0]), 1)
        self.assertEqual(mei_section[0][0].tag, mei.STAFF_GRP)
        self.assertEqual(len(mei_section[0][0]), 3)
        self.assertEqual(mei_section[0][0][0].tag, mei.STAFF_DEF)
        self.assertEqual(mei_section[0][0][0].get('lines'), '5')
        self.assertEqual(mei_section[0][0][0].get('n'), '1')
        self.assertEqual(mei_section[0][0][1].tag, mei.STAFF_GRP)
        self.assertEqual(mei_section[0][0][1][0].tag, mei.STAFF_DEF)
        self.assertEqual(mei_section[0][0][1][0].get('lines'), '5')
        self.assertEqual(mei_section[0][0][1][0].get('n'), '2')
        self.assertEqual(mei_section[0][0][1][1].tag, mei.STAFF_DEF)
        self.assertEqual(mei_section[0][0][1][1].get('n'), '3')
        self.assertEqual(mei_section[0][0][1][1].get('lines'), '5')
        self.assertEqual(mei_section[0][0][2].tag, mei.STAFF_DEF)
        self.assertEqual(mei_section[0][0][2].get('n'), '4')
        self.assertEqual(mei_section[0][0][2].get('lines'), '5')
        for x in range(1,5):
            self.assertEqual(mei_section[x].tag, mei.STAFF)
            self.assertEqual(mei_section[x].get('n'), str(x))
        self.assertIsNotNone(mei_section.get(xml.ID))

    @mock.patch("lychee.converters.abjad_to_lmei.staff_to_staff")
    def test_section_full_mock(self,mock_section):
        '''
        precondition: abjad Score containing Staff, StaffGroup containing two Staffs, and Staff
        postcondition: mei section Element containing scoreDef element and four staff Elements
        with staff Elements two and three of four grouped

        '''
        abjad_score = Score()
        abjad_score.append(Staff())
        abjad_score.append( StaffGroup([Staff(), Staff()]) )
        abjad_score.append(Staff())
        mock_section.side_effect = lambda x: etree.Element(mei.STAFF, n='1')

        mei_section = abjad_to_lmei.score_to_section(abjad_score)

        self.assertEqual(mei_section.tag, mei.SECTION)
        self.assertEqual(len(mei_section), 5)
        self.assertEqual(mei_section[0].tag, mei.SCORE_DEF)
        self.assertEqual(len(mei_section[0]), 1)
        self.assertEqual(mei_section[0][0].tag, mei.STAFF_GRP)
        self.assertEqual(len(mei_section[0][0]), 3)
        self.assertEqual(mei_section[0][0][0].tag, mei.STAFF_DEF)
        self.assertEqual(mei_section[0][0][0].get('lines'), '5')
        self.assertEqual(mei_section[0][0][0].get('n'), '1')
        self.assertEqual(mei_section[0][0][1].tag, mei.STAFF_GRP)
        self.assertEqual(mei_section[0][0][1][0].tag, mei.STAFF_DEF)
        self.assertEqual(mei_section[0][0][1][0].get('lines'), '5')
        self.assertEqual(mei_section[0][0][1][0].get('n'), '2')
        self.assertEqual(mei_section[0][0][1][1].tag, mei.STAFF_DEF)
        self.assertEqual(mei_section[0][0][1][1].get('n'), '3')
        self.assertEqual(mei_section[0][0][1][1].get('lines'), '5')
        self.assertEqual(mei_section[0][0][2].tag, mei.STAFF_DEF)
        self.assertEqual(mei_section[0][0][2].get('n'), '4')
        self.assertEqual(mei_section[0][0][2].get('lines'), '5')
        for x in range(1,5):
            self.assertEqual(mei_section[x].tag, mei.STAFF)
            self.assertEqual(mei_section[x].get('n'), str(x))
        self.assertIsNotNone(mei_section.get(xml.ID))

    def test_tuplet_to_tupletspan_empty_fixed(self):
        '''
        precondition: empty abjad FixedDuratonTuplet
        postcondition: list containing mei tupletspan Element with dur attr
        '''
        abjad_tuplet = FixedDurationTuplet(Duration(1,4), [])

        mei_element = abjad_to_lmei.tuplet_to_tupletspan(abjad_tuplet)

        self.assertTrue(isinstance(mei_element, etree._Element))
        tupletspan = mei_element
        self.assertEqual(tupletspan.tag, mei.TUPLET_SPAN)
        self.assertEqual(tupletspan.get('dur'), '4')
        self.assertIsNone(tupletspan.get('dots'))
        self.assertIsNone(tupletspan.get('num'))
        self.assertIsNone(tupletspan.get('numBase'))
        self.assertIsNone(tupletspan.get('startid'))
        self.assertIsNone(tupletspan.get('endid'))
        self.assertIsNotNone(tupletspan.get(xml.ID))

    def test_tuplet_to_tupletspan_empty_fixed_dotted(self):
        '''
        precondition: empty abjad FixedDuratonTuplet
        postcondition: list containing mei tupletspan Element with dur attr
        '''
        abjad_tuplet = FixedDurationTuplet(Duration(3,8), [])

        mei_element = abjad_to_lmei.tuplet_to_tupletspan(abjad_tuplet)

        self.assertTrue(isinstance(mei_element, etree._Element))
        tupletspan = mei_element
        self.assertEqual(tupletspan.tag, mei.TUPLET_SPAN)
        self.assertEqual(tupletspan.get('dur'), '4')
        self.assertEqual(tupletspan.get('dots'), '1')
        self.assertIsNone(tupletspan.get('num'))
        self.assertIsNone(tupletspan.get('numBase'))
        self.assertIsNone(tupletspan.get('startid'))
        self.assertIsNone(tupletspan.get('endid'))
        self.assertIsNotNone(tupletspan.get(xml.ID))

    def test_tuplet_to_tupletspan_empty(self):
        '''
        precondition: empty abjad Tuplet with fixed Multiplier
        postcondition: list containing mei tupletspan Element with num and numBase attrs
        '''
        abjad_tuplet = Tuplet(Multiplier(2,3), [])

        mei_element = abjad_to_lmei.tuplet_to_tupletspan(abjad_tuplet)

        self.assertTrue(isinstance(mei_element, etree._Element))
        tupletspan = mei_element
        self.assertEqual(tupletspan.tag, mei.TUPLET_SPAN)
        self.assertEqual(tupletspan.get('dur'), None)
        self.assertEqual(tupletspan.get('dots'), None)
        self.assertEqual(tupletspan.get('num'), '3')
        self.assertEqual(tupletspan.get('numBase'), '2')
        self.assertEqual(tupletspan.get('startid'), None)
        self.assertEqual(tupletspan.get('endid'), None)
        self.assertIsNotNone(tupletspan.get(xml.ID))

    def test_tuplet_to_tupletspan_full(self):
        '''
        precondition: abjad Tuplet containing leaves
        postcondition: list containing mei tupletspan Element followed by leaf Elements
        '''
        # returns list containing tupletspan followed by leaf elements
        abjad_tuplet = Tuplet(Multiplier(2,3), "c'8 c' c'")

        mei_elements = abjad_to_lmei.tuplet_to_tupletspan(abjad_tuplet)

        self.assertTrue(isinstance(mei_elements, list))
        self.assertEqual(len(mei_elements), 4)
        self.assertEqual(mei_elements[0].tag, mei.TUPLET_SPAN)
        self.assertEqual(mei_elements[0].get('dur'), '4')
        self.assertIsNone(mei_elements[0].get('dots'))
        self.assertEqual(mei_elements[0].get('num'), '3')
        self.assertEqual(mei_elements[0].get('numBase'), '2')
        self.assertEqual(mei_elements[0].get('startid'), mei_elements[1].get(xml.ID))
        self.assertEqual(mei_elements[0].get('endid'), mei_elements[-1].get(xml.ID))
        chunked_plist = mei_elements[0].get('plist').split()
        self.assertEqual(len(chunked_plist), 3)
        for note_element in mei_elements[1:]:
            self.assertTrue(note_element.get(xml.ID) in chunked_plist)

    @mock.patch("lychee.converters.abjad_to_lmei.leaf_to_element")
    def test_tuplet_to_tupletspan_full_mock(self, mock_element):
        '''
        precondition: abjad Tuplet containing leaves
        postcondition: list containing mei tupletspan Element followed by leaf Elements
        '''
        # returns list containing tupletspan followed by leaf elements
        abjad_tuplet = Tuplet(Multiplier(2,3), "c'8 c' c'")
        mock_element.side_effect = lambda x: etree.Element(mei.NOTE, pname='c', octave='4', dur='8')

        mei_elements = abjad_to_lmei.tuplet_to_tupletspan(abjad_tuplet)

        self.assertTrue(isinstance(mei_elements, list))
        self.assertEqual(len(mei_elements), 4)
        self.assertEqual(mei_elements[0].tag, mei.TUPLET_SPAN)
        self.assertEqual(mei_elements[0].get('dur'), '4')
        self.assertIsNone(mei_elements[0].get('dots'))
        self.assertEqual(mei_elements[0].get('num'), '3')
        self.assertEqual(mei_elements[0].get('numBase'), '2')
        self.assertEqual(mei_elements[0].get('startid'), mei_elements[1].get(xml.ID))
        self.assertEqual(mei_elements[0].get('endid'), mei_elements[-1].get(xml.ID))
        chunked_plist = mei_elements[0].get('plist').split()
        self.assertEqual(len(chunked_plist), 3)
        for note_element in mei_elements[1:]:
            self.assertTrue(note_element.get(xml.ID) in chunked_plist)

    def test_tuplet_to_tupletspan_full_dotted(self):
        '''
        precondition: abjad Tuplet of dotted duration containing leaves
        postcondition: list containing mei tupletspan Element with dots attr followed by leaf Elements
        '''
        abjad_tuplet = Tuplet()
        abjad_tuplet = abjad_tuplet.from_duration_and_ratio(Duration(3,8), [1] * 5)

        mei_elements = abjad_to_lmei.tuplet_to_tupletspan(abjad_tuplet)

        self.assertTrue(isinstance(mei_elements, list))
        self.assertEqual(len(mei_elements), 6)
        self.assertEqual(mei_elements[0].tag, mei.TUPLET_SPAN)
        self.assertEqual(mei_elements[0].get('dur'), '4')
        self.assertEqual(mei_elements[0].get('dots'), '1')
        self.assertEqual(mei_elements[0].get('num'), '5')
        self.assertEqual(mei_elements[0].get('numBase'), '3')
        self.assertEqual(mei_elements[0].get('startid'), mei_elements[1].get(xml.ID))
        self.assertEqual(mei_elements[0].get('endid'), mei_elements[-1].get(xml.ID))
        chunked_plist = mei_elements[0].get('plist').split()
        self.assertEqual(len(chunked_plist), 5)
        for note_element in mei_elements[1:]:
            self.assertTrue(note_element.get(xml.ID) in chunked_plist)

    @mock.patch("lychee.converters.abjad_to_lmei.leaf_to_element")
    def test_tuplet_to_tupletspan_full_dotted_mock(self, mock_element):
        '''
        precondition: abjad Tuplet of dotted duration containing leaves
        postcondition: list containing mei tupletspan Element with dots attr followed by leaf Elements
        '''
        abjad_tuplet = Tuplet()
        abjad_tuplet = abjad_tuplet.from_duration_and_ratio(Duration(3,8), [1] * 5)
        mock_element.side_effect = lambda x: etree.Element(mei.NOTE, pname='c', octave='4', dur='8')

        mei_elements = abjad_to_lmei.tuplet_to_tupletspan(abjad_tuplet)

        self.assertTrue(isinstance(mei_elements, list))
        self.assertEqual(len(mei_elements), 6)
        self.assertEqual(mei_elements[0].tag, mei.TUPLET_SPAN)
        self.assertEqual(mei_elements[0].get('dur'), '4')
        self.assertEqual(mei_elements[0].get('dots'), '1')
        self.assertEqual(mei_elements[0].get('num'), '5')
        self.assertEqual(mei_elements[0].get('numBase'), '3')
        self.assertEqual(mei_elements[0].get('startid'), mei_elements[1].get(xml.ID))
        self.assertEqual(mei_elements[0].get('endid'), mei_elements[-1].get(xml.ID))
        chunked_plist = mei_elements[0].get('plist').split()
        self.assertEqual(len(chunked_plist), 5)
        for note_element in mei_elements[1:]:
            self.assertTrue(note_element.get(xml.ID) in chunked_plist)

    def test_tuplet_to_tupletspan_full_nested(self):
        '''
        precondition: Abjad Tuplet containing Leaves and a Tuplet.
        postcondition: list of mei elements containing tupletspan followed by leaf/tupletspan Elements.
        '''
        inner_tuplet = FixedDurationTuplet((1,4), "c'8 c' c'")
        outer_tuplet = FixedDurationTuplet((3,8), [])
        outer_tuplet.append(inner_tuplet)
        outer_tuplet.extend("d'8 d' d'")

        mei_elements = abjad_to_lmei.tuplet_to_tupletspan(outer_tuplet)

        self.assertTrue(isinstance(mei_elements, list))
        self.assertEqual(len(mei_elements), 8)
        outer_tupletspan = mei_elements[0]
        inner_tupletspan = mei_elements[1]
        self.assertEqual(outer_tupletspan.tag, mei.TUPLET_SPAN)
        self.assertEqual(outer_tupletspan.get('dur'), '4')
        self.assertEqual(outer_tupletspan.get('dots'), '1')
        self.assertEqual(outer_tupletspan.get('num'), '5')
        self.assertEqual(outer_tupletspan.get('numBase'), '3')
        self.assertEqual(inner_tupletspan.tag, mei.TUPLET_SPAN)
        self.assertEqual(inner_tupletspan.get('dur'), '4')
        self.assertIsNone(inner_tupletspan.get('dots'))
        self.assertEqual(inner_tupletspan.get('num'), '3')
        self.assertEqual(inner_tupletspan.get('numBase'), '2')
        for note in mei_elements[2:]:
            self.assertEqual(note.tag, mei.NOTE)
        inner_ids = mei_elements[1].get('plist').split()
        for inner_tuplet_note in mei_elements[2:5]:
            self.assertTrue(inner_tuplet_note.get(xml.ID) in inner_ids)
        self.assertEqual(mei_elements[1].get('startid'), mei_elements[2].get(xml.ID))
        self.assertEqual(mei_elements[1].get('endid'), mei_elements[4].get(xml.ID))
        outer_ids = mei_elements[0].get('plist').split()
        for outer_tuplet_element in mei_elements[1:]:
            self.assertTrue(outer_tuplet_element.get(xml.ID) in outer_ids)
        self.assertEqual(mei_elements[0].get('startid'), mei_elements[1].get(xml.ID))
        self.assertEqual(mei_elements[0].get('endid'), mei_elements[-1].get(xml.ID))
        for note_element in mei_elements[1:]:
            self.assertTrue(note_element.get(xml.ID) in outer_ids)

    @mock.patch("lychee.converters.abjad_to_lmei.leaf_to_element")
    def test_tuplet_to_tupletspan_full_nested_mock(self, mock_element):
        '''
        precondition: Abjad Tuplet containing Leaves and a Tuplet.
        postcondition: list of mei elements containing tupletspan followed by leaf/tupletspan Elements.
        '''
        inner_tuplet = FixedDurationTuplet((1,4), "c'8 c' c'")
        outer_tuplet = FixedDurationTuplet((3,8), [])
        outer_tuplet.append(inner_tuplet)
        outer_tuplet.extend("d'8 d' d'")
        mock_element.side_effect = lambda x: etree.Element(mei.NOTE, pname='c', octave='4', dur='8')

        mei_elements = abjad_to_lmei.tuplet_to_tupletspan(outer_tuplet)

        self.assertTrue(isinstance(mei_elements, list))
        self.assertEqual(len(mei_elements), 8)
        outer_tupletspan = mei_elements[0]
        inner_tupletspan = mei_elements[1]
        self.assertEqual(outer_tupletspan.tag, mei.TUPLET_SPAN)
        self.assertEqual(outer_tupletspan.get('dur'), '4')
        self.assertEqual(outer_tupletspan.get('dots'), '1')
        self.assertEqual(outer_tupletspan.get('num'), '5')
        self.assertEqual(outer_tupletspan.get('numBase'), '3')
        self.assertEqual(inner_tupletspan.tag, mei.TUPLET_SPAN)
        self.assertEqual(inner_tupletspan.get('dur'), '4')
        self.assertIsNone(inner_tupletspan.get('dots'))
        self.assertEqual(inner_tupletspan.get('num'), '3')
        self.assertEqual(inner_tupletspan.get('numBase'), '2')
        for note in mei_elements[2:]:
            self.assertEqual(note.tag, mei.NOTE)
        inner_ids = mei_elements[1].get('plist').split()
        for inner_tuplet_note in mei_elements[2:5]:
            self.assertTrue(inner_tuplet_note.get(xml.ID) in inner_ids)
        self.assertEqual(mei_elements[1].get('startid'), mei_elements[2].get(xml.ID))
        self.assertEqual(mei_elements[1].get('endid'), mei_elements[4].get(xml.ID))
        outer_ids = mei_elements[0].get('plist').split()
        for outer_tuplet_element in mei_elements[1:]:
            self.assertTrue(outer_tuplet_element.get(xml.ID) in outer_ids)
        self.assertEqual(mei_elements[0].get('startid'), mei_elements[1].get(xml.ID))
        self.assertEqual(mei_elements[0].get('endid'), mei_elements[-1].get(xml.ID))
        for note_element in mei_elements[1:]:
            self.assertTrue(note_element.get(xml.ID) in outer_ids)
