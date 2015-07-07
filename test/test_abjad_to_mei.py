from lxml import etree as ETree
import mock
from abjad.tools.scoretools.Note import Note
from abjad.tools.scoretools.Rest import Rest
from abjad.tools.scoretools.Chord import Chord
from abjad.tools.scoretools.NoteHead import NoteHead
from abjad.tools.scoretools.Voice import Voice
from abjad.tools.scoretools.Staff import Staff
from abjad.tools.scoretools.StaffGroup import StaffGroup
from abjad.tools.scoretools.Score import Score
import abjad_to_mei
import unittest

class TestAbjadToMeiConversions(unittest.TestCase):
    
    # note conversion
    
    def test_note_basic(self):
        '''
        precondition: abjad note with duration, pitch name, and octave string
        postcondition: mei element
        '''
        abjad_note = Note("c'4")
        mei_note = abjad_to_mei.abjad_note_to_mei_note(abjad_note)
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(mei_note.attrib, {'dur': '4', 'pname': 'c', 'octave': '4'})
    
    def test_note_dotted(self):
        '''
        precondition: abjad note with dot
        postcondition: mei element with dots attribute
        '''
        abjad_note = Note("c'4.")
        mei_note = abjad_to_mei.abjad_note_to_mei_note(abjad_note)
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(mei_note.attrib, {'dots': '1', 'dur': '4', 'pname': 'c', 'octave': '4'})
    
    def test_note_accid(self):
        '''
        precondition: abjad note with accidental, neither forced nor cautionary
        postcondition: mei element with gestural accidental
        '''
        abjad_note = Note("cf'4")
        mei_note = abjad_to_mei.abjad_note_to_mei_note(abjad_note)
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(mei_note.attrib, {'accid.ges': 'f', 'dur': '4', 'pname': 'c', 'octave': '4'})
        
    def test_note_accid_and_cautionary(self):
        '''
        preconditions: abjad note with cautionary accidental
        postconditions: mei element containing cautionary accidental subelement
        '''
        abjad_note = Note("cf'?4")
        mei_note = abjad_to_mei.abjad_note_to_mei_note(abjad_note)
        self.assertEqual(mei_note.attrib, {'dur': '4', 'pname': 'c', 'octave': '4'})
        accid = mei_note.findall('./accid')
        accid = accid[0]
        self.assertEqual(accid.tag, 'accid')
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(accid.attrib, {'accid': 'f', 'func': 'cautionary'})
    
    def test_note_accid_and_forced(self):
        '''
        preconditions: abjad note with forced accidental
        postconditions: mei element with both written and gestural accidentals
        '''
        abjad_note = Note("cf'!4")
        mei_note = abjad_to_mei.abjad_note_to_mei_note(abjad_note)
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(mei_note.attrib, {'accid.ges': 'f', 'accid': 'f', 'dur': '4', 'pname': 'c', 'octave': '4'})
    
    def test_note_cautionary(self):
        '''
        precondition: abjad note with no accidental and cautionary natural
        postcondition: mei element containing cautionary accidental subelement set to natural
        '''
        abjad_note = Note("c'?4")
        mei_note = abjad_to_mei.abjad_note_to_mei_note(abjad_note)
        self.assertEqual(mei_note.attrib, {'dur': '4', 'pname': 'c', 'octave': '4'})
        accid = mei_note.findall('./accid')
        accid = accid[0]
        self.assertEqual(accid.tag, 'accid')
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(accid.attrib, {'accid': 'n', 'func': 'cautionary'})
    
    def test_note_forced(self):
        '''
        precondition: abjad note with no accidental and forced accidental
        postcondition: mei element with both accid.ges and accid attributes set
        '''
        abjad_note = Note("c'!4")
        mei_note = abjad_to_mei.abjad_note_to_mei_note(abjad_note)
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(mei_note.attrib, {'accid.ges': 'n', 'accid': 'n', 'dur': '4', 'pname': 'c', 'octave': '4'} )
    
    def test_notehead(self):
        '''
        precondition: Abjad NoteHead
        postcondition: mei note
        '''
        head = NoteHead("c'")
        mei_note = abjad_to_mei.abjad_note_to_mei_note(head)
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(mei_note.attrib, {'pname': 'c', 'octave': '4'})
    
    def test_notehead_cautionary(self):
        '''
        precondition: Abjad NoteHead with cautionary natural
        postcondition: mei note Element with cautionary natural
        '''
        head = NoteHead("c'")
        head.is_cautionary = True
        mei_note = abjad_to_mei.abjad_note_to_mei_note(head)
        self.assertEqual(mei_note.attrib, {'pname': 'c', 'octave': '4'})
        accid = mei_note.findall("./accid")
        accid = accid[0]
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(accid.attrib, {'accid': 'n', 'func': 'cautionary'})
    
    def test_notehead_forced(self):
        head = NoteHead("c'")
        head.is_forced = True
        mei_note = abjad_to_mei.abjad_note_to_mei_note(head)
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(mei_note.attrib, {'pname': 'c', 'octave': '4', 'accid.ges': 'n', 'accid': 'n'})
        
    def test_notehead_accid(self):
        '''
        precondition: abjad NoteHead with accidental
        postcondition: mei note Element with accidental
        '''
        head = NoteHead("cf'")
        mei_note = abjad_to_mei.abjad_note_to_mei_note(head)
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(mei_note.attrib, {'pname': 'c', 'octave': '4', 'accid.ges': 'f'})
        
    def test_notehead_accid_cautionary(self):
        '''
        precondition: Abjad NoteHead with cautionary accidental
        postcondition: mei note Element with cautionary accidental
        '''
        head = NoteHead("cf'")
        head.is_cautionary = True
        mei_note = abjad_to_mei.abjad_note_to_mei_note(head)
        self.assertEqual(mei_note.attrib, {'pname': 'c', 'octave': '4'})
        accid = mei_note.findall("./accid")
        accid = accid[0]
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(accid.attrib, {'accid': 'f', 'func': 'cautionary'})
        
    def test_notehead_accid_forced(self):
        head = NoteHead("cf'")
        head.is_forced = True
        mei_note = abjad_to_mei.abjad_note_to_mei_note(head)
        self.assertEqual(mei_note.tag, 'note')
        self.assertEqual(mei_note.attrib, {'pname': 'c', 'octave': '4', 'accid.ges': 'f', 'accid': 'f'})
    
    def test_rest(self):
        '''
        precondition: abjad rest with no dots.
        postcondition: mei rest with no dots.
        '''
        abjad_rest = Rest("r32")
        mei_rest = abjad_to_mei.abjad_rest_to_mei_rest(abjad_rest)
        self.assertEqual(mei_rest.tag, 'rest')
        self.assertEqual(mei_rest.attrib, {'dur': '32'} )
        
    def test_rest_dotted(self):
        '''
        precondition: dotted abjad rest.
        postcondition: dotted mei rest.
        '''
        abjad_rest = Rest("r32..")
        mei_rest = abjad_to_mei.abjad_rest_to_mei_rest(abjad_rest)
        self.assertEqual(mei_rest.tag, 'rest')
        self.assertEqual(mei_rest.attrib, {'dots': '2', 'dur': '32'})
    
    def test_chord_empty(self):
        '''
        precondition: abjad Chord with duration and no NoteHeads
        postcondition: mei chord Element with duration and no contained note Elements
        '''
        abjad_chord = Chord([],(1,4))
        mei_chord = abjad_to_mei.abjad_chord_to_mei_chord(abjad_chord)
        self.assertEqual(mei_chord.attrib, {'dur': '4'})
        self.assertEqual(mei_chord.tag, 'chord')
        self.assertEqual(len(mei_chord), 0)
        
    def test_chord_empty_dotted(self):
        '''
        precondition: abjad Chord with dotted duration and no NoteHeads
        postcondition: mei chord Element with dotted duration and no contained note Elements
        '''
        abjad_chord = Chord([],(3,8))
        mei_chord = abjad_to_mei.abjad_chord_to_mei_chord(abjad_chord)
        self.assertEqual(mei_chord.attrib, {'dur': '4','dots': '1'})
        self.assertEqual(mei_chord.tag, 'chord')
        self.assertEqual(len(mei_chord), 0)
    
    def test_chord_full(self):
        '''
        precondition: abjad Chord with duration and one or more NoteHeads
        postcondition: mei chord Element with duration and one or more contained note Elements
        '''
        abjad_chord = Chord("<c' d'>4")
        mei_chord = abjad_to_mei.abjad_chord_to_mei_chord(abjad_chord)
        self.assertEqual(mei_chord.attrib, {'dur': '4'})
        self.assertEqual(mei_chord.tag, 'chord')
        self.assertEqual(mei_chord[0].attrib, {'pname': 'c', 'octave': '4'})
        self.assertEqual(mei_chord[1].attrib, {'pname': 'd', 'octave': '4'})
    
    def test_chord_full_dotted(self):
        '''
        precondition: abjad Chord with dotted duration and one or more NoteHeads
        postcondition: mei chord Element with dotted duration and one or more contained note Elements
        '''
        abjad_chord = Chord("<c' d'>4.")
        mei_chord = abjad_to_mei.abjad_chord_to_mei_chord(abjad_chord)
        self.assertEqual(mei_chord.tag, 'chord')
        self.assertEqual(mei_chord.attrib, {'dur': '4', 'dots': '1'})
        self.assertEqual(mei_chord[0].attrib, {'pname': 'c', 'octave': '4'})
        self.assertEqual(mei_chord[1].attrib, {'pname': 'd', 'octave': '4'})
        
    def test_voice_to_layer_empty(self):
        '''
        precondition: empty abjad Voice
        postcondition: empty mei layer Element
        '''
        abjad_voice = Voice()
        mei_layer = abjad_to_mei.abjad_voice_to_mei_layer(abjad_voice)
        self.assertEqual(mei_layer.tag, 'layer')
        self.assertEqual(mei_layer.attrib, {'n': '1'})
        self.assertEqual(len(mei_layer),0)
    
    def test_voice_to_layer_full(self):
        '''
        precondition: abjad Voice containing rest, note, and chord
        postcondition: mei layer Element containing rest, note and chord
        '''
        abjad_voice = Voice("r4 c'4 <c' d'>4")
        mei_layer = abjad_to_mei.abjad_voice_to_mei_layer(abjad_voice)
        self.assertEqual(mei_layer.attrib, {'n': '1'})
        self.assertEqual(len(mei_layer), 3)
        self.assertEqual(mei_layer.tag, 'layer')
        self.assertEqual(mei_layer[0].tag, 'rest')
        self.assertEqual(mei_layer[1].tag, 'note')
        self.assertEqual(mei_layer[2].tag, 'chord')
   
    @mock.patch("abjad_to_mei.abjad_chord_to_mei_chord")
    @mock.patch("abjad_to_mei.abjad_note_to_mei_note")
    @mock.patch("abjad_to_mei.abjad_rest_to_mei_rest")
    def test_voice_to_layer_full_mock(self,mock_rest,mock_note, mock_chord):
        '''
        precondition: abjad Voice containing rest, note, and chord
        postcondition: mei layer Element containing rest, note and chord
        '''
        abjad_voice = Voice("r4 c'4 <c' d'>4")
        mock_rest.return_value = ETree.Element('rest')
        mock_note.return_value = ETree.Element('note')
        mock_chord.return_value = ETree.Element('chord')
        mei_layer = abjad_to_mei.abjad_voice_to_mei_layer(abjad_voice)
        self.assertEqual(mei_layer.attrib, {'n': '1'})
        self.assertEqual(len(mei_layer), 3)
        self.assertEqual(mei_layer.tag, 'layer')
        self.assertEqual(mei_layer[0].tag, 'rest')
        self.assertEqual(mei_layer[1].tag, 'note')
        self.assertEqual(mei_layer[2].tag, 'chord')
    
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
        
        mei_staff = abjad_to_mei.abjad_staff_to_mei_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, 'staff')
        self.assertEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 0)
    
    # staff with one voice
    def test_staff_one_voice(self):
        '''
        precondition: abjad Staff containing only one Voice
        postcondition: mei staff Element containing one layer Element
        '''
        voice = Voice("r4 c'4 <c' d'>4")
        abjad_staff = Staff([voice])
        
        mei_staff = abjad_to_mei.abjad_staff_to_mei_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, 'staff')
        self.assertEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, 'layer')
    
    @mock.patch("abjad_to_mei.abjad_voice_to_mei_layer")
    def test_staff_one_voice_mock(self,mock_layer):
        '''
        precondition: abjad Staff containing only one Voice
        postcondition: mei staff Element containing one layer Element
        '''
        voice = Voice("r4 c'4 <c' d'>4")
        abjad_staff = Staff([voice])
        mock_layer.return_value = ETree.Element('layer')
        
        mei_staff = abjad_to_mei.abjad_staff_to_mei_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, 'staff')
        self.assertEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, 'layer')
        
        
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
        
        mei_staff = abjad_to_mei.abjad_staff_to_mei_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, 'staff')
        self.assertEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 2)
        self.assertEqual(mei_staff[0].tag, 'layer')
        self.assertEqual(mei_staff[0].get('n'),'1')
        self.assertEqual(mei_staff[1].tag, 'layer')
        self.assertEqual(mei_staff[1].get('n'),'2')
    
    @mock.patch("abjad_to_mei.abjad_voice_to_mei_layer")
    def test_staff_parallel_mock(self,mock_layer):
        '''
        precondition: abjad Staff containing two or more parallel voices
        postcondition: mei staff Element containing two or more layer Elements
        '''
        voice_one = Voice("r4 c'4 <c' d'>4")
        voice_two = Voice("r4 d'4 <d' e'>4")
        abjad_staff = Staff([voice_one, voice_two])
        abjad_staff.is_simultaneous = True
        mock_layer.side_effect = lambda x: ETree.Element("layer",n='1')
        
        mei_staff = abjad_to_mei.abjad_staff_to_mei_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, 'staff')
        self.assertEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 2)
        self.assertEqual(mei_staff[0].tag, 'layer')
        self.assertEqual(mei_staff[0].get('n'),'1')
        self.assertEqual(mei_staff[1].tag, 'layer')
        self.assertEqual(mei_staff[1].get('n'),'2')

    # staff with consecutive voices
    def test_staff_consecutive(self):
        '''
        precondition: abjad Staff containing two or more consecutive Voices
        postcondition: mei staff Element containing one layer Element
        '''
        voice_one = Voice("r4 c'4 <c' d'>4")
        voice_two = Voice("r4 d'4 <d' e'>4")
        abjad_staff = Staff([voice_one, voice_two])
        
        mei_staff = abjad_to_mei.abjad_staff_to_mei_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, 'staff')
        self.assertEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, 'layer')
        self.assertEqual(mei_staff[0].get('n'),'1')
    
    @mock.patch("abjad_to_mei.abjad_voice_to_mei_layer")
    def test_staff_consecutive_mock(self,mock_layer):
        '''
        precondition: abjad Staff containing two or more consecutive Voices
        postcondition: mei staff Element containing one layer Element
        '''
        voice_one = Voice("r4 c'4 <c' d'>4")
        voice_two = Voice("r4 d'4 <d' e'>4")
        abjad_staff = Staff([voice_one, voice_two])
        mock_layer.return_value = ETree.Element("layer",n='1')
        
        mei_staff = abjad_to_mei.abjad_staff_to_mei_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, 'staff')
        self.assertEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, 'layer')
        self.assertEqual(mei_staff[0].get('n'),'1')
    
    # staff with leaves and no voice(s)
    def test_staff_leaves(self):
        '''
        precondition: abjad Staff containing leaves and no Voices
        postcondition: mei layer Element containing children leaf Elements
        '''
        abjad_staff = Staff("r4 c'4 <c' d'>4")
        
        mei_staff = abjad_to_mei.abjad_staff_to_mei_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, 'staff')
        self.assertEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, 'layer')
        self.assertEqual(mei_staff[0].get('n'),'1')
    
    @mock.patch("abjad_to_mei.abjad_voice_to_mei_layer")
    def test_staff_leaves_mock(self, mock_layer):
        '''
        precondition: abjad Staff containing leaves and no Voices
        postcondition: mei layer Element containing children leaf Elements
        '''
        abjad_staff = Staff("r4 c'4 <c' d'>4")
        mock_layer.return_value = ETree.Element("layer",n='1')
        
        mei_staff = abjad_to_mei.abjad_staff_to_mei_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, 'staff')
        self.assertEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, 'layer')
        self.assertEqual(mei_staff[0].get('n'),'1')
    
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
        
        mei_staff = abjad_to_mei.abjad_staff_to_mei_staff(abjad_staff)
        
        self.assertEqual(mei_staff.tag, 'staff')
        self.assertEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, 'layer')
        self.assertEqual(mei_staff[0].get('n'),'1')
        self.assertEqual(len(mei_staff[0]), 8)
    
    @mock.patch("abjad_to_mei.abjad_voice_to_mei_layer")
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
        dummy = ETree.Element("layer",n='1')
        for _ in range(8):
            ETree.SubElement(dummy, "note")
        mock_layer.return_value = dummy
        
        mei_staff = abjad_to_mei.abjad_staff_to_mei_staff(abjad_staff)
        
        self.assertEqual(1, mock_layer.call_count)
        self.assertEqual(mei_staff.tag, 'staff')
        self.assertEqual(mei_staff.attrib, {'n': '1'})
        self.assertEqual(len(mei_staff), 1)
        self.assertEqual(mei_staff[0].tag, 'layer')
        self.assertEqual(mei_staff[0].get('n'),'1')
        self.assertEqual(len(mei_staff[0]), 8)
    
    def test_section_empty(self):
        '''
        precondition: empty abjad Score
        postcondition: empty mei section Element
        '''
        abjad_score = Score()
        mei_section = abjad_to_mei.abjad_score_to_mei_section(abjad_score)
        self.assertEqual(mei_section.tag, 'section')
        self.assertEqual(mei_section.get('n'), '1')
        self.assertEqual(len(mei_section), 0)
        
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
        
        mei_section = abjad_to_mei.abjad_score_to_mei_section(abjad_score)
        
        self.assertEqual(mei_section.tag, 'section')
        self.assertEqual(len(mei_section), 5)
        self.assertEqual(len(mei_section[0]), 3)
        self.assertEqual(mei_section[0].tag, 'scoreDef')
        self.assertEqual(mei_section[0][0].tag, 'staffDef')
        self.assertEqual(mei_section[0][0].get('lines'), '5')
        self.assertEqual(mei_section[0][0].get('n'), '1')
        self.assertEqual(mei_section[0][1].tag, 'staffGrp')
        self.assertEqual(mei_section[0][1][0].tag, 'staffDef')
        self.assertEqual(mei_section[0][1][0].get('lines'), '5')
        self.assertEqual(mei_section[0][1][0].get('n'), '2')
        self.assertEqual(mei_section[0][1][1].tag, 'staffDef')
        self.assertEqual(mei_section[0][1][1].get('n'), '3')
        self.assertEqual(mei_section[0][1][1].get('lines'), '5')
        self.assertEqual(mei_section[0][2].tag, 'staffDef')
        self.assertEqual(mei_section[0][2].get('n'), '4')
        self.assertEqual(mei_section[0][2].get('lines'), '5')
        for x in range(1,5):
            self.assertEqual(mei_section[x].tag, 'staff')
            self.assertEqual(mei_section[x].get('n'), str(x))
    
    @mock.patch("abjad_to_mei.abjad_staff_to_mei_staff")
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
        mock_section.side_effect = lambda x: ETree.Element('staff',n='1')
        
        mei_section = abjad_to_mei.abjad_score_to_mei_section(abjad_score)
        
        self.assertEqual(mei_section.tag, 'section')
        self.assertEqual(len(mei_section), 5)
        self.assertEqual(len(mei_section[0]), 3)
        self.assertEqual(mei_section[0].tag, 'scoreDef')
        self.assertEqual(mei_section[0][0].tag, 'staffDef')
        self.assertEqual(mei_section[0][0].get('lines'), '5')
        self.assertEqual(mei_section[0][0].get('n'), '1')
        self.assertEqual(mei_section[0][1].tag, 'staffGrp')
        self.assertEqual(mei_section[0][1][0].tag, 'staffDef')
        self.assertEqual(mei_section[0][1][0].get('lines'), '5')
        self.assertEqual(mei_section[0][1][0].get('n'), '2')
        self.assertEqual(mei_section[0][1][1].tag, 'staffDef')
        self.assertEqual(mei_section[0][1][1].get('n'), '3')
        self.assertEqual(mei_section[0][1][1].get('lines'), '5')
        self.assertEqual(mei_section[0][2].tag, 'staffDef')
        self.assertEqual(mei_section[0][2].get('n'), '4')
        self.assertEqual(mei_section[0][2].get('lines'), '5')
        for x in range(1,5):
            self.assertEqual(mei_section[x].tag, 'staff')
            self.assertEqual(mei_section[x].get('n'), str(x))
        