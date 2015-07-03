#Jeff Trevino, 6/8/15
#given an Abjad note as input, outputs an appropriate mei Element.

from abjad.tools.scoretools.Note import Note
try:
    from xml.etree import cElementTree as ETree
except ImportError:
    from xml.etree import ElementTree as ETree

'''Abjad to mei note conversion.

    ..  container:: example
    
        **Example 1.** Initializes from Abjad note:

        ::

            >>> note = Note("cqs''?8.")
            >>> out = abjadNoteTomeiTree(note)
        
        ..  doctest::

            >>> >>> ET.tostring(out.getroot())
            <note dots="1" dur="8" octave="5" pname="c"><accid accid="sd" func="cautionary" /></note>

'''
    

def convert_accidental_abjad_to_mei(abjad_accidental_string):
    # Helper that converts an Abjad accidental string to an mei accidental string.
    accidental_dictionary = {'': 'n', 'f': 'f', 's': 's', 'ff': 'ff', 'ss': 'x', 
                            'tqs': 'su', 'qs': 'sd', 'tqf': 'fd', 'qf': 'fu'}
    return accidental_dictionary[abjad_accidental_string]


def get_numeric_duration_string(lilypond_duration_string):
    # Retrieves the duration number, as a string, from a lilypond duration string.
    numbers = [x for x in lilypond_duration_string if x.isalnum()]
    out = ''
    for x in numbers:
        out += x
    return out


def abjad_note_to_mei_element(note):
        assert isinstance(note,Note)
        dots = note.written_duration.dot_count
        duration = get_numeric_duration_string(note.written_duration.lilypond_duration_string)
        octave = note.written_pitch.octave.octave_number
        pitchname = note.written_pitch.pitch_class_name[0]
        accidental = convert_accidental_abjad_to_mei(note.written_pitch.accidental.abbreviation)
        is_cautionary = note.note_head.is_cautionary
        if is_cautionary:
            element = ETree.Element("note",dots=str(dots), dur=str(duration), octave=str(octave), pname=pitchname)
            ETree.SubElement(element,"accid",accid=accidental,func="cautionary")
        else:
            element = ETree.Element("note",dots=str(dots), dur=str(duration), octave=str(octave), pname=pitchname, accid=accidental)
        return element

note = Note("ctqs''4.")
element = abjad_note_to_mei_element(note)
ETree.tostring(element)