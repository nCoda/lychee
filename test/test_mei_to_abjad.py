from lxml import etree as ETree
from abjad.tools.scoretools.Note import Note
from abjad.tools.scoretools.Rest import Rest
from abjad.tools.scoretools.Chord import Chord
from abjad.tools.scoretools.NoteHead import NoteHead
from abjad.tools.scoretools.Voice import Voice
from abjad.tools.scoretools.Staff import Staff
from abjad.tools.scoretools.StaffGroup import StaffGroup
from abjad.tools.scoretools.Score import Score
import mei_to_abjad
import abjad_test_case
import mock
import unittest

try:
    from xml.etree import cElementTree as ETree
except ImportError:
    from xml.etree import ElementTree as ETree

#every method in the class starts with test_ will be run as a test

class TestMeiToAbjadConversions(abjad_test_case.AbjadTestCase):
    
    # note conversion
    
    def test_note_basic(self):
        '''
        precondition: mei note Element with duration, pitch name, and octave string
        postcondition: abjad Note with duration, pitch name, and octave string
        '''        
        dictionary = {'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element('note', dictionary)
        abjad_note = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        self.assertEqual(format(abjad_note), format(Note("c'4")))    
    
    def test_note_dotted(self):
        '''
        precondition: mei note Element with dots attribute
        postcondition: abjad Note with dot
        '''
        dictionary = {'dots': '1', 'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element('note', dictionary)
        abjad_note = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        self.assertEqual(format(abjad_note), format(Note("c'4.")))
    
    def test_note_accid(self):
        '''
        precondition: mei note Element with gestural accidental
        postcondition: abjad Note with accidental, neither forced nor cautionary
        '''
        dictionary = {'accid.ges': 'f', 'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element('note', dictionary)
        abjad_note = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        self.assertEqual(abjad_note, Note("cf'4"))
        
    def test_note_accid_and_cautionary(self):
        '''
        preconditions: mei note Element containing cautionary accidental subelement
        postconditions: abjad Note with cautionary accidental
        '''        
        dictionary = {'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element('note', dictionary)
        ETree.SubElement(mei_note, 'accid', {'accid': 'f', 'func': 'cautionary'}) 
        abjad_note = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        self.assertEqual(abjad_note, Note("cf'?4"))
    
    def test_note_accid_and_forced(self):
        '''
        preconditions: mei note Element with both written and gestural accidentals
        postconditions: abjad Note with forced accidental
        '''
        dictionary = {'accid.ges': 'f', 'accid': 'f', 'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element('note', dictionary)
        abjad_note = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        self.assertEqual(abjad_note, Note("cf'!4"))
        
    def test_note_cautionary(self):
        '''
        precondition: mei note Element containing cautionary accidental subelement set to natural
        postcondition: abjad Note with no accidental and cautionary natural
        '''
        dictionary = {'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element('note', dictionary)
        ETree.SubElement(mei_note, 'accid', {'accid': 'n', 'func': 'cautionary'}) 
        abjad_note = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        self.assertEqual(abjad_note, Note("c'?4"))
        
    def test_note_forced(self):
        '''
        precondition: mei note Element with both accid.ges and accid attributes set
        postcondition: abjad Note with no accidental and forced natural
        '''
        dictionary = {'accid.ges': 'n', 'accid': 'n', 'dur': '4', 'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element('note',dictionary)
        abjad_note = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        self.assertEqual(abjad_note, Note("c'!4"))
    
    #forced, cautionary, accidental, blank notehead tests
    
    def test_notehead_basic(self):
        '''
        precondition: mei note Element with pitch name, and octave string
        postcondition: abjad NoteHead with duration, pitch name, and octave string
        '''        
        dictionary = {'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element('note', dictionary)
        abjad_notehead = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        self.assertEqual(abjad_notehead, NoteHead("c'"))
    
    #notehead: basic, basic cautionary, basic forced, accidental, acc cautionary, acc forced.
    
    def test_notehead_basic_cautionary(self):
        '''
        precondition: mei note Element with cautionary accidental
        postcondition: Abjad NoteHead with cautionary accidental
        '''
        dictionary = {'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element('note', dictionary)
        ETree.SubElement(mei_note, 'accid', {'accid': 'n', 'func': 'cautionary'})
        abjad_notehead = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        head = NoteHead("c'")
        head.is_cautionary = True
        self.assertEqual(abjad_notehead, head)
    
    def test_notehead_basic_forced(self):
        '''
        precondition: mei note Element with no accidental and both accid.ges and accid attributes
        postcondition: Abjad NoteHead with forced natural
        '''
        dictionary = {'pname': 'c', 'octave': '4', 'accid.ges': 'n', 'accid': 'n'}
        mei_note = ETree.Element('note', dictionary)
        abjad_notehead = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        head = NoteHead("c'")
        head.is_forced = True
        self.assertEqual(abjad_notehead, head)
    
    def test_notehead_accid(self):
        '''
        precondition: mei note Element with accidental and no duration.
        postcondition: Abjad NoteHead with accidental.
        '''
        dictionary = {'pname': 'c', 'octave': '4', 'accid.ges': 'f'}
        mei_note = ETree.Element('note', dictionary)
        abjad_notehead = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        self.assertEqual(abjad_notehead, NoteHead("cf'"))
    
    def test_notehead_accid_cautionary(self):
        '''
        precondition: mei note Element with cautionary accidental
        postcondition: abjad NoteHead with cautionary accidental
        '''
        dictionary = {'pname': 'c', 'octave': '4'}
        mei_note = ETree.Element('note', dictionary)
        ETree.SubElement(mei_note, 'accid', {'accid': 'f', 'func': 'cautionary'})
        abjad_notehead = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        head = NoteHead("cf'")
        head.is_cautionary = True
        self.assertEqual(abjad_notehead, head)
    
    def test_notehead_accid_forced(self):
        '''
        precondition: mei note Element with forced accidental
        postcondition: abjad NoteHead with forced accidental
        '''
        dictionary = {'pname': 'c', 'octave': '4', 'accid.ges': 'f', 'accid': 'f'}
        mei_note = ETree.Element('note', dictionary)
        abjad_notehead = mei_to_abjad.mei_note_to_abjad_note(mei_note)
        head = NoteHead("cf'")
        head.is_forced = True
        self.assertEqual(abjad_notehead, head)
        
    def test_rest(self):
        '''
        precondition: mei rest Element with no dots.
        postcondition: abjad Rest with no dots.
        '''
        mei_rest = ETree.Element('rest',dur='32')
        abjad_rest = mei_to_abjad.mei_rest_to_abjad_rest(mei_rest)
        self.assertEqual(abjad_rest, Rest("r32"))
        
    def test_rest_dotted(self):
        '''
        precondition: dotted mei rest Element.
        postcondition: dotted abjad Rest.
        '''
        mei_rest = ETree.Element('rest',dur='32',dots='2')
        abjad_rest = mei_to_abjad.mei_rest_to_abjad_rest(mei_rest)
        self.assertEqual(abjad_rest, Rest("r32.."))
    
    def test_chord_empty(self):
        '''
        precondition: empty mei chord Element with undotted duration
        postcondition: empty abjad Chord with undotted duration
        '''
        mei_chord = ETree.Element('chord',dur='4')
        abjad_chord = mei_to_abjad.mei_chord_to_abjad_chord(mei_chord)
        self.assertEqual(abjad_chord, Chord([],(1,4)))
        
    def test_chord_empty_dotted(self):
        '''
        precondition: empty mei chord Element with dotted duration
        postcondition: empty abjad Chord with dotted duration
        '''
        mei_chord = ETree.Element('chord',dur='4',dots='1')
        abjad_chord = mei_to_abjad.mei_chord_to_abjad_chord(mei_chord)
        self.assertEqual(abjad_chord, Chord([],(3,8)))
        
    def test_chord_full(self):
        '''
        precondition: mei chord Element with undotted duration and two child note Elements
        postcondition: abjad Chord with undotted duration and two child note Elements
        '''
        mei_chord = ETree.Element('chord',dur='4')
        ETree.SubElement(mei_chord, 'note',pname='c',octave='4')
        ETree.SubElement(mei_chord, 'note',pname='d',octave='4')
        abjad_chord = mei_to_abjad.mei_chord_to_abjad_chord(mei_chord)
        self.assertEqual(abjad_chord, Chord("<c' d'>4"))
        
    def test_chord_full_dotted(self):
        '''
        precondition: mei chord Element with dotted duration and two child note Elements
        postcondition: abjad Chord with dotted duration and two child note Elements
        '''
        mei_chord = ETree.Element('chord',dur='4',dots='1')
        ETree.SubElement(mei_chord, 'note',pname='c',octave='4')
        ETree.SubElement(mei_chord, 'note',pname='d',octave='4')
        abjad_chord = mei_to_abjad.mei_chord_to_abjad_chord(mei_chord)
        self.assertEqual(abjad_chord, Chord("<c' d'>4."))
    
    def test_layer_to_voice_empty(self):
        '''
        precondition: empty mei layer Element
        postcondition: empty abjad Voice
        '''
        mei_layer = ETree.Element('layer',n='1')
        abjad_voice = mei_to_abjad.mei_layer_to_abjad_voice(mei_layer)
        self.assertEqual(abjad_voice, Voice() )
        
    def test_layer_to_voice_full(self):
        '''
        precondition: mei layer Element containing children
        postcondition: abjad Voice containing children
        '''
        mei_layer = ETree.Element('layer',n='1')
        ETree.SubElement(mei_layer,'rest',dur='4')
        ETree.SubElement(mei_layer,'note',pname='c',octave='4',dur='4')
        chord = ETree.SubElement(mei_layer,'chord',dur='4')
        ETree.SubElement(chord,'note',pname='c',octave='4')
        ETree.SubElement(chord,'note',pname='d',octave='4')
        
        abjad_voice = mei_to_abjad.mei_layer_to_abjad_voice(mei_layer)
        
        self.assertEqual(abjad_voice, Voice("r4 c'4 <c' d'>4"))
    

    @mock.patch("mei_to_abjad.mei_chord_to_abjad_chord")
    @mock.patch("mei_to_abjad.mei_note_to_abjad_note")
    @mock.patch("mei_to_abjad.mei_rest_to_abjad_rest")
    def test_layer_to_voice_full_mock(self, mock_rest, mock_note, mock_chord):
        '''
        precondition: mei layer Element containing children
        postcondition: abjad Voice containing children
        '''
        mei_layer = ETree.Element('layer',n='1')
        ETree.SubElement(mei_layer,'rest',dur='4')
        ETree.SubElement(mei_layer,'note',pname='c',octave='4',dur='4')
        chord = ETree.SubElement(mei_layer,'chord',dur='4')
        ETree.SubElement(chord,'note',pname='c',octave='4')
        ETree.SubElement(chord,'note',pname='d',octave='4')
        mock_rest.return_value = Rest((1,4))
        mock_note.return_value = Note("c'4")
        mock_chord.return_value = Chord("<c' d'>4")
        
        abjad_voice = mei_to_abjad.mei_layer_to_abjad_voice(mei_layer)
        
        self.assertEqual(abjad_voice, Voice("r4 c'4 <c' d'>4"))
    
    def test_staff_empty(self):
        '''
        precondition: empty mei staff Element
        postcondition: empty abjad Staff
        '''
        mei_staff = ETree.Element('staff',n='1')
        abjad_staff = mei_to_abjad.mei_staff_to_abjad_staff(mei_staff)
        self.assertEqual(abjad_staff, Staff())
        
    
    def test_staff_one_voice(self):
        '''
        precondition: mei staff Element containing one layer Element
        postcondition: abjad Staff containing one Voice
        '''
        mei_staff = ETree.Element('staff',n='1')
        mei_layer = ETree.SubElement(mei_staff,'layer',n='1')
        ETree.SubElement(mei_layer, 'rest', dur='4')
        ETree.SubElement(mei_layer, 'note', pname='c', dur='4', octave='4')
        
        abjad_staff = mei_to_abjad.mei_staff_to_abjad_staff(mei_staff)
        
        self.assertEqual(abjad_staff, Staff([Voice("r4 c'4")]))
    
    @mock.patch("mei_to_abjad.mei_layer_to_abjad_voice")
    def test_staff_one_voice_mock(self, mock_voice):
        '''
        precondition: mei staff Element containing one layer Element
        postcondition: abjad Staff containing one Voice
        '''
        mei_staff = ETree.Element('staff',n='1')
        mei_layer = ETree.SubElement(mei_staff,'layer',n='1')
        ETree.SubElement(mei_layer, 'rest', dur='4')
        ETree.SubElement(mei_layer, 'note', pname='c', dur='4', octave='4')
        mock_voice.return_value = Voice("r4 c'4")
        
        abjad_staff = mei_to_abjad.mei_staff_to_abjad_staff(mei_staff)
        
        voice = Voice("r4 c'4")
        comparator = Staff([voice])
        self.assertEqual(abjad_staff, comparator)
    
    def test_staff_parallel(self):
        '''
        precondition: mei staff Element containing two layer Elements
        postcondition: abjad Staff containing two Voices
        '''
        mei_staff = ETree.Element('staff',n='1')
        ETree.SubElement(mei_staff,'layer',n='1')
        ETree.SubElement(mei_staff,'layer',n='2')
        
        abjad_staff = mei_to_abjad.mei_staff_to_abjad_staff(mei_staff)

        self.assertEqual(abjad_staff, Staff([Voice(), Voice()]))
    
    @mock.patch("mei_to_abjad.mei_layer_to_abjad_voice")
    def test_staff_parallel_mock(self, mock_voice):
        '''
        precondition: mei staff Element containing two layer Elements
        postcondition: abjad Staff containing two Voices
        '''
        mei_staff = ETree.Element('staff',n='1')
        ETree.SubElement(mei_staff,'layer',n='1')
        ETree.SubElement(mei_staff,'layer',n='2')
        mock_voice.side_effect = lambda x: Voice()
        
        abjad_staff = mei_to_abjad.mei_staff_to_abjad_staff(mei_staff)
        
        self.assertEqual(abjad_staff, Staff([Voice(), Voice()]))

    def test_section_empty(self):
        '''
        precondition: empty mei section Element
        postcondition: empty abjad Score
        '''
        mei_section = ETree.Element('section',n='1')
        abjad_score = mei_to_abjad.mei_section_to_abjad_score(mei_section)
        self.assertEqual(abjad_score, Score())
        
    def test_section_full(self):
        '''
        precondition: mei section Element containing scoreDef element and four staff Elements
        with staff Elements two and three of four grouped
        postcondition: abjad Score containing Staff, StaffGroup containing two Staffs, and Staff
        '''
        mei_section = ETree.Element('section', n='1')
        mei_score_def = ETree.Element('scoreDef', n='1')
        mei_staff_grp = ETree.Element('staffGrp', n='1')
        mei_staffs = []
        mei_staff_defs = []
        for x in range(4):
            mei_staff_defs.append( ETree.Element('staffDef',n=str(x + 1)))
        for x in range(4):
            mei_staffs.append( ETree.Element('staff',n=str(x + 1)))
        mei_section.append(mei_score_def)
        mei_score_def.append(mei_staff_defs[0])
        mei_score_def.append(mei_staff_grp)
        mei_staff_grp.extend(mei_staff_defs[1:3])
        mei_score_def.append(mei_staff_defs[3])
        mei_section.extend(mei_staffs)
        
        abjad_score = mei_to_abjad.mei_section_to_abjad_score(mei_section)
        
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
        
    @mock.patch("mei_to_abjad.mei_staff_to_abjad_staff")
    def test_section_full_mock(self, mock_staff):
        '''
        precondition: mei section Element containing scoreDef element and four staff Elements
        with staff Elements two and three of four grouped
        postcondition: abjad Score containing Staff, StaffGroup containing two Staffs, and Staff
        '''
        mei_section = ETree.Element('section', n='1')
        mei_score_def = ETree.Element('scoreDef', n='1')
        mei_staff_grp = ETree.Element('staffGrp', n='1')
        mei_staffs = []
        mei_staff_defs = []
        for x in range(4):
            mei_staff_defs.append( ETree.Element('staffDef',n=str(x + 1)))
        for x in range(4):
            mei_staffs.append( ETree.Element('staff',n=str(x + 1)))
        mei_section.append(mei_score_def)
        mei_score_def.append(mei_staff_defs[0])
        mei_score_def.append(mei_staff_grp)
        mei_staff_grp.extend(mei_staff_defs[1:3])
        mei_score_def.append(mei_staff_defs[3])
        mei_section.extend(mei_staffs)
        mock_staff.side_effect = lambda x: Staff()
        
        abjad_score = mei_to_abjad.mei_section_to_abjad_score(mei_section)
        
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
        