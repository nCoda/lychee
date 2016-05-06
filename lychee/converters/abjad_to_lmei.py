#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/abjad_to_lmei.py
# Purpose:                Converts an abjad document to an lmei document.
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
import uuid

from lxml import etree as etree
import six
import hashlib
from abjad.tools.indicatortools import Clef
from abjad.tools.scoretools.Note import Note
from abjad.tools.scoretools.Rest import Rest
from abjad.tools.scoretools.Chord import Chord
from abjad.tools.scoretools.Skip import Skip
from abjad.tools.scoretools.Leaf import Leaf
from abjad.tools.scoretools.Measure import Measure
from abjad.tools.scoretools.NoteHead import NoteHead
from abjad.tools.scoretools.Tuplet import Tuplet
from abjad.tools.scoretools.FixedDurationTuplet import FixedDurationTuplet
from abjad.tools.durationtools.Multiplier import Multiplier
from abjad.tools.durationtools.Duration import Duration
from abjad.tools.scoretools.Voice import Voice
from abjad.tools.scoretools.Staff import Staff
from abjad.tools.scoretools.StaffGroup import StaffGroup
from abjad.tools.topleveltools.mutate import mutate
from abjad.tools.topleveltools.inspect_ import inspect_
from abjad.tools.topleveltools.attach import attach

import lychee
from lychee import exceptions
from lychee.signals import inbound
from lychee.namespaces import mei, xml


# translatable strings
# error messages
_NOT_A_LEAF_NODE = 'Object of type {0} is not a leaf node'


def convert(document, **kwargs):
    '''
    Convert an Abjad document into an MEI document.

    :param object document: the Abjad document.
    :returns: The corresponding MEI document.
    :rtype: :class:`lxml.etree.ElementTree.Element` or :class:`lxml.etree.ElementTree.ElementTree`
    '''
    inbound.CONVERSION_STARTED.emit()

    conversion_dict = {
        "<class 'abjad.tools.scoretools.Note.Note'>": note_to_note,
        "<class 'abjad.tools.scoretools.Rest.Rest'>": rest_to_rest,
        "<class 'abjad.tools.scoretools.Skip.Skip'>": skip_to_space,
        "<class 'abjad.tools.scoretools.Chord.Chord'>": chord_to_chord,
        "<class 'abjad.tools.scoretools.Tuplet.Tuplet'>": tuplet_to_tupletspan,
        "<class 'abjad.tools.scoretools.Voice.Voice'>": voice_to_layer,
        "<class 'abjad.tools.scoretools.Staff.Staff'>": staff_to_staff,
        "<class 'abjad.tools.scoretools.Score.Score'>": score_to_section,
    }
    converted = conversion_dict[str(type(document))](document)

    inbound.CONVERSION_FINISH.emit(converted=converted)
    return converted


def convert_accidental(abjad_accidental_string):
    '''
    Convert an abjad accidental string to an mei accidental string.

    :param abjad_accidental_string: the Abjad accidental string.
    :type abjad_accidental_string: string
    :returns: the MEI accidental string.
    :rtype: string
    '''
    accidental_dictionary = {'': '', 'f': 'f', 's': 's', 'ff': 'ff', 'ss': 'x',
                            'tqs': 'su', 'qs': 'sd', 'tqf': 'fd', 'qf': 'fu'}
    return accidental_dictionary[abjad_accidental_string]


def add_xml_ids(abjad_object, mei_element):
    '''
    Attach the same SHA256 hash digest as xml ID to both an abjad object and an mei element.

    :param abjad_object: The abjad object to attach the ID to.
    :type abjad_object: :class:`abjad.tools.abctools.AbjadObject.AbjadObject`
    :param mei_element: The MEI Element to attach the ID to.
    :type mei_element: :class:`lxml.etree.ElementTree.Element`
    '''
    try:
        abjad_str = str(abjad_object)
    except UnderfullContainerError:
        abjad_str = 'underfull'

    parentage = inspect_(abjad_object).get_parentage()
    id_string = '{0}{1}{2}{3}'.format(abjad_str, parentage.score_index, mei_element.tag, mei_element.get('n', ''))
    hasher = hashlib.new('SHA256', six.b(id_string))
    the_xmlid = 'z{0}'.format(hasher.hexdigest())

    attach(the_xmlid, abjad_object)
    mei_element.set(xml.ID, the_xmlid)


