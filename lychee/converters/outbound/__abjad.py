#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/lmei_to_abjad.py
# Purpose:                Converts an lmei document to an abjad document.
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
'''
Convert a Lychee-MEI document to an Abjad document.

.. warning::
    This module is intended for internal *Lychee* use only, so the API may change without notice.
    If you wish to use this module outside *Lychee*, please contact us to discuss the best way.

.. tip::
    We recommend that you use the converters indirectly.
    Refer to :ref:`how-to-use-converters` for more information.

.. note:: This is an outbound converter that does not emit signals directly. Refer to the
    :mod:`lychee.signals.outbound` module for more information.
'''

import six
from lxml import etree as etree

from abjad.tools.scoretools.Note import Note
from abjad.tools.scoretools.Rest import Rest
from abjad.tools.scoretools.Chord import Chord
from abjad.tools.scoretools.Skip import Skip
from abjad.tools.scoretools.NoteHead import NoteHead
from abjad.tools.scoretools.FixedDurationTuplet import FixedDurationTuplet
from abjad.tools.scoretools.Tuplet import Tuplet
from abjad.tools.durationtools.Multiplier import Multiplier
from abjad.tools.durationtools.Duration import Duration
from abjad.tools.scoretools.Voice import Voice
from abjad.tools.scoretools.Staff import Staff
from abjad.tools.scoretools.Score import Score
from abjad.tools.scoretools.StaffGroup import StaffGroup
from abjad.tools.scoretools.NoteHead import NoteHead
from abjad.tools.durationtools.Duration import Duration
from abjad.tools.topleveltools.inspect_ import inspect_
from abjad.tools.topleveltools.attach import attach

from lychee import exceptions
from lychee.namespaces import mei, xml


# translatable strings
# errors
_UNSUPPORTED_ELEMENT = 'Cannot convert <{tagname}> elements to Abjad at this time'


def convert(document, **kwargs):
    '''
    Convert an MEI document into an Abjad document.

    :param document: The MEI document.
    :type document: :class:`lxml.etree.ElementTree.Element` or :class:`lxml.etree.ElementTree.ElementTree`
    :returns: The corresponding MEI document.
    :rtype: object
    :raises: :exc:`lychee.exceptions.OutboundConversionError` when there is a forseeable error.
    '''
    tag_to_func = {
        # alphabetical by MEI tag name
        mei.CHORD: element_to_leaf,
        mei.LAYER: layer_to_voice,
        mei.NOTE: element_to_leaf,
        mei.REST: element_to_leaf,
        mei.SECTION: section_to_score,
        mei.SPACE: element_to_leaf,
        mei.STAFF: staff_to_staff,
        mei.TUPLET_SPAN: tupletspan_to_tuplet,
    }
    tag = document.tag

    if tag in tag_to_func:
        return tag_to_func[tag](document)
    else:
        raise exceptions.OutboundConversionError(_UNSUPPORTED_ELEMENT.format(tagname=tag))


def convert_accidental(mei_accidental_string):
    '''
    Convert an MEI accidental string into an Abjad accidental string.

    :param mei_accidental_string: the MEI accidental string to convert.
    :type mei_accidental_string: string
    :returns: the corresponding Abjad accidental string.
    :rtype: string
    '''
    # helper that converts an mei accidental string to an Abjad accidental string
    accidental_dictionary = {'f': 'f', 's': 's', 'ff': 'ff', 'x': 'ss', 'su': 'tqs',
                            'sd': 'qs', 'fd': 'tqf', 'fu': 'qf'}
    return accidental_dictionary[mei_accidental_string]


def octave_integer_to_string(octave_integer):
    '''
    Convert an octave integer to the corresponding Lilypond tick string.
    See the Lilypond docs for explanation octave representation via apostrophes and commas.

    :param octave_integer: the octave integer to convert.
    :type octave_integer: integer
    :returns: the corresponding Lilypond tick string (either apostrophes, empty, or commas).
    :rtype: string
    '''
    if octave_integer == 3:
        return ''
    elif octave_integer > 3:
        return "'" * (octave_integer - 3)
    else:
        return "," * (3 - octave_integer)


