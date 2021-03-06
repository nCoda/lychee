#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/test/test_abjad.py
# Purpose:                Tests conversion from lmei to abjad.
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
from lxml import etree as ETree
from abjad.tools.scoretools.Note import Note
from abjad.tools.scoretools.Rest import Rest
from abjad.tools.scoretools.Chord import Chord
from abjad.tools.scoretools.Skip import Skip
from abjad.tools.scoretools.NoteHead import NoteHead
from abjad.tools.scoretools.Tuplet import Tuplet
from abjad.tools.scoretools.Voice import Voice
from abjad.tools.scoretools.Staff import Staff
from abjad.tools.scoretools.StaffGroup import StaffGroup
from abjad.tools.scoretools.Score import Score
from abjad.tools.durationtools.Duration import Duration
from abjad.tools.durationtools.Multiplier import Multiplier
from abjad.tools.topleveltools.inspect import inspect
from abjad.tools.topleveltools.attach import attach
from lychee.converters.outbound import abjad
from lychee.converters.tests import abjad_test_case
from lychee import exceptions
from lychee.namespaces import mei, xml
import pytest
import unittest
import six

try:
    from unittest import mock
except ImportError:
    import mock


class TestConvertFunction(object):
    '''
    Tests for abjad.convert().
    '''

    def test_supported_element(self):
        '''
        Convert an MEI <note>.

        Expect an Abjad Note.
        '''
        note = ETree.Element(mei.NOTE, {'dur': '4', 'pname': 'c', 'octave': '4'})
        actual = abjad.convert(note)
        assert isinstance(actual, Note)

    def test_unsupported_element(self):
        '''
        Convert an MEI <boat>.

        Expect an OutboundConversionError.
        '''
        boat = ETree.Element('boat', {'size': 'panamax', 'owner': "Cap'n Crunch"})
        with pytest.raises(exceptions.OutboundConversionError) as exc:
            abjad.convert(boat)
        assert exc.value.args[0] == abjad._UNSUPPORTED_ELEMENT.format(tagname='boat')