def note_to_note(abjad_note):
    '''
    Convert an Abjad Note or NoteHead object to an MEI note Element.

    :param abjad_note: the Abjad Note object to convert.
    :type abjad_note: :class:`abjad.tools.scoretools.Note.Note`
    :returns: The corresponding MEI note Element.
    :rtype: :class:`lxml.etree.ElementTree.Element`
    '''
    #also handles abjad NoteHead objects (which have pitch and octave attrs but no dur)
    #(NoteHeads have the 'written_duration' attribute, Notes don't.)
    if hasattr(abjad_note,'written_duration'):
        dots = abjad_note.written_duration.dot_count
        duration = abjad_note.written_duration.lilypond_duration_string
        if dots:
            duration = duration[:duration.find('.')]
    else:
    #otherwise, assume a Note came in
        dots = None
        duration = None
    octave = abjad_note.written_pitch.octave.octave_number
    pitchname = abjad_note.written_pitch.pitch_class_name[0]
    accidental = convert_accidental(abjad_note.written_pitch.accidental.abbreviation)
    #cautionary accidental handling
    if hasattr(abjad_note, 'is_cautionary'):
        is_cautionary = abjad_note.is_cautionary
    else:
        is_cautionary = abjad_note.note_head.is_cautionary
    #forced accidental handling
    if hasattr(abjad_note, 'is_forced'):
        is_forced = abjad_note.is_forced
    else:
        is_forced = abjad_note.note_head.is_forced
    dictionary = {'oct': str(octave), 'pname': pitchname}
    #make the MEI note according to the information collected above
    mei_note = etree.Element(mei.NOTE, dictionary)
    if duration:
        mei_note.set('dur',str(duration))
    if dots:
        mei_note.set('dots',str(dots))
    if accidental:
        if is_cautionary:
            accid = etree.SubElement(mei_note,mei.ACCID,accid=accidental,func='cautionary')
        else:
            mei_note.set('accid.ges', accidental)
            if is_forced:
                mei_note.set('accid', accidental)
    else:
        if is_cautionary:
            accid = etree.SubElement(mei_note,mei.ACCID,accid='n',func='cautionary')
        if is_forced:
            mei_note.set('accid.ges', 'n')
            mei_note.set('accid', 'n')
    #If the input was a Note, add an xml ID; if it was a NoteHead, don't.
    if not isinstance(abjad_note, NoteHead):
        add_xml_ids(abjad_note, mei_note)
    return mei_note


def rest_to_rest(abjad_rest):
    '''
    Convert an Abjad Rest object to an MEI rest Element.
    Collects info from the abjad object, then generates mei Element.

    :param abjad_rest: The Abjad Rest object to convert.
    :type abjad_rest: :class:`abjad.tools.scoretools.Rest.Rest`
    :returns: The corresponding MEI rest Element.
    :rtype: :class:`lxml.etree.ElementTree.Element`
    '''
    duration = abjad_rest.written_duration.lilypond_duration_string
    dots = abjad_rest.written_duration.dot_count
    mei_rest = etree.Element(mei.REST)
    if dots:
        dot_index = duration.find('.')
        dur_number_string = duration[:dot_index]
        mei_rest.set('dots',str(dots))
    else:
        dur_number_string = duration
    mei_rest.set('dur',dur_number_string)
    add_xml_ids(abjad_rest, mei_rest)
    return mei_rest