def append_accidental(mei_note):  # TODO: this function is untested
    '''
    Create an MEI note's corresponding Lilypond accidental string.

    :param mei_note: the MEI note to interrogate for accidental information.
    :type mei_note: :class:`lxml.etree.ElementTree.Element`
    :returns: the corresponding Lilypond accidental string.
    :rtype: string
    '''
    # append accidental string, if one should be appended
    accid_element = mei_note.findall('./{0}'.format(mei.ACCID))
    if len(accid_element):
    # if cautionary accidental
        accid = accid_element[0].get('accid')
        if accid != 'n':
        # that isn't a natural
            return convert_accidental(accid)
    else:
    # if normal accidental
        accid = mei_note.get('accid.ges')
        if accid:
            if accid != 'n':
                return convert_accidental(accid)
    return ''


def make_abjad_note_from_string(the_string,mei_note):
    '''
    Append duration informtion from an MEI note to a Lilypond pitch-octave string to create an Abjad Note.

    :param the_string: the Lilypond pitch-octave string to append duration information to.
    :type the_string: string
    :param mei_note: the MEI note to query for duration information.
    :type mei_note: :class:`lxml.etree.ElementTree.Element`
    :returns: an Abjad Note.
    :rtype: :class:`abjad.tools.scoretools.Note.Note`
    '''
     #append the duration
    the_string += str(mei_note.get('dur'))
    if mei_note.get('dots'):
        for x in range(int(mei_note.get('dots'))):
            the_string += '.'
    # and create a note
    return Note(the_string)


def set_forced(abjad_note,mei_note):
    '''
    Set an Abjad Note's forced accidental attribute to true if the MEI note has an 'accid' attribute; returns the Note.

    :param abjad_note: the Abjad Note to consider setting.
    :type abjad_note: :class:`abjad.tools.scoretools.Note.Note`
    :param mei_note: the MEI note to interrogate for an 'accid' attribute.
    :type mei_note: :class:`lxml.etree.ElementTree.Element`
    :returns: the modified Abjad Note.
    :rtype: :class:`abjad.tools.scoreetools.Note.Note`
    '''

    if mei_note.get('accid'):
        if hasattr(abjad_note,'is_forced'):
            abjad_note.is_forced = True
        else:
            abjad_note.note_head.is_forced = True
    return abjad_note


def set_cautionary(abjad_note, mei_note):
    '''
    Set an Abjad Note's cautionary accidental attribute to true if the MEI note parents a child, assumed to be an accidental Element; returns the Note.

    :param abjad_note: the Abjad Note to consider setting.
    :type abjad_note: :class:`abjad.tools.scoretools.Note.Note`
    :param mei_note: the MEI note to interrogate for a child.
    :type mei_note: :class:`lxml.etree.ElementTree.Element`
    :returns: the modified Abjad Note.
    :rtype: :class:`abjad.tools.scoretools.Note.Note`
    '''
    if len(mei_note):
        if hasattr(abjad_note, 'is_cautionary'):
            abjad_note.is_cautionary = True
        else:
            abjad_note.note_head.is_cautionary = True
    return abjad_note


def note_to_note(mei_note):
    '''
    Convert an MEI note Element into an Abjad Note.

    :param mei_note: the MEI note Element to convert.
    :type mei_note: :class:`lxml.etree.ElementTree.Element`
    :returns: the corresponding Abjad Note.
    :rtype: :class:`abjad.tools.scoretools.Note.Note`
    '''
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
    output = set_forced(output, mei_note)
    # set cautionary
    output = set_cautionary(output, mei_note)
    return output


def rest_to_rest(mei_rest):
    '''
    Convert an MEI rest Element into an Abjad Rest.

    :param mei_rest: the MEI rest Element to convert.
    :type mei_rest: :class:`lxml.etree.ElementTree.Element`
    :returns: the corresponding Abjad Rest.
    :rtype: :class:`abjad.tools.scoretools.Rest.Rest`
    '''
    the_string = "r"
    the_string += mei_rest.get('dur')
    if mei_rest.get('dots'):
        for x in range(int(mei_rest.get('dots'))):
            the_string += '.'
    abjad_rest = Rest(the_string)
    return abjad_rest