class TestLmeiToAbjadConversions(abjad_test_case.AbjadTestCase):

    # note conversion

    def test_note_basic(self):
        '''
        precondition: mei note Element with duration, pitch name, and octave string
        postcondition: abjad Note with duration, pitch name, and octave string
        '''
        dictionary = {'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element(mei.NOTE, dictionary)
        abjad_note = abjad.note_to_note(mei_note)
        self.assertEqual(format(abjad_note), format(Note("c'4")))

    def test_note_dotted(self):
        '''
        precondition: mei note Element with dots attribute
        postcondition: abjad Note with dot
        '''
        dictionary = {'dots': '1', 'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element(mei.NOTE, dictionary)
        abjad_note = abjad.note_to_note(mei_note)
        self.assertEqual(format(abjad_note), format(Note("c'4.")))

    def test_note_accid(self):
        '''
        precondition: mei note Element with gestural accidental
        postcondition: abjad Note with accidental, neither forced nor cautionary
        '''
        dictionary = {'accid.ges': 'f', 'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element(mei.NOTE, dictionary)
        abjad_note = abjad.note_to_note(mei_note)
        self.assertEqual(abjad_note, Note("cf'4"))

    def test_note_accid_and_cautionary(self):
        '''
        preconditions: mei note Element containing cautionary accidental subelement
        postconditions: abjad Note with cautionary accidental
        '''
        dictionary = {'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element(mei.NOTE, dictionary)
        ETree.SubElement(mei_note, mei.ACCID, {'accid': 'f', 'func': 'cautionary'})
        abjad_note = abjad.note_to_note(mei_note)
        self.assertEqual(abjad_note, Note("cf'?4"))

    def test_note_accid_and_forced(self):
        '''
        preconditions: mei note Element with both written and gestural accidentals
        postconditions: abjad Note with forced accidental
        '''
        dictionary = {'accid.ges': 'f', 'accid': 'f', 'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element(mei.NOTE, dictionary)
        abjad_note = abjad.note_to_note(mei_note)
        self.assertEqual(abjad_note, Note("cf'!4"))

    def test_note_cautionary(self):
        '''
        precondition: mei note Element containing cautionary accidental subelement set to natural
        postcondition: abjad Note with no accidental and cautionary natural
        '''
        dictionary = {'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element(mei.NOTE, dictionary)
        ETree.SubElement(mei_note, mei.ACCID, {'accid': 'n', 'func': 'cautionary'})
        abjad_note = abjad.note_to_note(mei_note)
        self.assertEqual(abjad_note, Note("c'?4"))

    def test_note_forced(self):
        '''
        precondition: mei note Element with both accid.ges and accid attributes set
        postcondition: abjad Note with no accidental and forced natural
        '''
        dictionary = {'accid.ges': 'n', 'accid': 'n', 'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element(mei.NOTE,dictionary)
        abjad_note = abjad.note_to_note(mei_note)
        self.assertEqual(abjad_note, Note("c'!4"))

    #forced, cautionary, accidental, blank notehead tests

    def test_notehead_basic(self):
        '''
        precondition: mei note Element with pitch name, and octave string
        postcondition: abjad NoteHead with duration, pitch name, and octave string
        '''
        dictionary = {'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element(mei.NOTE, dictionary)
        abjad_notehead = abjad.note_to_note(mei_note)
        self.assertEqual(abjad_notehead, NoteHead("c'"))

    #notehead: basic, basic cautionary, basic forced, accidental, acc cautionary, acc forced.

    def test_notehead_basic_cautionary(self):
        '''
        precondition: mei note Element with cautionary accidental
        postcondition: Abjad NoteHead with cautionary accidental
        '''
        dictionary = {'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element(mei.NOTE, dictionary)
        ETree.SubElement(mei_note, mei.ACCID, {'accid': 'n', 'func': 'cautionary'})
        abjad_notehead = abjad.note_to_note(mei_note)
        head = NoteHead("c'")
        head.is_cautionary = True
        self.assertEqual(abjad_notehead, head)

    def test_notehead_basic_forced(self):
        '''
        precondition: mei note Element with no accidental and both accid.ges and accid attributes
        postcondition: Abjad NoteHead with forced natural
        '''
        dictionary = {'pname': 'c', 'octave': '4', 'accid.ges': 'n', 'accid': 'n'}
        mei_note = ETree.Element(mei.NOTE, dictionary)
        abjad_notehead = abjad.note_to_note(mei_note)
        head = NoteHead("c'")
        head.is_forced = True
        self.assertEqual(abjad_notehead, head)

    def test_notehead_accid(self):
        '''
        precondition: mei note Element with accidental and no duration.
        postcondition: Abjad NoteHead with accidental.
        '''
        dictionary = {'pname': 'c', 'octave': '4', 'accid.ges': 'f'}
        mei_note = ETree.Element(mei.NOTE, dictionary)
        abjad_notehead = abjad.note_to_note(mei_note)
        self.assertEqual(abjad_notehead, NoteHead("cf'"))

    def test_notehead_accid_cautionary(self):
        '''
        precondition: mei note Element with cautionary accidental
        postcondition: abjad NoteHead with cautionary accidental
        '''
        dictionary = {'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element(mei.NOTE, dictionary)
        ETree.SubElement(mei_note, mei.ACCID, {'accid': 'f', 'func': 'cautionary'})
        abjad_notehead = abjad.note_to_note(mei_note)
        head = NoteHead("cf'")
        head.is_cautionary = True
        self.assertEqual(abjad_notehead, head)

    def test_notehead_accid_forced(self):
        '''
        precondition: mei note Element with forced accidental
        postcondition: abjad NoteHead with forced accidental
        '''
        dictionary = {'pname': 'c', 'octave': '4', 'accid.ges': 'f', 'accid': 'f'}
        mei_note = ETree.Element(mei.NOTE, dictionary)
        abjad_notehead = abjad.note_to_note(mei_note)
        head = NoteHead("cf'")
        head.is_forced = True
        self.assertEqual(abjad_notehead, head)

    def test_rest(self):
        '''
        precondition: mei rest Element with no dots.
        postcondition: abjad Rest with no dots.
        '''
        mei_rest = ETree.Element(mei.REST,dur='32')
        abjad_rest = abjad.rest_to_rest(mei_rest)
        self.assertEqual(abjad_rest, Rest("r32"))

    def test_rest_dotted(self):
        '''
        precondition: dotted mei rest Element.
        postcondition: dotted abjad Rest.
        '''
        mei_rest = ETree.Element(mei.REST,dur='32',dots='2')
        abjad_rest = abjad.rest_to_rest(mei_rest)
        self.assertEqual(abjad_rest, Rest("r32.."))

    def test_space_to_skip(self):
        '''
        precondition: mei space Element with no dots.
        postcondition: abjad Skip with no dots.
        '''
        mei_space = ETree.Element(mei.SPACE,dur='32')
        abjad_skip = abjad.space_to_skip(mei_space)
        self.assertEqual(abjad_skip, Skip("s32"))

    def test_space_to_skip_dotted(self):
        '''
        precondition: dotted mei space Element
        postcondition: dotted abjad Skip.
        '''
        mei_space = ETree.Element(mei.SPACE,dur='32',dots='2')
        abjad_skip = abjad.space_to_skip(mei_space)
        self.assertEqual(abjad_skip, Skip("s32.."))

    def test_chord_empty(self):
        '''
        precondition: empty mei chord Element with undotted duration
        postcondition: empty abjad Chord with undotted duration
        '''
        mei_chord = ETree.Element(mei.CHORD,dur='4')
        abjad_chord = abjad.chord_to_chord(mei_chord)
        self.assertEqual(abjad_chord, Chord([],(1,4)))

    def test_chord_empty_dotted(self):
        '''
        precondition: empty mei chord Element with dotted duration
        postcondition: empty abjad Chord with dotted duration
        '''
        mei_chord = ETree.Element(mei.CHORD,dur='4',dots='1')
        abjad_chord = abjad.chord_to_chord(mei_chord)
        self.assertEqual(abjad_chord, Chord([],(3,8)))

    def test_chord_full(self):
        '''
        precondition: mei chord Element with undotted duration and two child note Elements
        postcondition: abjad Chord with undotted duration and two child note Elements
        '''
        mei_chord = ETree.Element(mei.CHORD,dur='4')
        ETree.SubElement(mei_chord, mei.NOTE,pname='c',octave='4')
        ETree.SubElement(mei_chord, mei.NOTE,pname='d',octave='4')
        abjad_chord = abjad.chord_to_chord(mei_chord)
        self.assertEqual(abjad_chord, Chord("<c' d'>4"))

    def test_chord_full_dotted(self):
        '''
        precondition: mei chord Element with dotted duration and two child note Elements
        postcondition: abjad Chord with dotted duration and two child note Elements
        '''
        mei_chord = ETree.Element(mei.CHORD,dur='4',dots='1')
        ETree.SubElement(mei_chord, mei.NOTE,pname='c',octave='4')
        ETree.SubElement(mei_chord, mei.NOTE,pname='d',octave='4')
        abjad_chord = abjad.chord_to_chord(mei_chord)
        self.assertEqual(abjad_chord, Chord("<c' d'>4."))

    def test_layer_to_voice_empty(self):
        '''
        precondition: empty mei layer Element
        postcondition: empty abjad Voice
        '''
        mei_layer = ETree.Element(mei.LAYER,n='1')
        abjad_voice = abjad.layer_to_voice(mei_layer)
        self.assertEqual(abjad_voice, Voice() )

    def test_layer_to_voice_full(self):
        '''
        precondition: mei layer Element containing children
        postcondition: abjad Voice containing children
        '''
        mei_layer = ETree.Element(mei.LAYER, n='1')
        ETree.SubElement(mei_layer, mei.REST, dur='4')
        ETree.SubElement(mei_layer, mei.NOTE, pname='c', octave='4', dur='4')
        chord = ETree.SubElement(mei_layer, mei.CHORD, dur='4')
        ETree.SubElement(chord, mei.NOTE, pname='c', octave='4')
        ETree.SubElement(chord, mei.NOTE, pname='d', octave='4')

        abjad_voice = abjad.layer_to_voice(mei_layer)

        self.assertEqual(abjad_voice, Voice("r4 c'4 <c' d'>4"))



    @mock.patch("lychee.converters.outbound.abjad.chord_to_chord")
    @mock.patch("lychee.converters.outbound.abjad.note_to_note")
    @mock.patch("lychee.converters.outbound.abjad.rest_to_rest")
    def test_layer_to_voice_full_mock(self, mock_rest, mock_note, mock_chord):
        '''
        precondition: mei layer Element containing children
        postcondition: abjad Voice containing children
        '''
        mei_layer = ETree.Element(mei.LAYER,n='1')
        ETree.SubElement(mei_layer, mei.REST, dur='4')
        ETree.SubElement(mei_layer, mei.NOTE, pname='c', octave='4', dur='4')
        chord = ETree.SubElement(mei_layer, mei.CHORD, dur='4')
        ETree.SubElement(chord, mei.NOTE, pname='c', octave='4')
        ETree.SubElement(chord, mei.NOTE, pname='d', octave='4')
        mock_rest.return_value = Rest((1,4))
        mock_note.return_value = Note("c'4")
        mock_chord.return_value = Chord("<c' d'>4")

        abjad_voice = abjad.layer_to_voice(mei_layer)

        self.assertEqual(abjad_voice, Voice("r4 c'4 <c' d'>4"))

    def test_staff_empty(self):
        '''
        precondition: empty mei staff Element
        postcondition: empty abjad Staff
        '''
        mei_staff = ETree.Element(mei.STAFF,n='1')
        abjad_staff = abjad.staff_to_staff(mei_staff)
        self.assertEqual(abjad_staff, Staff())


    def test_staff_one_voice(self):
        '''
        precondition: mei staff Element containing one layer Element
        postcondition: abjad Staff containing one Voice
        '''
        mei_staff = ETree.Element(mei.STAFF,n='1')
        mei_layer = ETree.SubElement(mei_staff, mei.LAYER, n='1')
        ETree.SubElement(mei_layer, mei.REST, dur='4')
        ETree.SubElement(mei_layer, mei.NOTE, pname='c', dur='4', octave='4')

        abjad_staff = abjad.staff_to_staff(mei_staff)

        self.assertEqual(abjad_staff, Staff([Voice("r4 c'4")]))

    @mock.patch("lychee.converters.outbound.abjad.layer_to_voice")
    def test_staff_one_voice_mock(self, mock_voice):
        '''
        precondition: mei staff Element containing one layer Element
        postcondition: abjad Staff containing one Voice
        '''
        mei_staff = ETree.Element(mei.STAFF,n='1')
        mei_layer = ETree.SubElement(mei_staff, mei.LAYER, n='1')
        ETree.SubElement(mei_layer, mei.REST, dur='4')
        ETree.SubElement(mei_layer, mei.NOTE, pname='c', dur='4', octave='4')
        mock_voice.return_value = Voice("r4 c'4")

        abjad_staff = abjad.staff_to_staff(mei_staff)

        voice = Voice("r4 c'4")
        comparator = Staff([voice])
        self.assertEqual(abjad_staff, comparator)

    def test_staff_parallel(self):
        '''
        precondition: mei staff Element containing two layer Elements
        postcondition: abjad Staff containing two Voices
        '''
        mei_staff = ETree.Element(mei.STAFF, n='1')
        ETree.SubElement(mei_staff, mei.LAYER, n='1')
        ETree.SubElement(mei_staff, mei.LAYER, n='2')

        abjad_staff = abjad.staff_to_staff(mei_staff)

        self.assertEqual(abjad_staff, Staff([Voice(), Voice()]))

    @mock.patch("lychee.converters.outbound.abjad.layer_to_voice")
    def test_staff_parallel_mock(self, mock_voice):
        '''
        precondition: mei staff Element containing two layer Elements
        postcondition: abjad Staff containing two Voices
        '''
        mei_staff = ETree.Element(mei.STAFF, n='1')
        ETree.SubElement(mei_staff, mei.LAYER, n='1')
        ETree.SubElement(mei_staff, mei.LAYER, n='2')
        mock_voice.side_effect = lambda x: Voice()

        abjad_staff = abjad.staff_to_staff(mei_staff)

        self.assertEqual(abjad_staff, Staff([Voice(), Voice()]))

    def test_section_empty(self):
        '''
        precondition: empty mei section Element
        postcondition: empty abjad Score
        '''
        mei_section = ETree.Element(mei.SECTION,n='1')
        abjad_score = abjad.section_to_score(mei_section)
        self.assertEqual(abjad_score, Score())

    def test_section_full(self):
        '''
        precondition: mei section Element containing scoreDef element and four staff Elements
        with staff Elements two and three of four grouped
        postcondition: abjad Score containing Staff, StaffGroup containing two Staffs, and Staff
        '''
        mei_section = ETree.Element(mei.SECTION, n='1')
        mei_score_def = ETree.Element(mei.SCORE_DEF, n='1')
        main_staff_grp = ETree.Element(mei.STAFF_GRP, n='1')
        contained_mei_staff_grp = ETree.Element(mei.STAFF_GRP, n='1')
        mei_staffs = []
        mei_staff_defs = []
        for x in range(4):
            mei_staff_defs.append(ETree.Element(mei.STAFF_DEF, n=str(x + 1)))
            mei_staffs.append(ETree.Element(mei.STAFF, n=str(x + 1)))
        mei_section.append(mei_score_def)
        mei_score_def.append(main_staff_grp)
        main_staff_grp.append(mei_staff_defs[0])
        main_staff_grp.append(contained_mei_staff_grp)
        contained_mei_staff_grp.extend(mei_staff_defs[1:3])
        main_staff_grp.append(mei_staff_defs[3])
        mei_section.extend(mei_staffs)

        abjad_score = abjad.section_to_score(mei_section)

        comparator = Score()
        comparator.append(Staff())
        comparator.append(StaffGroup([Staff(), Staff()]))
        comparator.append(Staff())

        self.assertEqual(abjad_score, comparator)
        self.assertEqual(len(abjad_score), 3)
        self.assertEqual(isinstance(abjad_score[0], Staff), True)
        self.assertEqual(isinstance(abjad_score[1], StaffGroup), True)
        self.assertEqual(isinstance(abjad_score[2], Staff), True)
        self.assertEqual(len(abjad_score[1]), 2)

    @mock.patch("lychee.converters.outbound.abjad.staff_to_staff")
    def test_section_full_mock(self, mock_staff):
        '''
        precondition: mei section Element containing scoreDef element and four staff Elements
        with staff Elements two and three of four grouped
        postcondition: abjad Score containing Staff, StaffGroup containing two Staffs, and Staff
        '''
        mei_section = ETree.Element(mei.SECTION, n='1')
        mei_score_def = ETree.Element(mei.SCORE_DEF, n='1')
        main_staff_grp = ETree.Element(mei.STAFF_GRP, n='1')
        contained_mei_staff_grp = ETree.Element(mei.STAFF_GRP, n='1')
        mei_staffs = []
        mei_staff_defs = []
        for x in range(4):
            mei_staff_defs.append( ETree.Element(mei.STAFF_DEF, n=str(x + 1)))
        for x in range(4):
            mei_staffs.append( ETree.Element(mei.STAFF, n=str(x + 1)))
        mei_section.append(mei_score_def)
        mei_score_def.append(main_staff_grp)
        main_staff_grp.append(mei_staff_defs[0])
        main_staff_grp.append(contained_mei_staff_grp)
        contained_mei_staff_grp.extend(mei_staff_defs[1:3])
        main_staff_grp.append(mei_staff_defs[3])
        mei_section.extend(mei_staffs)
        mock_staff.side_effect = lambda x: Staff()

        abjad_score = abjad.section_to_score(mei_section)

        comparator = Score()
        comparator.append(Staff())
        comparator.append(StaffGroup([Staff(), Staff()]))
        comparator.append(Staff())

        self.assertEqual(abjad_score, comparator)
        self.assertEqual(len(abjad_score), 3)
        self.assertEqual(isinstance(abjad_score[0], Staff), True)
        self.assertEqual(isinstance(abjad_score[1], StaffGroup), True)
        self.assertEqual(isinstance(abjad_score[2], Staff), True)
        self.assertEqual(len(abjad_score[1]), 2)


    def test_tupletspan_to_tuplet_empty(self):
        '''
        precondition: mei tupletspan Element with multipier, no duration
        postcondition: abjad Tuplet object with Multiplier, no duration
        '''
        mei_tupletspan = ETree.Element(mei.TUPLET_SPAN,num='3',numBase='2')
        abjad_tuplet = abjad.tupletspan_to_tuplet(mei_tupletspan)
        self.assertEqual(len(abjad_tuplet), 0)
        self.assertEqual(abjad_tuplet.multiplier, Multiplier(2,3))

    def test_tupletspan_to_tuplet_full(self):
        '''
        precondition: mei tupletspan Element with multipier, duration, and children
        postcondition: abjad Tuplet object with Multiplier, duration, and children
        '''
        mei_tupletspan = ETree.Element(mei.TUPLET_SPAN,num='3', numBase='2', dur='4')
        tupletspan_list = [mei_tupletspan]
        for x in range(3):
            note = ETree.Element(mei.NOTE, pname='c', octave='4', dur='8')
            note.set(xml.ID, six.b(str(x + 1)))
            tupletspan_list.append(note)
        mei_tupletspan.set('startid', '1')
        mei_tupletspan.set('endid', '5')
        mei_tupletspan.set('plist', '1 2 3 4 5')

        abjad_tuplet = abjad.tupletspan_to_tuplet(tupletspan_list)

        self.assertEqual(len(abjad_tuplet), 3)
        self.assertEqual(abjad_tuplet.multiplier, Multiplier(2,3))
        self.assertEqual(abjad_tuplet.multiplied_duration, Duration(1,4))
        for note in abjad_tuplet:
            self.assertTrue(isinstance(note, Note))
            self.assertEqual(note.written_duration, Duration(1,8))
            self.assertEqual(inspect(note).get_duration(), Duration(1,12))


    @mock.patch("lychee.converters.outbound.abjad.element_to_leaf")
    def test_tupletspan_to_tuplet_full_mock(self, mock_leaf):
        '''
        precondition: mei tupletspan Element with multipier, duration, and children
        postcondition: abjad Tuplet object with Multiplier, duration, and children
        '''
        mei_tupletspan = ETree.Element(mei.TUPLET_SPAN,num='3', numBase='2', dur='4')
        tupletspan_list = [mei_tupletspan]
        for x in range(3):
            note = ETree.Element(mei.NOTE, pname='c', octave='4', dur='8')
            note.set(xml.ID, six.b(str(x + 1)))
            tupletspan_list.append(note)
        mei_tupletspan.set('startid', '1')
        mei_tupletspan.set('endid', '5')
        mei_tupletspan.set('plist', '1 2 3 4 5')
        mock_leaf.side_effect = lambda x: Note("c'8")

        abjad_tuplet = abjad.tupletspan_to_tuplet(tupletspan_list)

        self.assertEqual(len(abjad_tuplet), 3)
        self.assertEqual(abjad_tuplet.multiplier, Multiplier(2,3))
        self.assertEqual(abjad_tuplet.multiplied_duration, Duration(1,4))
        for note in abjad_tuplet:
            self.assertTrue(isinstance(note, Note))
            self.assertEqual(note.written_duration, Duration(1,8))
            self.assertEqual(inspect(note).get_duration(), Duration(1,12))

    def test_tupletspan_to_tuplet_full_dotted(self):
        '''
        precondition: mei tupletspan Element with multipier, dotted duration, and children
        postcondition: abjad Tuplet object with Multiplier, dotted duration, and children
        '''
        mei_tupletspan = [ETree.Element(mei.TUPLET_SPAN,num='5', numBase='3', dur='4', dots='1')]
        for x in range(5):
            note = ETree.Element(mei.NOTE, pname='c', octave='4', dur='8')
            note.set(xml.ID, six.b(str(x + 1)))
            mei_tupletspan.append(note)
        mei_tupletspan[0].set('startid', '1')
        mei_tupletspan[0].set('endid', '5')
        mei_tupletspan[0].set('plist', '1 2 3 4 5')

        abjad_tuplet = abjad.tupletspan_to_tuplet(mei_tupletspan)

        self.assertEqual(len(abjad_tuplet), 5)
        self.assertEqual(abjad_tuplet.multiplier, Multiplier(3,5))
        self.assertEqual(abjad_tuplet.multiplied_duration, Duration(3,8))
        for note in abjad_tuplet:
            self.assertTrue(isinstance(note, Note))
            self.assertEqual(note.written_duration, Duration(1,8))
            self.assertEqual(inspect(note).get_duration(), Duration(3,40))

    @mock.patch("lychee.converters.outbound.abjad.element_to_leaf")
    def test_tupletspan_to_tuplet_full_dotted_mock(self, mock_leaf):
        '''
        precondition: mei tupletspan Element with multipier, dotted duration, and children
        postcondition: abjad Tuplet object with Multiplier, dotted duration, and children
        '''
        mei_tupletspan = [ETree.Element(mei.TUPLET_SPAN,num='5', numBase='3', dur='4', dots='1')]
        for x in range(5):
            note = ETree.Element(mei.NOTE, pname='c', octave='4', dur='8')
            note.set(xml.ID, six.b(str(x + 1)))
            mei_tupletspan.append(note)
        mei_tupletspan[0].set('startid', '1')
        mei_tupletspan[0].set('endid', '5')
        mei_tupletspan[0].set('plist', '1 2 3 4 5')
        mock_leaf.side_effect = lambda x: Note("c'8")

        abjad_tuplet = abjad.tupletspan_to_tuplet(mei_tupletspan)

        self.assertEqual(len(abjad_tuplet), 5)
        self.assertEqual(abjad_tuplet.multiplier, Multiplier(3,5))
        self.assertEqual(abjad_tuplet.multiplied_duration, Duration(3,8))
        for note in abjad_tuplet:
            self.assertTrue(isinstance(note, Note))
            self.assertEqual(note.written_duration, Duration(1,8))
            self.assertEqual(inspect(note).get_duration(), Duration(3,40))

    def test_tupletspan_to_tuplet_full_nested(self):
        '''
        precondition: list containing mei tupletspan Element, notes, and (nested) tupletspan Element
        postcondition: abjad Tuplet containing notes and (nested) abjad Tuplet
        '''
        mei_nested_tuplet = []
        outer_tuplet = ETree.Element(mei.TUPLET_SPAN, dur='4', dots='1', num='5', numBase='3')
        inner_tuplet = ETree.Element(mei.TUPLET_SPAN, dur='4', num='3', numBase='2')
        inner_tuplet.set(xml.ID, six.b('1'))
        mei_nested_tuplet.extend([outer_tuplet, inner_tuplet])
        for x in range(6):
            note = ETree.Element(mei.NOTE, dur='8', pname='c', octave='4')
            note.set(xml.ID, six.b(str(x + 2)))
            mei_nested_tuplet.append(note)
        outer_tuplet.set('startid', mei_nested_tuplet[1].get(xml.ID))
        outer_tuplet.set('endid', mei_nested_tuplet[-1].get(xml.ID))
        outer_tuplet.set('plist', '1 2 3 4 5 6 7')
        inner_tuplet.set('startid', mei_nested_tuplet[2].get(xml.ID))
        inner_tuplet.set('endid', mei_nested_tuplet[4].get(xml.ID))
        inner_tuplet.set('plist', '2 3 4')

        abjad_tuplet = abjad.tupletspan_to_tuplet(mei_nested_tuplet)

        inner_tuplet = abjad_tuplet[0]
        self.assertTrue(isinstance(abjad_tuplet, Tuplet))
        self.assertTrue(isinstance(abjad_tuplet[0], Tuplet))
        self.assertEqual(len(abjad_tuplet), 4)
        self.assertEqual(abjad_tuplet.multiplier, Multiplier(3,5))
        self.assertEqual(inner_tuplet.multiplier, Multiplier(2,3))
        self.assertEqual(inspect(abjad_tuplet).get_duration(), Duration(3,8))
        self.assertEqual(inspect(inner_tuplet).get_duration(), Duration(3,20))
        for note in inner_tuplet:
            self.assertTrue(isinstance(note, Note))
            self.assertEqual(note.written_duration, Duration(1,8))
            self.assertEqual(inspect(note).get_duration(), Duration(1,20))
        for note in abjad_tuplet[1:]:
            self.assertTrue(isinstance(note, Note))
            self.assertEqual(note.written_duration, Duration(1,8))
            self.assertEqual(inspect(note).get_duration(), Duration(3,40))

    @mock.patch("lychee.converters.outbound.abjad.element_to_leaf")
    def test_tupletspan_to_tuplet_full_nested_mock(self, mock_leaf):
        '''
        precondition: list containing mei tupletspan Element, notes, and (nested) tupletspan Element
        postcondition: abjad Tuplet containing notes and (nested) abjad Tuplet
        '''
        mei_nested_tuplet = []
        outer_tuplet = ETree.Element(mei.TUPLET_SPAN, dur='4', dots='1', num='5', numBase='3')
        inner_tuplet = ETree.Element(mei.TUPLET_SPAN, dur='4', num='3', numBase='2')
        inner_tuplet.set(xml.ID, six.b('1'))
        mei_nested_tuplet.extend([outer_tuplet, inner_tuplet])
        for x in range(6):
            note = ETree.Element(mei.NOTE, dur='8', pname='c', octave='4')
            note.set(xml.ID, six.b(str(x + 2)))
            mei_nested_tuplet.append(note)
        outer_tuplet.set('startid', mei_nested_tuplet[1].get(xml.ID))
        outer_tuplet.set('endid', mei_nested_tuplet[-1].get(xml.ID))
        outer_tuplet.set('plist', '1 2 3 4 5 6 7')
        inner_tuplet.set('startid', mei_nested_tuplet[2].get(xml.ID))
        inner_tuplet.set('endid', mei_nested_tuplet[4].get(xml.ID))
        inner_tuplet.set('plist', '2 3 4')
        mock_leaf.side_effect = lambda x: Note("c'8")

        abjad_tuplet = abjad.tupletspan_to_tuplet(mei_nested_tuplet)

        inner_tuplet = abjad_tuplet[0]
        self.assertTrue(isinstance(abjad_tuplet, Tuplet))
        self.assertTrue(isinstance(abjad_tuplet[0], Tuplet))
        self.assertEqual(len(abjad_tuplet), 4)
        self.assertEqual(abjad_tuplet.multiplier, Multiplier(3,5))
        self.assertEqual(inner_tuplet.multiplier, Multiplier(2,3))
        self.assertEqual(inspect(abjad_tuplet).get_duration(), Duration(3,8))
        self.assertEqual(inspect(inner_tuplet).get_duration(), Duration(3,20))
        for note in inner_tuplet:
            self.assertTrue(isinstance(note, Note))
            self.assertEqual(note.written_duration, Duration(1,8))
            self.assertEqual(inspect(note).get_duration(), Duration(1,20))
        for note in abjad_tuplet[1:]:
            self.assertTrue(isinstance(note, Note))
            self.assertEqual(note.written_duration, Duration(1,8))
            self.assertEqual(inspect(note).get_duration(), Duration(3,40))

    @mock.patch('lychee.converters.outbound.abjad.rest_to_rest')
    @mock.patch('lychee.converters.outbound.abjad.note_to_note')
    @mock.patch('lychee.converters.outbound.abjad.chord_to_chord')
    @mock.patch('lychee.converters.outbound.abjad.space_to_skip')
    def test_element_to_leaf(self, mock_space, mock_chord, mock_note, mock_rest):
        '''
        Ensure element_to_leaf() calls its helper functions as expected.
        '''
        rest = ETree.Element(mei.REST)
        note = ETree.Element(mei.NOTE)
        chord = ETree.Element(mei.CHORD)
        space = ETree.Element(mei.SPACE)

        assert abjad.element_to_leaf(rest) is not None
        assert abjad.element_to_leaf(note) is not None
        assert abjad.element_to_leaf(chord) is not None
        assert abjad.element_to_leaf(space) is not None

        mock_rest.assert_called_once_with(rest)
        mock_note.assert_called_once_with(note)
        mock_chord.assert_called_once_with(chord)
        mock_space.assert_called_once_with(space)