def skip_to_space(abjad_skip):
    '''
    Convert an Abjad Skip object to an MEI space Element.

    :param abjad_skip: The Abjad Skip object to convert.
    :type abjad_skip: :class:`abjad.tools.scoretools.Skip.Skip`
    :returns: The corresponding MEI space Element.
    :rtype: :class:`lxml.etree.ElementTree.Element`
    '''
    duration = abjad_skip.written_duration.lilypond_duration_string
    dots = abjad_skip.written_duration.dot_count
    mei_space = etree.Element(mei.SPACE)
    if dots:
        dot_index = duration.find('.')
        dur_number_string = duration[:dot_index]
        mei_space.set('dots',str(dots))
    else:
        dur_number_string = duration
    mei_space.set('dur',dur_number_string)
    add_xml_ids(abjad_skip, mei_space)
    return mei_space


def chord_to_chord(abjad_chord):
    '''
    Convert an Abjad Chord object to an MEI chord Element.

    :param abjad_chord: the Abjad Chord object to convert.
    :type abjad_chord: :class:`abjad.tools.scoretools.Chord.Chord`
    :returns: the corresponding MEI chord Element.
    :rtype: :class:`lxml.etree.ElementTree.Element`
    '''
    mei_chord = etree.Element(mei.CHORD)
    dots = abjad_chord.written_duration.dot_count
    dur_string = abjad_chord.written_duration.lilypond_duration_string
    if dots:
        mei_chord.set('dots',str(abjad_chord.written_duration.dot_count))
        dur_string = dur_string[:dur_string.find('.')]
    mei_chord.set('dur',dur_string)
    for head in abjad_chord.note_heads:
        mei_note = note_to_note(head)
        mei_chord.append(mei_note)
    add_xml_ids(abjad_chord, mei_chord)
    return mei_chord


def empty_tuplet_to_tupletspan_element(abjad_tuplet):
    '''
    Convert an empty Abjad Tuplet or FixedDurationTuplet container to an MEI tupletspan Element.

    :param abjad_tuplet: the empty Abjad Tuplet container to convert.
    :type abjad_tuplet: :class:`abjad.tools.scoretools.Tuplet.Tuplet` or :class:`abjad.tools.scoretools.FixedDurationTuplet.FixedDurationTuplet`
    :returns: The corresponding MEI tupletspan Element.
    :rtype: :class:`lxml.etree.ElementTree.Element`
    '''
    if isinstance(abjad_tuplet, Tuplet) and not isinstance(abjad_tuplet, FixedDurationTuplet):
        numerator = six.b(str(abjad_tuplet.multiplier.numerator))
        denominator = six.b(str(abjad_tuplet.multiplier.denominator))
        tupletspan = etree.Element(mei.TUPLET_SPAN,num=denominator, numBase=numerator)
        add_xml_ids(abjad_tuplet, tupletspan)
        return tupletspan
    elif isinstance(abjad_tuplet, FixedDurationTuplet):
        dots = abjad_tuplet.target_duration.dot_count
        dur = abjad_tuplet.target_duration.lilypond_duration_string
        tupletspan = etree.Element(mei.TUPLET_SPAN)
        if dots:
            dur = dur[:dur.find('.')]
            tupletspan.set('dots', six.b(str(dots)))
        tupletspan.set('dur', six.b(str(dur)))
        add_xml_ids(abjad_tuplet, tupletspan)
        return tupletspan


def calculate_tuplet_duration(tuplet):
    '''
    Calculate the duration of a tuplet that potentially contains nested tuplets.

    :param tuplet: the Abjad tuplet to query for duration.
    :type tuplet: :class:`~abjad.tools.scoretools.Tuplet` or :class:`~abjad.tools.scoretools.FixedDurationTuplet`
    '''
    if isinstance(tuplet, FixedDurationTuplet):
	return tuplet.target_duration
    else:
	return tuplet.multiplied_duration


