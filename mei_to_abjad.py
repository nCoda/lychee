# -*- encoding: utf-8 -*-
# Jeff Treviño, 6/8/15
# given an mei string as an input, outputs an abjad note.

from abjad.tools.scoretools.Note import Note
try:
    from xml.etree import cElementTree as ETree
except ImportError:
    from xml.etree import ElementTree as ETree

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
    # Helper that converts an mei accidental string to an Abjad accidental string.
    accidental_dictionary = {'n': '', 'f': 'f', 's': 's', 'ff': 'ff', 'x': 'ss', 'su': 'tqs', 
                            'sd': 'qs', 'fd': 'tqf', 'fu': 'qf'}
    return accidental_dictionary[mei_accidental_string]


def octave_integer_to_string(octave_integer):
    if octave_integer == 3:
        return ''
    elif octave_integer > 3:
        return "'" * (octave_integer - 3)
    else:
        return "," * (3 - octave_integer)


def mei_to_abjad_note(element):
    the_string = ''
    the_string += element.attrib['pname']
    if len(element) == 1:
        the_string += convert_accidental_mei_to_abjad(element[0].attrib['accid'])
        the_string += octave_integer_to_string(int(element.attrib['oct']))
        the_string += "?"
    else:
        the_string += convert_accidental_mei_to_abjad(element.attrib['accid'])
        the_string += octave_integerToString(int(element.attrib['oct']))
    the_string += str(element.attrib['dur'])
    for x in range(int(element.attrib['dots'])):
        the_string += '.'
    abjad_note =  Note(the_string)
    return abjad_note

element = ETree.Element("note",dots="1",dur="4",oct="4",pname="c")
ETree.SubElement(element,"accid",accid="sd",func="cautionary")
note = mei_to_abjad_note(element)