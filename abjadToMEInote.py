# -*- encoding: utf-8 -*-
#Jeff Treviño, 6/8/15
#given an Abjad note as input, outputs an appropriate MEI Element Tree.

from abjad.tools.scoretools.Note import Note
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

r'''Abjad to MEI note conversion.

    ..  container:: example
    
        **Example 1.** Initializes from Abjad note:

        ::

            >>> note = Note("cqs''?8.")
            >>> out = abjadNoteToMEITree(note)
        
        ..  doctest::

            >>> >>> ET.tostring(out.getroot())
            <note dots="1" dur="8" octave="5" pname="c"><accid accid="sd" func="cautionary" /></note>

    '''
    
def convertAccidentalAbjadToMEI(abjadAccidentalString):
    #Helper that converts an Abjad accidental string to an MEI accidental string.
    accidentalDictionary = {'':'n','f':'f','s':'s','ff':'ff','ss':'x','tqs':'su','qs':'sd','tqf':'fd','qf':'fu'}
    return accidentalDictionary[abjadAccidentalString]

def getNumericDurationStringFromLilypondDurationString(lilypondDurationString):
    #Some durations are one number, but others are two numbers.
    numbers = [x for x in lilypondDurationString if x.isalnum()]
    out = ''
    for x in numbers:
        out += x
    return out

def abjadNoteToMEITree(note):
        assert isinstance(note,Note)
        dots = note.written_duration.dot_count
        duration = getNumericDurationStringFromLilypondDurationString(note.written_duration.lilypond_duration_string)
        octave = note.written_pitch.octave.octave_number
        pitchname = note.written_pitch.pitch_class_name[0]
        accidental = convertAccidentalAbjadToMEI(note.written_pitch.accidental.abbreviation)
        is_cautionary = note.note_head.is_cautionary
        if is_cautionary:
            root = ET.Element("note",dots=str(dots), dur=str(duration), octave=str(octave), pname=pitchname)
            ET.SubElement(root,"accid",accid=accidental,func="cautionary")
        else:
            root = ET.Element("note",dots=str(dots), dur=str(duration), octave=str(octave), pname=pitchname, accid=accidental)
        return ET.ElementTree(root)