def setup_outermost_tupletspan(mei_tupletspan, abjad_tuplet):
    '''
    Set an mei tupletspan's 'dur', 'dots', 'n', 'num', and 'numBase' attributes according to info from an abjad Tuplet.

    :param mei_tupletspan: The MEI tupletspan Element to initialize.
    :type mei_tupletspan: :class:`lxml.etree.ElementTree.Element`
    :param abjad_tuplet: the Abjad Tuplet container from which to initialize.
    :type abjad_tuplet: :class:`abjad.tools.scoretools.Tuplet.Tuplet` or :class:`abjad.tools.scoretools.FixedDurationTuplet.FixedDurationTuplet`
    :returns: Abjad Duration.
    :rtype: :class: `abjad.tools.durationtools.Duration.Duration`
    '''
    mei_tupletspan.set('n','1')
    duration = calculate_tuplet_duration(abjad_tuplet)
    dur = duration.lilypond_duration_string
    dots = duration.dot_count
    if dots:
        dur = dur[:dur.find('.')]
        mei_tupletspan.set('dots', six.b(str(dots)))
    mei_tupletspan.set('dur', six.b(dur))
    mei_tupletspan.set('num', six.b(str(abjad_tuplet.multiplier.denominator)))
    mei_tupletspan.set('numBase', six.b(str(abjad_tuplet.multiplier.numerator)))
    add_xml_ids(abjad_tuplet, mei_tupletspan)


def tuplet_to_tupletspan(abjad_tuplet):
    '''
    Convert an empty abjad Tuplet container into an mei tupletspan Element and
    converts a full abjad Tuplet container into a list beginning with a tupletspan
    element and followed by appropriate conversions of the container's leaves.

    :param abjad_tuplet: The Abjad Tuplet container to convert.
    :type abjad_tuplet: :class:`abjad.tools.scoretools.Tuplet.Tuplet` or :class:`abjad.tools.scoretools.FixedDurationTuplet.FixedDurationTuplet`
    :returns: the corresponding MEI tupletspan Element or list of MEI Elements.
    :rtype: :class:`lxml.etree.ElementTree.Element` or list
    '''
    if len(abjad_tuplet) == 0:
        return empty_tuplet_to_tupletspan_element(abjad_tuplet)
    elif isinstance(abjad_tuplet, Tuplet):
        if isinstance(abjad_tuplet, Tuplet) and not isinstance(abjad_tuplet, FixedDurationTuplet):
            abjad_tuplet = abjad_tuplet.to_fixed_duration_tuplet()
        span_n = 1
        component_n = 1
        outermost_span = etree.Element(mei.TUPLET_SPAN)
        setup_outermost_tupletspan(outermost_span, abjad_tuplet)
        output_list = [outermost_span]
        plist = ''
        for x, component in enumerate(abjad_tuplet):
            if isinstance(component, Tuplet):
                span_n += 1
                tuplet_list = tuplet_to_tupletspan(component)
                tuplet_list[0].set('n', six.b(str(span_n)))
                add_xml_ids(component, tuplet_list[0])
                output_list.extend(tuplet_list)
            else:
                mei_component = leaf_to_element(component)
                mei_component.set('n', six.b(str(component_n)))
                component_n += 1
                add_xml_ids(abjad_tuplet[x], mei_component)
                output_list.append(mei_component)
        for element in output_list[1:]:
            plist = plist + str(element.get(xml.ID)) + ' '
        plist = plist[:-1]
        outermost_span.set('startid',six.b(str(output_list[1].get(xml.ID))))
        outermost_span.set('endid',six.b(str(output_list[-1].get(xml.ID))))
        outermost_span.set('plist',plist)
        return output_list


