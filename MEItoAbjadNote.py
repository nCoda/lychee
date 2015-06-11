# -*- encoding: utf-8 -*-
#Jeff Treviño, 6/8/15
#given an MEI string as an input, outputs an Abjad note.

from abjad.tools.scoretools.Note import Note
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

r'''MEI to Abjad note conversion.

    ..  container:: example
    
        **Example 1.** Initializes from MEI Element Tree:

        ::

            >>> root = ET.Element("note",dots="1",dur="4",oct="4",pname="c")
            >>> ET.SubElement(root,"accid",accid="sd",func="cautionary")
            >>> tree = ET.ElementTree(root)
            >>> note = MEITreeToAbjadNote(tree)
        
        ..  doctest::

            >>> note
            Note("cqs'4.")

    '''

def convertAccidentalMEItoAbjad(MEIaccidentalString):
    #Helper that converts an MEI accidental string to an Abjad accidental string.
    accidentalDictionary = {'n':'','f':'f','s':'s','ff':'ff','x':'ss','su':'tqs','sd':'qs','fd':'tqf','fu':'qf'}
    return accidentalDictionary[MEIaccidentalString]

def octaveIntegerToString(octaveInteger):
    if octaveInteger == 3:
        return ''
    elif octaveInteger > 3:
        return "'"*(octaveInteger-3)
    else:
        return ","*(3-octaveInteger)

def MEITreeToAbjadNote(tree):
    assert isinstance(tree,ET.ElementTree)
    root = tree.getroot()
    theString = ''
    theString += root.attrib['pname']
    if len(root) == 1:
        theString += convertAccidentalMEItoAbjad(root[0].attrib['accid'])
        theString += octaveIntegerToString(int(root.attrib['oct']))
        theString += "?"
    else:
        theString += convertAccidentalMEItoAbjad(root.attrib['accid'])
        theString += octaveIntegerToString(int(root.attrib['oct']))
    theString += str(root.attrib['dur'])
    for x in range(int(root.attrib['dots'])):
        theString += '.'
    abjadNote =  Note(theString)
    return abjadNote