def space_to_skip(mei_space):
    '''
    Convert an MEI space Element into an Abjad Skip.

    :param mei_space: the MEI space Element to convert.
    :type mei_space: :class:`lxml.etree.ElementTree.Element`
    :returns: the corresponding Abjad Skip.
    :rtype: :class:`abjad.tools.scoretools.Skip.Skip`
    '''
    the_string = "r"
    the_string += mei_space.get('dur')
    if mei_space.get('dots'):
        for x in range(int(mei_space.get('dots'))):
            the_string += '.'
    abjad_skip = Skip(the_string)
    return abjad_skip


def chord_to_chord(mei_chord):
    '''
    Convert an MEI chord Element into an Abjad Chord.

    :param mei_chord: the MEI chord Element to convert.
    :type mei_chord: :class:`lxml.etree.ElementTree.Element`
    :returns: the corresponding Abjad Chord.
    :rtype: :class:`abjad.tools.scoretools.Chord.Chord`
    '''
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
        noteheads.append(note_to_note(child))
    abjad_chord = Chord(noteheads,abjad_duration)
    return abjad_chord


def tupletspan_element_to_empty_tuplet(mei_tupletspan):
    '''
    Convert an MEI tupletspan Element into an empty Abjad Tuplet or FixedDurationTuplet.
    An MEI tupletspan with 'num' and 'numBase' attributes but no duration yields a Tuplet object.
    A durated MEI tupletspan without 'num' and 'numBase' attributes yields a FixedDurationTuplet object.

    :param mei_tupletspan: the MEI tupletspan Element to convert.
    :type mei_tupletspan: :class:`lxml.etree.ElementTree.Element`
    :returns: the corresponding empty Abjad Tuplet or FixedDurationTuplet.
    :rtype: :class:`abjad.tools.scoretools.Tuplet.Tuplet` or :class:`abjad.tools.scoretools.FixedDurationTuplet.FixedDurationTuplet`
    '''
    numerator = mei_tupletspan.get('numBase')
    mei_duration = mei_tupletspan.get('dur')
    if numerator and mei_duration is None:
        denominator = mei_tupletspan.get('num')
        multiplier = Multiplier(int(numerator), int(denominator))
        return Tuplet(multiplier, [])
    elif mei_duration != None:
        dots = mei_tupletspan.get('dots')
        dur_string = mei_duration
        if dots != None:
            for x in range(int(dots)):
                dur_string += '.'
        duration = Duration()
        duration = duration.from_lilypond_duration_string(dur_string)
        return_tuplet = FixedDurationTuplet(duration, [])
        return return_tuplet


def setup_outermost_tupletspan(mei_tupletspan):
    '''
    Generate an Abjad FixedDurationTuplet with a duration taken from an MEI tupletspan Element.

    :param mei_tupletspan: the MEI tupletspan Element to query for duration.
    :type mei_tupletspan: :class:`lxml.etree.ElementTree.Element`
    :returns: an Abjad FixedDurationTuplet with mei_tupletspan's duration.
    :rtype: :class:`abjad.tools.scoretools.FixedDurationTuplet.FixedDurationTuplet`
    '''
    mei_duration = mei_tupletspan.get('dur')
    dots = mei_tupletspan.get('dots')
    dur_string = mei_duration
    if dots != None:
        for x in range(int(dots)):
            dur_string += '.'
    duration = Duration()
    duration = duration.from_lilypond_duration_string(dur_string)
    return_tuplet = FixedDurationTuplet(duration, [])
    return return_tuplet