def leaf_to_element(abjad_object):
    '''
    Convert an Abjad leaf (Rest, Note, Chord) container to the corresponding MEI element.

    :param abjad_object: the Abjad leaf to convert.
    :type abjad_object: :class:`abjad.tools.scoretools.Leaf.Leaf`
    :returns: the corresponding MEI Element.
    :rtype: List or :class:`lxml.etree.ElementTree.Element`
    :raises: :exc:`lychee.exceptions.InboundConversionError` when ``abjad_object`` is not a leaf.
    '''
    element_dict = {
        "<class 'abjad.tools.scoretools.Chord.Chord'>": chord_to_chord,
        "<class 'abjad.tools.scoretools.Note.Note'>": note_to_note,
        "<class 'abjad.tools.scoretools.Rest.Rest'>": rest_to_rest,
        "<class 'abjad.tools.scoretools.Skip.Skip'>": skip_to_space,
    }
    try:
        return element_dict[str(type(abjad_object))](abjad_object)
    except KeyError:
        raise exceptions.InboundConversionError(_NOT_A_LEAF_NODE.format(str(type(abjad_object))))


def voice_to_layer(abjad_voice):
    '''
    Convert an abjad Voice into an mei layer Element.

    :param abjad_voice: the Abjad Voice to convert.
    :type abjad_voice: :class:`abjad.tools.scoretools.Voice.Voice`
    :returns: the corresponding MEI layer Element.
    :rtype: :class:`lxml.etree.ElementTree.Element`
    '''
    mei_layer = etree.Element(mei.LAYER,n="1")
    for child in abjad_voice:
        if isinstance(child, Tuplet):
            mei_layer.extend(tuplet_to_tupletspan(child))
        else:
            mei_layer.append(leaf_to_element(child))
    add_xml_ids(abjad_voice, mei_layer)
    return mei_layer


def measure_to_measure(a_measure):
    '''
    Convert an Abjad Measure to an MEI <measure>.

    :param a_measure: The Measure to convert.
    :type a_measure: :class:`abjad.tools.scoretools.Measure`
    :returns: The MEI <measure> element.
    :rtype: :class:`~lxml.etree.ElementTree._Element`
    '''
    m_measure = etree.Element(mei.MEASURE, n=str(a_measure.measure_number))
    add_xml_ids(a_measure, m_measure)

    # the <measure> needs a <layer> so we'll invent one
    m_layer = m_measure.makeelement(mei.LAYER, {'n': '1'})  # no Abjad Voice means no @xml:id
    add_xml_ids(a_measure, m_layer)
    m_measure.append(m_layer)

    # the the Abjad measure's content in the <layer>
    for a_leaf in a_measure:
        m_layer.append(leaf_to_element(a_leaf))

    return m_measure


def staff_to_staff(abjad_staff):
    '''
    Convert an abjad Staff to an mei staff Element.
    Handles sibling Voice and Leaf components by flattening all into a single Voice.

    :param abjad_staff: the Abjad Staff to convert.
    :type abjad_staff: :class:`abjad.tools.scoretools.Staff.Staff`
    :returns: the corresponding MEI Element or list of Elements.
    :rtype: :class:`lxml.etree.ElementTree.Element`

    .. note:: Because this function cannot determine the correct @n attribute of the ``abjad_staff``,
        *both* the @n and @xml:id attributes are unset for the returned ``<staff>`` element. It is
        the caller's responsibilty to provide the @n attribute, then @xml:id, which depends on the
        former.
    '''
    mei_staff = etree.Element(mei.STAFF)

    if len(abjad_staff) > 0:
        if isinstance(abjad_staff[0], Voice) and abjad_staff.is_simultaneous:
            # simultaneous Voices become <layer> in <staff>
            # raise NotImplementedError('a')
            for i, voice in enumerate(abjad_staff):
                mei_layer = voice_to_layer(voice)
                mei_layer.set('n', str(i + 1))
                add_xml_ids(abjad_staff, mei_layer)
                mei_staff.append(mei_layer)

        elif isinstance(abjad_staff[0], Measure):
            for a_measure in abjad_staff:
                mei_staff.append(measure_to_measure(a_measure))

        else:
            # sequential Voices and/or mixture of Voices and leaf nodes are flattened to one <layer>
            # raise NotImplementedError('b')
            out_voice = Voice()
            for component in abjad_staff:
                if isinstance(component, Voice):
                    out_voice.extend([mutate(x).copy() for x in component])
                else:
                    out_voice.append(mutate(component).copy())

            mei_staff.append(voice_to_layer(out_voice))

    return mei_staff


