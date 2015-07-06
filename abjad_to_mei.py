#Jeff Trevino, 6/8/15
#given an Abjad object as input, outputs an appropriate mei Element.
from abjad.tools.scoretools.Note import Note
from abjad.tools.scoretools.Rest import Rest
from abjad.tools.scoretools.Chord import Chord
from abjad.tools.scoretools.NoteHead import NoteHead
from abjad.tools.scoretools.Voice import Voice
from abjad.tools.scoretools.Staff import Staff
from abjad.tools.topleveltools.mutate import mutate

from lxml import etree as ETree

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
    accidental_dictionary = {'': '', 'f': 'f', 's': 's', 'ff': 'ff', 'ss': 'x', 
                            'tqs': 'su', 'qs': 'sd', 'tqf': 'fd', 'qf': 'fu'}
    return accidental_dictionary[abjad_accidental_string]


def abjad_note_to_mei_note(abjad_note):
        if hasattr(abjad_note,'written_duration'):
            dots = abjad_note.written_duration.dot_count
            duration = abjad_note.written_duration.lilypond_duration_string
            if dots:
                duration = duration[:duration.find('.')]
        else:
            dots = None
            duration = None
        octave = abjad_note.written_pitch.octave.octave_number
        pitchname = abjad_note.written_pitch.pitch_class_name[0]
        accidental = convert_accidental_abjad_to_mei(abjad_note.written_pitch.accidental.abbreviation)
        if hasattr(abjad_note, 'is_cautionary'):
            is_cautionary = abjad_note.is_cautionary
        else:
            is_cautionary = abjad_note.note_head.is_cautionary
        if hasattr(abjad_note, 'is_forced'):
            is_forced = abjad_note.is_forced
        else:
            is_forced = abjad_note.note_head.is_forced
        dictionary = {'octave': str(octave), 
                        'pname': pitchname}
        mei_note = ETree.Element("note", dictionary)
        if duration:
            mei_note.set('dur',str(duration))
        if dots:
            mei_note.set('dots',str(dots))
        if accidental:
            if is_cautionary:
                ETree.SubElement(mei_note,"accid",accid=accidental,func="cautionary")
            else:
                mei_note.set('accid.ges', accidental)
                if is_forced:
                    mei_note.set('accid', accidental)
        else:
            if is_cautionary:
                ETree.SubElement(mei_note,"accid",accid='n',func="cautionary")
            if is_forced:
                mei_note.set('accid.ges', 'n')
                mei_note.set('accid', 'n')
        return mei_note

def abjad_rest_to_mei_rest(abjad_rest):
    duration = abjad_rest.written_duration.lilypond_duration_string
    dots = abjad_rest.written_duration.dot_count
    mei_rest = ETree.Element('rest')
    if dots:
        dot_index = duration.find('.')
        dur_number_string = duration[:dot_index]
        mei_rest.set('dots',str(dots))
    else:
        dur_number_string = duration
    mei_rest.set('dur',dur_number_string)
    return mei_rest


def abjad_chord_to_mei_chord(abjad_chord):
    mei_chord = ETree.Element("chord")
    dots = abjad_chord.written_duration.dot_count
    dur_string = abjad_chord.written_duration.lilypond_duration_string
    if dots:
        mei_chord.set('dots',str(abjad_chord.written_duration.dot_count))
        dur_string = dur_string[:dur_string.find('.')]
    mei_chord.set('dur',dur_string)
    for head in abjad_chord.note_heads:
        mei_note = abjad_note_to_mei_note(head)
        mei_chord.append(mei_note)
    return mei_chord

def abjad_leaf_to_mei_element(abjad_object):
    if isinstance(abjad_object, Rest):
        return abjad_rest_to_mei_rest(abjad_object)
    elif isinstance(abjad_object, (Note,NoteHead)):
        return abjad_note_to_mei_note(abjad_object)
    elif isinstance(abjad_object, Chord):
        return abjad_chord_to_mei_chord(abjad_object)

def abjad_voice_to_mei_layer(abjad_voice):
    mei_layer = ETree.Element('layer',n="1")
    for child in abjad_voice:
        mei_layer.append(abjad_leaf_to_mei_element(child))
    return mei_layer

def abjad_staff_to_mei_staff(abjad_staff):
    mei_staff = ETree.Element('staff',n='1')
    if len(abjad_staff) != 0:
        if abjad_staff.is_simultaneous:
            for x,voice in enumerate(abjad_staff):
                mei_layer = abjad_voice_to_mei_layer(voice)
                mei_layer.set('n',str(x+1))
                mei_staff.append(mei_layer)
        else:
            out_voice = Voice()
            for component in abjad_staff:
                if isinstance(component, Voice):
                    out_voice.extend([mutate(x).copy() for x in component])
                else:
                    out_voice.append(mutate(component).copy())
            mei_layer = abjad_voice_to_mei_layer(out_voice)
        mei_staff.append(mei_layer)
    return mei_staff