def tupletspan_to_tuplet(mei_tupletspan):
    '''
    Convert an MEI tupletspan to an Abjad Tuplet object.
    A tupletspan Element converts into an empty Tuplet, while a list beginning with a tupletspan element and
    followed by some number of leaf Elements converts into an Abjad Tuplet object full of the following components.

    :param mei_tupletspan: the MEI tupletspan to convert.
    :type mei_tupletspan: list or :class:`lxml.etree.ElementTree.Element`
    :returns: corresponding Abjad Tuplet.
    :rtype: :class:`abjad.tools.scoretools.FixedDurationTuplet.FixedDurationTuplet`
    '''
    if isinstance(mei_tupletspan, list):
        # list beginning with tuplet span and continuing with spanned Elements
        # set up the outermost tuplet and components list
        abjad_outermost_tuplet = setup_outermost_tupletspan(mei_tupletspan[0])
        tuplet_components = []
        outermost_tuplet_members = mei_tupletspan[1:]
        index = 0
        while index < len(outermost_tuplet_members):
            element = outermost_tuplet_members[index]
            #iterate through the list; if you hit a tuplet, recurse
            if element.tag == mei.TUPLET_SPAN:
                plist = element.get('plist').split()
                end_index = index + len(plist) + 1
                recursion_list = outermost_tuplet_members[index:end_index]
                abjad_tuplet = tupletspan_to_tuplet(recursion_list)
                tuplet_components.append(abjad_tuplet)
                index = index + len(plist) + 1
            else:
                #convert the element and add it to the list
                mei_element = element_to_leaf(element)
                tuplet_components.append(mei_element)
                index += 1
        abjad_outermost_tuplet.extend(tuplet_components)
        abjad_outermost_tuplet = abjad_outermost_tuplet.to_fixed_duration_tuplet()
        return abjad_outermost_tuplet
    elif hasattr(mei_tupletspan, 'xpath'):
        return tupletspan_element_to_empty_tuplet(mei_tupletspan)
    else:
        raise AssertionError("Input argument isn't a list or Element.")


def element_to_leaf(mei_element):
    '''
    Convert an MEI leaf Element to the corresponding Abjad leaf.

    :param mei_element: the MEI Element to convert.
    :type mei_element: :class:`lxml.etree.ElementTree.Element`
    :returns: the corresponding Abjad leaf.
    :rtype: :class:`abjad.tools.scoretools.Leaf.Leaf`
    '''
    tag_to_func = {
        mei.REST: rest_to_rest,
        mei.NOTE: note_to_note,
        mei.CHORD: chord_to_chord,
        mei.SPACE: space_to_skip,
    }
    return tag_to_func[mei_element.tag](mei_element)


def layer_to_voice(mei_layer):
    '''
    Convert an MEI layer Element into an Abjad Voice container.

    :param mei_layer: the MEI layer Element to convert.
    :type mei_layer: :class:`lxml.etree.ElementTree.Element`
    :returns: the corresponding Abjad Voice.
    :rtype: :class:`abjad.tools.scoretools.Voice.Voice`
    '''
    abjad_voice = Voice()
    for child in mei_layer:
        if isinstance(child, list):
            abjad_voice.append(tupletspan_to_tuplet(child))
        else:
            abjad_voice.append(element_to_leaf(child))
    return abjad_voice


def staff_to_staff(mei_staff):
    '''
    Convert an MEI staff Element into an Abjad Staff container.

    :param mei_staff: the MEI staff Element to convert.
    :type mei_staff: :class:`lxml.etree.ElementTree.Element`
    :returns: the corresponding Abjad Staff.
    :rtype: :class:`abjad.tools.scoretools.Staff.Staff`
    '''
    abjad_staff = Staff()
    for layer in mei_staff:
        abjad_staff.append(layer_to_voice(layer))
    return abjad_staff


def section_to_score(mei_section):
    '''
    Convert an MEI section Element into an Abjad Score container.

    :param mei_section: the MEI section Element to convert.
    :type mei_section: :class:`lxml.etree.ElementTree.Element`
    :returns: the corresponding Abjad Score container.
    :rtype: :class:`abjad.tools.scoretools.Score.Score`
    '''
    if len(mei_section) == 0:
        return Score()
    abjad_score = Score()
    score_def = mei_section[0]
    mei_global_staff_group = score_def[0]
    staffs = mei_section[1:]
    for element in mei_global_staff_group:
        if element.tag == mei.STAFF_DEF:
            staff_index = int(element.get('n')) - 1
            abjad_staff = staff_to_staff(staffs[staff_index])
            abjad_score.append(abjad_staff)
        elif element.tag == mei.STAFF_GRP:
            abjad_staff_group = StaffGroup()
            for staffDef in element:
                staff_index = int(staffDef.get('n')) - 1
                abjad_staff_group.append(staff_to_staff(staffs[staff_index]))
            abjad_score.append(abjad_staff_group)
    return abjad_score