def set_initial_clef(a_staff, m_staffdef):
    '''
    Set the initial clef for a <staffDef> according to the Abjad Staff.

    :param a_staff: The Abjad Staff in which to find the initial clef.
    :type a_staff: :class:`abjad.tools.scoretools.Staff`
    :param m_staffdef: The MEI <staffDef> element in which to set the initial clef.
    :type m_staffdef: :class:`lxml.etree.ElementTree.Element`
    :returns: `None`

    If the clef is unset, or a currently-unsupported type, nothing happens.
    '''
    a_clef = inspect_(a_staff).get_effective(Clef)

    if a_clef:
        clef_name = a_clef.name.lower()
        if clef_name == 'treble':
            shape = 'G'
            line = '2'
        elif clef_name == 'bass':
            shape = 'F'
            line = '4'
        elif clef_name == 'tenor':
            shape = 'C'
            line = '4'
        elif clef_name == 'alto':
            shape = 'C'
            line = '3'
        else:
            return

        m_staffdef.set('clef.shape', shape)
        m_staffdef.set('clef.line', line)


def score_to_section(abjad_score):
    '''
    Convert an abjad Score into an mei section Element.

    :param abjad_score: the Abjad Score object to convert.
    :type abjad_score: :class:`abjad.tools.scoretools.Score.Score`
    :returns: the corresponding MEI section Element.
    :rtype: :class:`lxml.etree.ElementTree.Element`
    '''
    #an empty abjad Score returns an empty mei section Element
    if len(abjad_score) == 0:
        mei_section = etree.Element(mei.SECTION,n='1')
        add_xml_ids(abjad_score, mei_section)
        return mei_section
    #otherwise set up a section element containing a master staff group
    mei_section = etree.Element(mei.SECTION, n='1')
    add_xml_ids(abjad_score, mei_section)
    score_def = etree.Element(mei.SCORE_DEF)
    add_xml_ids(abjad_score, score_def)
    mei_section.append(score_def)
    mei_main_staff_group = etree.Element(mei.STAFF_GRP,symbol='line')
    score_def.append(mei_main_staff_group)
    staffCounter = 1
    for component in abjad_score:
        if isinstance(component, Staff):
            #if the component is a staff, convert to an mei staff
            abjad_staff = component
            mei_staff = staff_to_staff(abjad_staff)
            mei_staff.set('n', str(staffCounter))
            mei_section.append(mei_staff)
            add_xml_ids(abjad_staff, mei_staff)
            staff_def = etree.Element(mei.STAFF_DEF,lines='5',n=str(staffCounter))
            set_initial_clef(abjad_staff, staff_def)
            add_xml_ids(abjad_staff, staff_def)
            mei_main_staff_group.append(staff_def)
            staffCounter += 1
        elif isinstance(component, StaffGroup):
            #if it's a staff group, convert to a staff group containing staff Elements
            abjad_staff_group = component
            mei_staff_group = etree.Element(mei.STAFF_GRP,symbol='bracket')
            add_xml_ids(abjad_staff_group, mei_staff_group)
            mei_main_staff_group.append(mei_staff_group)
            for staff in abjad_staff_group:
                abjad_staff = staff
                mei_staff = staff_to_staff(abjad_staff)
                mei_staff.set('n', str(staffCounter))
                add_xml_ids(abjad_staff, mei_staff)
                mei_section.append(mei_staff)
                staff_def = etree.Element(mei.STAFF_DEF,lines='5',n=str(staffCounter))
                set_initial_clef(abjad_staff, staff_def)
                add_xml_ids(abjad_staff, staff_def)
                mei_staff_group.append(staff_def)
                staffCounter += 1
    return mei_section
