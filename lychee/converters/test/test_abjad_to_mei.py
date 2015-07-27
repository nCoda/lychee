from lxml import etree as etree
from abjad.tools.scoretools.Note import Note
from abjad.tools.scoretools.Rest import Rest
from abjad.tools.scoretools.Chord import Chord
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
from lychee.converters import abjad_to_mei
import unittest
import abjad_test_case

try:
    from unittest import mock
except ImportError:
    import mock

_MEINS = '{http://www.music-encoding.org/ns/mei}'
_XMLNS = '{http://www.w3.org/XML/1998/namespace}id'
etree.register_namespace('mei', _MEINS[1:-1])

class TestAbjadToMeiConversions(abjad_test_case.AbjadTestCase):
    
    # note conversion
    
    def test_note_basic(self):
        '''
        precondition: abjad note with duration, pitch name, and octave string
        postcondition: mei element
        '''
        abjad_note = Note("c'4")
        mei_note = abjad_to_mei.note_to_note(abjad_note)
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(mei_note.attrib, {'dur': '4', 'pname': 'c', 'octave': '4'})
        self.assertIsNotNone(mei_note.get(_XMLNS))
    
    def test_note_dotted(self):
        '''
        precondition: abjad note with dot
        postcondition: mei element with dots attribute
        '''
        abjad_note = Note("c'4.")
        mei_note = abjad_to_mei.note_to_note(abjad_note)
        self.assertIsNotNone(mei_note.get(_XMLNS))
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(mei_note.attrib, {'dots': '1', 'dur': '4', 'pname': 'c', 'octave': '4'})
    
    def test_note_accid(self):
        '''
        precondition: abjad note with accidental, neither forced nor cautionary
        postcondition: mei element with gestural accidental
        '''
        abjad_note = Note("cf'4")
        mei_note = abjad_to_mei.note_to_note(abjad_note)
        self.assertIsNotNone(mei_note.get(_XMLNS))
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(mei_note.attrib, {'accid.ges': 'f', 'dur': '4', 'pname': 'c', 'octave': '4'})
        
    def test_note_accid_and_cautionary(self):
        '''
        preconditions: abjad note with cautionary accidental
        postconditions: mei element containing cautionary accidental subelement
        '''
        abjad_note = Note("cf'?4")
        mei_note = abjad_to_mei.note_to_note(abjad_note)
        self.assertAttribsEqual(mei_note.attrib, {'dur': '4', 'pname': 'c', 'octave': '4'})
        accid = mei_note.findall('./{}accid'.format(_MEINS))
        accid = accid[0]
        self.assertIsNotNone(mei_note.get(_XMLNS))
        self.assertEqual(accid.tag, '{}accid'.format(_MEINS))
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(accid.attrib, {'accid': 'f', 'func': 'cautionary'})
    
    def test_note_accid_and_forced(self):
        '''
        preconditions: abjad note with forced accidental
        postconditions: mei element with both written and gestural accidentals
        '''
        abjad_note = Note("cf'!4")
        mei_note = abjad_to_mei.note_to_note(abjad_note)
        self.assertIsNotNone(mei_note.get(_XMLNS))
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(mei_note.attrib, {'accid.ges': 'f', 'accid': 'f', 'dur': '4', 'pname': 'c', 'octave': '4'})
    
    def test_note_cautionary(self):
        '''
        precondition: abjad note with no accidental and cautionary natural
        postcondition: mei element containing cautionary accidental subelement set to natural
        '''
        abjad_note = Note("c'?4")
        mei_note = abjad_to_mei.note_to_note(abjad_note)
        self.assertAttribsEqual(mei_note.attrib, {'dur': '4', 'pname': 'c', 'octave': '4'})
        accid = mei_note.findall('./{}accid'.format(_MEINS))
        accid = accid[0]
        self.assertEqual(accid.tag, '{}accid'.format(_MEINS))
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(accid.attrib, {'accid': 'n', 'func': 'cautionary'})
        self.assertIsNotNone(mei_note.get(_XMLNS))
    
    def test_note_forced(self):
        '''
        precondition: abjad note with no accidental and forced accidental
        postcondition: mei element with both accid.ges and accid attributes set
        '''
        abjad_note = Note("c'!4")
        mei_note = abjad_to_mei.note_to_note(abjad_note)
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(mei_note.attrib, {'accid.ges': 'n', 'accid': 'n', 'dur': '4', 'pname': 'c', 'octave': '4'} )
        self.assertIsNotNone(mei_note.get(_XMLNS))
    
    def test_notehead(self):
        '''
        precondition: Abjad NoteHead
        postcondition: mei note
        '''
        head = NoteHead("c'")
        mei_note = abjad_to_mei.note_to_note(head)
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(mei_note.attrib, {'pname': 'c', 'octave': '4'})
    
    def test_notehead_cautionary(self):
        '''
        precondition: Abjad NoteHead with cautionary natural
        postcondition: mei note Element with cautionary natural
        '''
        head = NoteHead("c'")
        head.is_cautionary = True
        mei_note = abjad_to_mei.note_to_note(head)
        self.assertAttribsEqual(mei_note.attrib, {'pname': 'c', 'octave': '4'})
        accid = mei_note.findall('./{}accid'.format(_MEINS))
        accid = accid[0]
        self.assertEqual(accid.tag, '{}accid'.format(_MEINS))
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(accid.attrib, {'accid': 'n', 'func': 'cautionary'})
    
    def test_notehead_forced(self):
        head = NoteHead("c'")
        head.is_forced = True
        mei_note = abjad_to_mei.note_to_note(head)
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(mei_note.attrib, {'pname': 'c', 'octave': '4', 'accid.ges': 'n', 'accid': 'n'})
        
    def test_notehead_accid(self):
        '''
        precondition: abjad NoteHead with accidental
        postcondition: mei note Element with accidental
        '''
        head = NoteHead("cf'")
        mei_note = abjad_to_mei.note_to_note(head)
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(mei_note.attrib, {'pname': 'c', 'octave': '4', 'accid.ges': 'f'})
        
    def test_notehead_accid_cautionary(self):
        '''
        precondition: Abjad NoteHead with cautionary accidental
        postcondition: mei note Element with cautionary accidental
        '''
        head = NoteHead("cf'")
        head.is_cautionary = True
        mei_note = abjad_to_mei.note_to_note(head)
        self.assertAttribsEqual(mei_note.attrib, {'pname': 'c', 'octave': '4'})
        accid = mei_note.findall('./{}accid'.format(_MEINS))
        accid = accid[0]
        self.assertEqual(accid.tag, '{}accid'.format(_MEINS))
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(accid.attrib, {'accid': 'f', 'func': 'cautionary'})
        
    def test_notehead_accid_forced(self):
        head = NoteHead("cf'")
        head.is_forced = True
        mei_note = abjad_to_mei.note_to_note(head)
        self.assertEqual(mei_note.tag, '{}note'.format(_MEINS))
        self.assertAttribsEqual(mei_note.attrib, {'pname': 'c', 'octave': '4', 'accid.ges': 'f', 'accid': 'f'})
    
    def test_rest(self):
        '''
        precondition: abjad rest with no dots.
        postcondition: mei rest with no dots.
        '''
        abjad_rest = Rest("r32")
        mei_rest = abjad_to_mei.rest_to_rest(abjad_rest)
        self.assertEqual(mei_rest.tag, '{}rest'.format(_MEINS))
        self.assertAttribsEqual(mei_rest.attrib, {'dur': '32'} )
        self.assertIsNotNone(mei_rest.get(_XMLNS))
        
    def test_rest_dotted(self):
        '''
        precondition: dotted abjad rest.
        postcondition: dotted mei rest.
        '''
        abjad_rest = Rest("r32..")
        mei_rest = abjad_to_mei.rest_to_rest(abjad_rest)
        self.assertEqual(mei_rest.tag, '{}rest'.format(_MEINS))
        self.assertAttribsEqual(mei_rest.attrib, {'dots': '2', 'dur': '32'})
        self.assertIsNotNone(mei_rest.get(_XMLNS))
    
    def test_chord_empty(self):
        '''
        precondition: abjad Chord with duration and no NoteHeads
        postcondition: mei chord Element with duration and no contained note Elements
        '''
        abjad_chord = Chord([],(1,4))
        mei_chord = abjad_to_mei.chord_to_chord(abjad_chord)
        self.assertAttribsEqual(mei_chord.attrib, {'dur': '4'})
        self.assertEqual(mei_chord.tag, '{}chord'.format(_MEINS))
        self.assertEqual(len(mei_chord), 0)
        self.assertIsNotNone(mei_chord.get(_XMLNS))
        
    def test_chord_empty_dotted(self):
        '''
        precondition: abjad Chord with dotted duration and no NoteHeads
        postcondition: mei chord Element with dotted duration and no contained note Elements
        '''
        abjad_chord = Chord([],(3,8))
        mei_chord = abjad_to_mei.chord_to_chord(abjad_chord)
        self.assertAttribsEqual(mei_chord.attrib, {'dur': '4','dots': '1'})
        self.assertEqual(mei_chord.tag, '{}chord'.format(_MEINS))
        self.assertEqual(len(mei_chord), 0)
        self.assertIsNotNone(mei_chord.get(_XMLNS))
    
    def test_chord_full(self):
        '''
        precondition: abjad Chord with duration and one or more NoteHeads
        postcondition: mei chord Element with duration and one or more contained note Elements
        '''
        abjad_chord = Chord("<c' d'>4")
        mei_chord = abjad_to_mei.chord_to_chord(abjad_chord)
        self.assertAttribsEqual(mei_chord.attrib, {'dur': '4'})
        self.assertEqual(mei_chord.tag, '{}chord'.format(_MEINS))
        self.assertAttribsEqual(mei_chord[0].attrib, {'pname': 'c', 'octave': '4'})
        self.assertAttribsEqual(mei_chord[1].attrib, {'pname': 'd', 'octave': '4'})
        self.assertIsNotNone(mei_chord.get(_XMLNS))
    
    def test_chord_full_dotted(self):
        '''
        precondition: abjad Chord with dotted duration and one or more NoteHeads
        postcondition: mei chord Element with dotted duration and one or more contained note Elements
        '''
        abjad_chord = Chord("<c' d'>4.")
        mei_chord = abjad_to_mei.chord_to_chord(abjad_chord)
        self.assertEqual(mei_chord.tag, '{}chord'.format(_MEINS))
        self.assertAttribsEqual(mei_chord.attrib, {'dur': '4', 'dots': '1'})
        self.assertAttribsEqual(mei_chord[0].attrib, {'pname': 'c', 'octave': '4'})
        self.assertAttribsEqual(mei_chord[1].attrib, {'pname': 'd', 'octave': '4'})
        self.assertIsNotNone(mei_chord.get(_XMLNS))
        
    def test_voice_to_layer_empty(self):
        '''
        precondition: empty abjad Voice
        postcondition: empty mei layer Element
        '''
        abjad_voice = Voice()
        mei_layer = abjad_to_mei.voice_to_layer(abjad_voice)
        self.assertEqual(mei_layer.tag, '{}layer'.format(_MEINS))
        self.assertAttribsEqual(mei_layer.attrib, {'n': '1'})
        self.assertEqual(len(mei_layer),0)
        self.assertIsNotNone(mei_layer.get(_XMLNS))
    
    def test_voice_to_layer_full(self):
        '''
        precondition: abjad Voice containing rest, note, and chord
        postcondition: mei layer Element containing rest, note and chord
        '''
        abjad_voice = Voice("r4 c'4 <c' d'>4")
        mei_layer = abjad_to_mei.voice_to_layer(abjad_voice)
        self.assertAttribsEqual(mei_layer.attrib, {'n': '1'})
        self.assertEqual(len(mei_layer), 3)
        self.assertEqual(mei_layer.tag, '{}layer'.format(_MEINS))
        self.assertEqual(mei_layer[0].tag, '{}rest'.format(_MEINS))
        self.assertEqual(mei_layer[1].tag, '{}note'.format(_MEINS))
        self.assertEqual(mei_layer[2].tag, '{}chord'.format(_MEINS))
        self.assertIsNotNone(mei_layer.get(_XMLNS))

    @mock.patch("lychee.converters.abjad_to_mei.chord_to_chord")
    @mock.patch("lychee.converters.abjad_to_mei.note_to_note")
    @mock.patch("lychee.converters.abjad_to_mei.rest_to_rest")
    def test_voice_to_layer_full_mock(self,mock_rest,mock_note, mock_chord):
        '''
        precondition: abjad Voice containing rest, note, and chord
        postcondition: mei layer Element containing rest, note and chord
        '''
        abjad_voice = Voice("r4 c'4 <c' d'>4")
        mock_rest.return_value = etree.Element('{}rest'.format(_MEINS))
        mock_note.return_value = etree.Element('{}note'.format(_MEINS))
        mock_chord.return_value = etree.Element('{}chord'.format(_MEINS))
        mei_layer = abjad_to_mei.voice_to_layer(abjad_voice)
        self.assertAttribsEqual(mei_layer.attrib, {'n': '1'})
        self.assertEqual(len(mei_layer), 3)
        self.assertEqual(mei_layer.tag, '{}layer'.format(_MEINS))
        self.assertEqual(mei_layer[0].tag, '{}rest'.format(_MEINS))
        self.assertEqual(mei_layer[1].tag, '{}note'.format(_MEINS))
        self.assertEqual(mei_layer[2].tag, '{}chord'.format(_MEINS))
        self.assertIsNotNone(mei_layer.get(_XMLNS))
    
    # inconsistencies: 
    # layer added en route to mei; shouldn't be there when translated back to abjad
    # sequential layers flattened into one layer; can't be recuperated
    # measures don't yet exist
    
    def test_staff_empty(self):
        '''
        precondition: empty abjad Staff
        postcondition: empty mei layer Element
        '''
        abjad_staff = Staff()
        
        mei_staff = abjad_to_mei.staff_to_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, '{}staff'.format(_MEINS))
        self.assertAttribsEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 0)
        self.assertIsNotNone(mei_staff.get(_XMLNS))
    
    # staff with one voice
    def test_staff_one_voice(self):
        '''
        precondition: abjad Staff containing only one Voice
        postcondition: mei staff Element containing one layer Element
        '''
        voice = Voice("r4 c'4 <c' d'>4")
        abjad_staff = Staff([voice])
        
        mei_staff = abjad_to_mei.staff_to_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, '{}staff'.format(_MEINS))
        self.assertAttribsEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, '{}layer'.format(_MEINS))
        self.assertIsNotNone(mei_staff.get(_XMLNS))

    @mock.patch("lychee.converters.abjad_to_mei.voice_to_layer")
    def test_staff_one_voice_mock(self,mock_layer):
        '''
        precondition: abjad Staff containing only one Voice
        postcondition: mei staff Element containing one layer Element
        '''
        voice = Voice("r4 c'4 <c' d'>4")
        abjad_staff = Staff([voice])
        mock_layer.return_value = etree.Element('{}layer'.format(_MEINS))
        
        mei_staff = abjad_to_mei.staff_to_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, '{}staff'.format(_MEINS))
        self.assertAttribsEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, '{}layer'.format(_MEINS))
        self.assertIsNotNone(mei_staff.get(_XMLNS))
        
        
    # staff with parallel voices (enumerate n based on staff n)
    def test_staff_parallel(self):
        '''
        precondition: abjad Staff containing two or more parallel voices
        postcondition: mei staff Element containing two or more layer Elements
        '''
        voice_one = Voice("r4 c'4 <c' d'>4")
        voice_two = Voice("r4 d'4 <d' e'>4")
        abjad_staff = Staff([voice_one, voice_two])
        abjad_staff.is_simultaneous = True
        
        mei_staff = abjad_to_mei.staff_to_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, '{}staff'.format(_MEINS))
        self.assertAttribsEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 2)
        self.assertEqual(mei_staff[0].tag, '{}layer'.format(_MEINS))
        self.assertEqual(mei_staff[0].get('n'),'1')
        self.assertEqual(mei_staff[1].tag, '{}layer'.format(_MEINS))
        self.assertEqual(mei_staff[1].get('n'),'2')
        self.assertIsNotNone(mei_staff.get(_XMLNS))

    @mock.patch("lychee.converters.abjad_to_mei.voice_to_layer")
    def test_staff_parallel_mock(self,mock_layer):
        '''
        precondition: abjad Staff containing two or more parallel voices
        postcondition: mei staff Element containing two or more layer Elements
        '''
        voice_one = Voice("r4 c'4 <c' d'>4")
        voice_two = Voice("r4 d'4 <d' e'>4")
        abjad_staff = Staff([voice_one, voice_two])
        abjad_staff.is_simultaneous = True
        mock_layer.side_effect = lambda x: etree.Element('{}layer'.format(_MEINS))
        
        mei_staff = abjad_to_mei.staff_to_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, '{}staff'.format(_MEINS))
        self.assertAttribsEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 2)
        self.assertEqual(mei_staff[0].tag, '{}layer'.format(_MEINS))
        self.assertEqual(mei_staff[0].get('n'),'1')
        self.assertEqual(mei_staff[1].tag, '{}layer'.format(_MEINS))
        self.assertEqual(mei_staff[1].get('n'),'2')
        self.assertIsNotNone(mei_staff.get(_XMLNS))

    # staff with consecutive voices
    def test_staff_consecutive(self):
        '''
        precondition: abjad Staff containing two or more consecutive Voices
        postcondition: mei staff Element containing one layer Element
        '''
        voice_one = Voice("r4 c'4 <c' d'>4")
        voice_two = Voice("r4 d'4 <d' e'>4")
        abjad_staff = Staff([voice_one, voice_two])
        
        mei_staff = abjad_to_mei.staff_to_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, '{}staff'.format(_MEINS))
        self.assertAttribsEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, '{}layer'.format(_MEINS))
        self.assertEqual(mei_staff[0].get('n'),'1')
        self.assertIsNotNone(mei_staff.get(_XMLNS))

    @mock.patch("lychee.converters.abjad_to_mei.voice_to_layer")
    def test_staff_consecutive_mock(self,mock_layer):
        '''
        precondition: abjad Staff containing two or more consecutive Voices
        postcondition: mei staff Element containing one layer Element
        '''
        voice_one = Voice("r4 c'4 <c' d'>4")
        voice_two = Voice("r4 d'4 <d' e'>4")
        abjad_staff = Staff([voice_one, voice_two])
        mock_layer.return_value = etree.Element('{}layer'.format(_MEINS),n='1')
        
        mei_staff = abjad_to_mei.staff_to_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, '{}staff'.format(_MEINS))
        self.assertAttribsEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, '{}layer'.format(_MEINS))
        self.assertEqual(mei_staff[0].get('n'),'1')
        self.assertIsNotNone(mei_staff.get(_XMLNS))
    
    # staff with leaves and no voice(s)
    def test_staff_leaves(self):
        '''
        precondition: abjad Staff containing leaves and no Voices
        postcondition: mei layer Element containing children leaf Elements
        '''
        abjad_staff = Staff("r4 c'4 <c' d'>4")
        
        mei_staff = abjad_to_mei.staff_to_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, '{}staff'.format(_MEINS))
        self.assertAttribsEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, '{}layer'.format(_MEINS))
        self.assertEqual(mei_staff[0].get('n'),'1')
        self.assertIsNotNone(mei_staff.get(_XMLNS))

    @mock.patch("lychee.converters.abjad_to_mei.voice_to_layer")
    def test_staff_leaves_mock(self, mock_layer):
        '''
        precondition: abjad Staff containing leaves and no Voices
        postcondition: mei layer Element containing children leaf Elements
        '''
        abjad_staff = Staff("r4 c'4 <c' d'>4")
        mock_layer.return_value = etree.Element('{}layer'.format(_MEINS), n='1')
        
        mei_staff = abjad_to_mei.staff_to_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, '{}staff'.format(_MEINS))
        self.assertAttribsEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, '{}layer'.format(_MEINS))
        self.assertEqual(mei_staff[0].get('n'),'1')
        self.assertIsNotNone(mei_staff.get(_XMLNS))
    
    # staff with some combination of leaves and voices
    def test_staff_leaves_and_voices(self):
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
        
        mei_staff = abjad_to_mei.staff_to_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, '{}staff'.format(_MEINS))
        self.assertAttribsEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, '{}layer'.format(_MEINS))
        self.assertEqual(mei_staff[0].get('n'),'1')
        self.assertEqual(len(mei_staff[0]), 8)
        self.assertIsNotNone(mei_staff.get(_XMLNS))

    @mock.patch("lychee.converters.abjad_to_mei.voice_to_layer")
    def test_staff_leaves_and_voices_mock(self, mock_layer):
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
        dummy = etree.Element('{}layer'.format(_MEINS),n='1')
        for _ in range(8):
            etree.SubElement(dummy, '{}note'.format(_MEINS))
        mock_layer.return_value = dummy
        
        mei_staff = abjad_to_mei.staff_to_staff(abjad_staff)
        
        self.assertEqual(1, mock_layer.call_count)
        self.assertEqual(mei_staff.tag, '{}staff'.format(_MEINS))
        self.assertAttribsEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, '{}layer'.format(_MEINS))
        self.assertEqual(mei_staff[0].get('n'),'1')
        self.assertEqual(len(mei_staff[0]), 8)
        self.assertIsNotNone(mei_staff.get(_XMLNS))
    
    def test_section_empty(self):
        '''
        precondition: empty abjad Score
        postcondition: empty mei section Element
        '''
        abjad_score = Score()
        mei_section = abjad_to_mei.score_to_section(abjad_score)
        self.assertEqual(mei_section.tag, '{}section'.format(_MEINS))
        self.assertEqual(mei_section.get('n'), '1')
        self.assertEqual(len(mei_section), 0)
        self.assertIsNotNone(mei_section.get(_XMLNS))
        
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
        
        mei_section = abjad_to_mei.score_to_section(abjad_score)
        
        self.assertEqual(mei_section.tag, '{}section'.format(_MEINS))
        self.assertEqual(len(mei_section), 5)
        self.assertEqual(mei_section[0].tag, '{}scoreDef'.format(_MEINS))
        self.assertEqual(len(mei_section[0]), 1)
        self.assertEqual(mei_section[0][0].tag, '{}staffGrp'.format(_MEINS))
        self.assertEqual(len(mei_section[0][0]), 3)
        self.assertEqual(mei_section[0][0][0].tag, '{}staffDef'.format(_MEINS))
        self.assertEqual(mei_section[0][0][0].get('lines'), '5')
        self.assertEqual(mei_section[0][0][0].get('n'), '1')
        self.assertEqual(mei_section[0][0][1].tag, '{}staffGrp'.format(_MEINS))
        self.assertEqual(mei_section[0][0][1][0].tag, '{}staffDef'.format(_MEINS))
        self.assertEqual(mei_section[0][0][1][0].get('lines'), '5')
        self.assertEqual(mei_section[0][0][1][0].get('n'), '2')
        self.assertEqual(mei_section[0][0][1][1].tag, '{}staffDef'.format(_MEINS))
        self.assertEqual(mei_section[0][0][1][1].get('n'), '3')
        self.assertEqual(mei_section[0][0][1][1].get('lines'), '5')
        self.assertEqual(mei_section[0][0][2].tag, '{}staffDef'.format(_MEINS))
        self.assertEqual(mei_section[0][0][2].get('n'), '4')
        self.assertEqual(mei_section[0][0][2].get('lines'), '5')
        for x in range(1,5):
            self.assertEqual(mei_section[x].tag, '{}staff'.format(_MEINS))
            self.assertEqual(mei_section[x].get('n'), str(x))
        self.assertIsNotNone(mei_section.get(_XMLNS))

    @mock.patch("lychee.converters.abjad_to_mei.staff_to_staff")
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
        mock_section.side_effect = lambda x: etree.Element('{}staff'.format(_MEINS),n='1')
        
        mei_section = abjad_to_mei.score_to_section(abjad_score)
        
        self.assertEqual(mei_section.tag, '{}section'.format(_MEINS))
        self.assertEqual(len(mei_section), 5)
        self.assertEqual(mei_section[0].tag, '{}scoreDef'.format(_MEINS))
        self.assertEqual(len(mei_section[0]), 1)
        self.assertEqual(mei_section[0][0].tag, '{}staffGrp'.format(_MEINS))
        self.assertEqual(len(mei_section[0][0]), 3)
        self.assertEqual(mei_section[0][0][0].tag, '{}staffDef'.format(_MEINS))
        self.assertEqual(mei_section[0][0][0].get('lines'), '5')
        self.assertEqual(mei_section[0][0][0].get('n'), '1')
        self.assertEqual(mei_section[0][0][1].tag, '{}staffGrp'.format(_MEINS))
        self.assertEqual(mei_section[0][0][1][0].tag, '{}staffDef'.format(_MEINS))
        self.assertEqual(mei_section[0][0][1][0].get('lines'), '5')
        self.assertEqual(mei_section[0][0][1][0].get('n'), '2')
        self.assertEqual(mei_section[0][0][1][1].tag, '{}staffDef'.format(_MEINS))
        self.assertEqual(mei_section[0][0][1][1].get('n'), '3')
        self.assertEqual(mei_section[0][0][1][1].get('lines'), '5')
        self.assertEqual(mei_section[0][0][2].tag, '{}staffDef'.format(_MEINS))
        self.assertEqual(mei_section[0][0][2].get('n'), '4')
        self.assertEqual(mei_section[0][0][2].get('lines'), '5')
        for x in range(1,5):
            self.assertEqual(mei_section[x].tag, '{}staff'.format(_MEINS))
            self.assertEqual(mei_section[x].get('n'), str(x))
        self.assertIsNotNone(mei_section.get(_XMLNS))

    def test_tuplet_to_tupletspan_empty_fixed(self):  
        '''
        precondition: empty abjad FixedDuratonTuplet
        postcondition: list containing mei tupletspan Element with dur attr
        '''  
        abjad_tuplet = FixedDurationTuplet(Duration(1,4), [])
        
        mei_element = abjad_to_mei.tuplet_to_tupletspan(abjad_tuplet)
        
        self.assertTrue(isinstance(mei_element, etree._Element))
        tupletspan = mei_element
        self.assertEqual(tupletspan.tag, '{}tupletspan'.format(_MEINS))
        self.assertEqual(tupletspan.get('dur'), '4')
        self.assertIsNone(tupletspan.get('dots'))
        self.assertIsNone(tupletspan.get('num'))
        self.assertIsNone(tupletspan.get('numBase'))
        self.assertIsNone(tupletspan.get('startid'))
        self.assertIsNone(tupletspan.get('endid'))
        self.assertIsNotNone(tupletspan.get(_XMLNS))
    
    def test_tuplet_to_tupletspan_empty_fixed_dotted(self):  
        '''
        precondition: empty abjad FixedDuratonTuplet
        postcondition: list containing mei tupletspan Element with dur attr
        '''  
        abjad_tuplet = FixedDurationTuplet(Duration(3,8), [])
        
        mei_element = abjad_to_mei.tuplet_to_tupletspan(abjad_tuplet)

        self.assertTrue(isinstance(mei_element, etree._Element))
        tupletspan = mei_element
        self.assertEqual(tupletspan.tag, '{}tupletspan'.format(_MEINS))
        self.assertEqual(tupletspan.get('dur'), '4')
        self.assertEqual(tupletspan.get('dots'), '1')
        self.assertIsNone(tupletspan.get('num'))
        self.assertIsNone(tupletspan.get('numBase'))
        self.assertIsNone(tupletspan.get('startid'))
        self.assertIsNone(tupletspan.get('endid'))
        self.assertIsNotNone(tupletspan.get(_XMLNS))
    
    def test_tuplet_to_tupletspan_empty(self):  
        '''
        precondition: empty abjad Tuplet with fixed Multiplier
        postcondition: list containing mei tupletspan Element with num and numBase attrs
        '''  
        abjad_tuplet = Tuplet(Multiplier(2,3), [])
        
        mei_element = abjad_to_mei.tuplet_to_tupletspan(abjad_tuplet)
        
        self.assertTrue(isinstance(mei_element, etree._Element))
        tupletspan = mei_element
        self.assertEqual(tupletspan.tag, '{}tupletspan'.format(_MEINS))
        self.assertEqual(tupletspan.get('dur'), None)
        self.assertEqual(tupletspan.get('dots'), None)
        self.assertEqual(tupletspan.get('num'), '3')
        self.assertEqual(tupletspan.get('numBase'), '2')
        self.assertEqual(tupletspan.get('startid'), None)
        self.assertEqual(tupletspan.get('endid'), None)
        self.assertIsNotNone(tupletspan.get(_XMLNS))
    
    def test_tuplet_to_tupletspan_full(self):
        '''
        precondition: abjad Tuplet containing leaves
        postcondition: list containing mei tupletspan Element followed by leaf Elements
        '''
        # returns list containing tupletspan followed by leaf elements
        abjad_tuplet = Tuplet(Multiplier(2,3), "c'8 c' c'")
        
        mei_elements = abjad_to_mei.tuplet_to_tupletspan(abjad_tuplet)
        
        self.assertTrue(isinstance(mei_elements, list))
        self.assertEqual(len(mei_elements), 4)
        self.assertEqual(mei_elements[0].tag, '{}tupletspan'.format(_MEINS))
        self.assertEqual(mei_elements[0].get('dur'), '4')
        self.assertIsNone(mei_elements[0].get('dots'))
        self.assertEqual(mei_elements[0].get('num'), '3')
        self.assertEqual(mei_elements[0].get('numBase'), '2')
        self.assertEqual(mei_elements[0].get('startid'), mei_elements[1].get(_XMLNS))
        self.assertEqual(mei_elements[0].get('endid'), mei_elements[-1].get(_XMLNS))
        chunked_plist = mei_elements[0].get('plist').split()
        self.assertEqual(len(chunked_plist), 3)
        for note_element in mei_elements[1:]:
            self.assertTrue(note_element.get(_XMLNS) in chunked_plist)

    @mock.patch("lychee.converters.abjad_to_mei.leaf_to_element")
    def test_tuplet_to_tupletspan_full_mock(self, mock_element):
        '''
        precondition: abjad Tuplet containing leaves
        postcondition: list containing mei tupletspan Element followed by leaf Elements
        '''
        # returns list containing tupletspan followed by leaf elements
        abjad_tuplet = Tuplet(Multiplier(2,3), "c'8 c' c'")
        mock_element.side_effect = lambda x: etree.Element('{}note'.format(_MEINS), pname='c', octave='4', dur='8')
        
        mei_elements = abjad_to_mei.tuplet_to_tupletspan(abjad_tuplet)
        
        self.assertTrue(isinstance(mei_elements, list))
        self.assertEqual(len(mei_elements), 4)
        self.assertEqual(mei_elements[0].tag, '{}tupletspan'.format(_MEINS))
        self.assertEqual(mei_elements[0].get('dur'), '4')
        self.assertIsNone(mei_elements[0].get('dots'))
        self.assertEqual(mei_elements[0].get('num'), '3')
        self.assertEqual(mei_elements[0].get('numBase'), '2')
        self.assertEqual(mei_elements[0].get('startid'), mei_elements[1].get(_XMLNS))
        self.assertEqual(mei_elements[0].get('endid'), mei_elements[-1].get(_XMLNS))
        chunked_plist = mei_elements[0].get('plist').split()
        self.assertEqual(len(chunked_plist), 3)
        for note_element in mei_elements[1:]:
            self.assertTrue(note_element.get(_XMLNS) in chunked_plist)
    
    def test_tuplet_to_tupletspan_full_dotted(self):
        '''
        precondition: abjad Tuplet of dotted duration containing leaves
        postcondition: list containing mei tupletspan Element with dots attr followed by leaf Elements
        '''
        abjad_tuplet = Tuplet()
        abjad_tuplet = abjad_tuplet.from_duration_and_ratio(Duration(3,8), [1] * 5)
        
        mei_elements = abjad_to_mei.tuplet_to_tupletspan(abjad_tuplet)
        
        self.assertTrue(isinstance(mei_elements, list))
        self.assertEqual(len(mei_elements), 6)
        self.assertEqual(mei_elements[0].tag, '{}tupletspan'.format(_MEINS))
        self.assertEqual(mei_elements[0].get('dur'), '4')
        self.assertEqual(mei_elements[0].get('dots'), '1')
        self.assertEqual(mei_elements[0].get('num'), '5')
        self.assertEqual(mei_elements[0].get('numBase'), '3')
        self.assertEqual(mei_elements[0].get('startid'), mei_elements[1].get(_XMLNS))
        self.assertEqual(mei_elements[0].get('endid'), mei_elements[-1].get(_XMLNS))
        chunked_plist = mei_elements[0].get('plist').split()
        self.assertEqual(len(chunked_plist), 5)
        for note_element in mei_elements[1:]:
            self.assertTrue(note_element.get(_XMLNS) in chunked_plist)

    @mock.patch("lychee.converters.abjad_to_mei.leaf_to_element")
    def test_tuplet_to_tupletspan_full_dotted_mock(self, mock_element):
        '''
        precondition: abjad Tuplet of dotted duration containing leaves
        postcondition: list containing mei tupletspan Element with dots attr followed by leaf Elements
        '''
        abjad_tuplet = Tuplet()
        abjad_tuplet = abjad_tuplet.from_duration_and_ratio(Duration(3,8), [1] * 5)
        mock_element.side_effect = lambda x: etree.Element('{}note'.format(_MEINS), pname='c', octave='4', dur='8')
        
        mei_elements = abjad_to_mei.tuplet_to_tupletspan(abjad_tuplet)
        
        self.assertTrue(isinstance(mei_elements, list))
        self.assertEqual(len(mei_elements), 6)
        self.assertEqual(mei_elements[0].tag, '{}tupletspan'.format(_MEINS))
        self.assertEqual(mei_elements[0].get('dur'), '4')
        self.assertEqual(mei_elements[0].get('dots'), '1')
        self.assertEqual(mei_elements[0].get('num'), '5')
        self.assertEqual(mei_elements[0].get('numBase'), '3')
        self.assertEqual(mei_elements[0].get('startid'), mei_elements[1].get(_XMLNS))
        self.assertEqual(mei_elements[0].get('endid'), mei_elements[-1].get(_XMLNS))
        chunked_plist = mei_elements[0].get('plist').split()
        self.assertEqual(len(chunked_plist), 5)
        for note_element in mei_elements[1:]:
            self.assertTrue(note_element.get(_XMLNS) in chunked_plist)
    
    def test_tuplet_to_tupletspan_full_nested(self):
        '''
        precondition: Abjad Tuplet containing Leaves and a Tuplet.
        postcondition: list of mei elements containing tupletspan followed by leaf/tupletspan Elements.
        '''
        inner_tuplet = FixedDurationTuplet((1,4), "c'8 c' c'")
        outer_tuplet = FixedDurationTuplet((3,8), [])
        outer_tuplet.append(inner_tuplet)
        outer_tuplet.extend("d'8 d' d'")
        
        mei_elements = abjad_to_mei.tuplet_to_tupletspan(outer_tuplet)
        
        self.assertTrue(isinstance(mei_elements, list))
        self.assertEqual(len(mei_elements), 8)
        outer_tupletspan = mei_elements[0]
        inner_tupletspan = mei_elements[1]
        self.assertEqual(outer_tupletspan.tag, '{}tupletspan'.format(_MEINS))
        self.assertEqual(outer_tupletspan.get('dur'), '4')
        self.assertEqual(outer_tupletspan.get('dots'), '1')
        self.assertEqual(outer_tupletspan.get('num'), '5')
        self.assertEqual(outer_tupletspan.get('numBase'), '3')
        self.assertEqual(inner_tupletspan.tag, '{}tupletspan'.format(_MEINS))
        self.assertEqual(inner_tupletspan.get('dur'), '4')
        self.assertIsNone(inner_tupletspan.get('dots'))
        self.assertEqual(inner_tupletspan.get('num'), '3')
        self.assertEqual(inner_tupletspan.get('numBase'), '2')
        for note in mei_elements[2:]:
            self.assertEqual(note.tag, '{}note'.format(_MEINS))
        inner_ids = mei_elements[1].get('plist').split()
        for inner_tuplet_note in mei_elements[2:5]:
            self.assertTrue(inner_tuplet_note.get(_XMLNS) in inner_ids)
        self.assertEqual(mei_elements[1].get('startid'), mei_elements[2].get(_XMLNS))
        self.assertEqual(mei_elements[1].get('endid'), mei_elements[4].get(_XMLNS))
        outer_ids = mei_elements[0].get('plist').split()
        for outer_tuplet_element in mei_elements[1:]:
            self.assertTrue(outer_tuplet_element.get(_XMLNS) in outer_ids)
        self.assertEqual(mei_elements[0].get('startid'), mei_elements[1].get(_XMLNS))
        self.assertEqual(mei_elements[0].get('endid'), mei_elements[-1].get(_XMLNS))
        for note_element in mei_elements[1:]:
            self.assertTrue(note_element.get(_XMLNS) in outer_ids)

    @mock.patch("lychee.converters.abjad_to_mei.leaf_to_element")
    def test_tuplet_to_tupletspan_full_nested_mock(self, mock_element):
        '''
        precondition: Abjad Tuplet containing Leaves and a Tuplet.
        postcondition: list of mei elements containing tupletspan followed by leaf/tupletspan Elements.
        '''
        inner_tuplet = FixedDurationTuplet((1,4), "c'8 c' c'")
        outer_tuplet = FixedDurationTuplet((3,8), [])
        outer_tuplet.append(inner_tuplet)
        outer_tuplet.extend("d'8 d' d'")
        mock_element.side_effect = lambda x: etree.Element('{}note'.format(_MEINS), pname='c', octave='4', dur='8')
        
        mei_elements = abjad_to_mei.tuplet_to_tupletspan(outer_tuplet)
        
        self.assertTrue(isinstance(mei_elements, list))
        self.assertEqual(len(mei_elements), 8)
        outer_tupletspan = mei_elements[0]
        inner_tupletspan = mei_elements[1]
        self.assertEqual(outer_tupletspan.tag, '{}tupletspan'.format(_MEINS))
        self.assertEqual(outer_tupletspan.get('dur'), '4')
        self.assertEqual(outer_tupletspan.get('dots'), '1')
        self.assertEqual(outer_tupletspan.get('num'), '5')
        self.assertEqual(outer_tupletspan.get('numBase'), '3')
        self.assertEqual(inner_tupletspan.tag, '{}tupletspan'.format(_MEINS))
        self.assertEqual(inner_tupletspan.get('dur'), '4')
        self.assertIsNone(inner_tupletspan.get('dots'))
        self.assertEqual(inner_tupletspan.get('num'), '3')
        self.assertEqual(inner_tupletspan.get('numBase'), '2')
        for note in mei_elements[2:]:
            self.assertEqual(note.tag, '{}note'.format(_MEINS))
        inner_ids = mei_elements[1].get('plist').split()
        for inner_tuplet_note in mei_elements[2:5]:
            self.assertTrue(inner_tuplet_note.get(_XMLNS) in inner_ids)
        self.assertEqual(mei_elements[1].get('startid'), mei_elements[2].get(_XMLNS))
        self.assertEqual(mei_elements[1].get('endid'), mei_elements[4].get(_XMLNS))
        outer_ids = mei_elements[0].get('plist').split()
        for outer_tuplet_element in mei_elements[1:]:
            self.assertTrue(outer_tuplet_element.get(_XMLNS) in outer_ids)
        self.assertEqual(mei_elements[0].get('startid'), mei_elements[1].get(_XMLNS))
        self.assertEqual(mei_elements[0].get('endid'), mei_elements[-1].get(_XMLNS))
        for note_element in mei_elements[1:]:
            self.assertTrue(note_element.get(_XMLNS) in outer_ids)