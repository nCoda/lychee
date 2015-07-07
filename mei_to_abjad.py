# -*- encoding: utf-8 -*-
# Jeff Treviño, 6/8/15
# given an mei string as an input, outputs an abjad note

from abjad.tools.scoretools.Note import Note
from abjad.tools.scoretools.Rest import Rest
from abjad.tools.scoretools.Chord import Chord
from abjad.tools.scoretools.Voice import Voice
from abjad.tools.scoretools.Staff import Staff
from abjad.tools.scoretools.Score import Score
from abjad.tools.scoretools.StaffGroup import StaffGroup
from abjad.tools.scoretools.NoteHead import NoteHead
from abjad.tools.durationtools.Duration import Duration


from lxml import etree as ETree

'''MEI to Abjad note conversion.

    ..  container:: example
    
        **Example 1.** Initializes from mei Element Tree:

        ::

            >>> root = ETree.Element("note",dots="1",dur="4",oct="4",pname="c")
            >>> ETree.SubElement(root,"accid",accid="sd",func="cautionary")
            >>> tree = ETree.ElementTree(root)
            >>> note = meiTreeToAbjadNote(tree)
        
        ..  doctest::

            >>> note
            Note("cqs'4.")

    '''


def convert_accidental_mei_to_abjad(mei_accidental_string):
    # helper that converts an mei accidental string to an Abjad accidental string
    accidental_dictionary = {'f': 'f', 's': 's', 'ff': 'ff', 'x': 'ss', 'su': 'tqs', 
                            'sd': 'qs', 'fd': 'tqf', 'fu': 'qf'}
    return accidental_dictionary[mei_accidental_string]


def octave_integer_to_string(octave_integer):
    if octave_integer == 3:
        return ''
    elif octave_integer > 3:
        return "'" * (octave_integer - 3)
    else:
        return "," * (3 - octave_integer)


def append_accidental(mei_note):
    # append accidental string, if one should be appended
    accid_element = mei_note.findall('./accid')
    if len(accid_element):
    # if cautionary accidental
        accid = accid_element[0].get('accid')
        if accid != 'n':
        # that isn't a natural
            return convert_accidental_mei_to_abjad(accid)
    else:
    # if normal accidental
        accid = mei_note.get('accid.ges')
        if accid:
            if accid != 'n':
                return convert_accidental_mei_to_abjad(accid)
    return ''
        
        
def make_abjad_note_from_string(the_string,mei_note):
     #append the duration
        the_string += str(mei_note.get('dur'))
        if mei_note.get('dots'):
            for x in range(int(mei_note.get('dots'))):
                the_string += '.'
        # and create a note
        return Note(the_string)

def set_forced(output,mei_note):
    if mei_note.get('accid'):
        if hasattr(output,'is_forced'):
            output.is_forced = True
        else:
            output.note_head.is_forced = True

def set_cautionary(output, mei_note):
    accid = mei_note.findall('accid')
    if len(accid):
        if hasattr(output, 'is_cautionary'):
            output.is_cautionary = True
        else:
            output.note_head.is_cautionary = True
        

def mei_note_to_abjad_note(mei_note):
    the_string = ""
    # append pitch name
    the_string += mei_note.get('pname')
    the_string += append_accidental(mei_note)
    # octave tick string
    the_string += octave_integer_to_string(int(mei_note.get('octave')))
    #if the mei note Element has a duration,
    if mei_note.get('dur'):
       output = make_abjad_note_from_string(the_string,mei_note)
    else:
        # otherwise create an abjad NoteHead
        output = NoteHead(the_string)
    # set forced
    set_forced(output,mei_note)
    # set cautionary
    set_cautionary(output, mei_note)
    return output
        

def mei_rest_to_abjad_rest(mei_rest):
    the_string = "r"
    the_string += mei_rest.get('dur')
    if mei_rest.get('dots'):
        for x in range(int(mei_rest.get('dots'))):
            the_string += '.'
    abjad_rest = Rest(the_string)
    return abjad_rest



def mei_chord_to_abjad_chord(mei_chord):
    dots = mei_chord.get('dots')
    dur = mei_chord.get('dur')
    abjad_duration = Duration()
    lily_dur_string = dur
    if dots:
        for x in range(int(dots)):
            lily_dur_string += "."
    abjad_duration = abjad_duration.from_lilypond_duration_string(lily_dur_string)
    noteheads = []
    for child in mei_chord:
        noteheads.append(mei_note_to_abjad_note(child))
    abjad_chord = Chord(noteheads,abjad_duration)
    return abjad_chord

def mei_element_to_abjad_leaf(mei_element):
    if mei_element.tag == 'rest':
        return mei_rest_to_abjad_rest(mei_element)
    elif mei_element.tag == 'note':
        return mei_note_to_abjad_note(mei_element)
    elif mei_element.tag == 'chord':
        return mei_chord_to_abjad_chord(mei_element)

def mei_layer_to_abjad_voice(mei_layer):
    abjad_voice = Voice()
    for child in mei_layer:
        abjad_voice.append(mei_element_to_abjad_leaf(child))
    return abjad_voice

def mei_staff_to_abjad_staff(mei_staff):
    abjad_staff = Staff()
    for layer in mei_staff:
        abjad_staff.append(mei_layer_to_abjad_voice(layer))
    return abjad_staff

def mei_section_to_abjad_score(mei_section):
    if len(mei_section) == 0:
        return Score()
    abjad_score = Score()
    scoreDef = mei_section[0]
    staffs = mei_section[1:]
    for element in scoreDef:
        if element.tag == 'staffDef':
            staff_index = int(element.get('n')) - 1
            abjad_staff = mei_staff_to_abjad_staff(staffs[staff_index])
            abjad_score.append(abjad_staff)
        elif element.tag == 'staffGrp':
            abjad_staff_group = StaffGroup()
            for staffDef in element:
                staff_index = int(staffDef.get('n')) - 1
                abjad_staff_group.append(mei_staff_to_abjad_staff(staffs[staff_index]))
            abjad_score.append(abjad_staff_group)
    return abjad_score
            