#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/abjad_to_mei.py
# Purpose:                Converts an Abjad document to an MEI document.
#
# Copyright (C) 2015 Jeffrey Treviño
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
Converts an Abjad document to an MEI document.

..  container:: example

    **Example 1.** Initializes from Abjad note:

    ::

        >>> note = Note("cqs''?8.")
        >>> out = abjadNoteTomeiTree(note)

    ..  doctest::

        >>> >>> ET.tostring(out.getroot())
        <note dots="1" dur="8" octave="5" pname="c"><accid accid="sd" func="cautionary" /></note>
'''


import uuid

from lxml import etree as ETree
import six
import hashlib

from abjad import *
from abjad.tools.scoretools.NoteHead import NoteHead

'''
from abjad.tools.scoretools.Note import Note
from abjad.tools.scoretools.Rest import Rest
from abjad.tools.scoretools.Chord import Chord
from abjad.tools.scoretools.NoteHead import NoteHead
from abjad.tools.durationtools.Multiplier import Multiplier
from abjad.tools.durationtools.Duration import Duration
from abjad.tools.scoretools.Voice import Voice
from abjad.tools.scoretools.Staff import Staff
from abjad.tools.scoretools.StaffGroup import StaffGroup
from abjad.tools.topleveltools.mutate import mutate
from abjad.tools.topleveltools import *
'''

#import lychee
#from lychee.signals import inbound


_MEINS = '{http://www.music-encoding.org/ns/mei}'
_XMLNS = '{http://www.w3.org/XML/1998/namespace}id'
ETree.register_namespace('mei', _MEINS[1:-1])


def convert(document, **kwargs):
    '''
    Convert an Abjad document into an MEI document.

    :param object document: The Abjad document.
    :returns: The corresponding MEI document.
    :rtype: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    '''
    inbound.CONVERSION_STARTED.emit()
    lychee.log('{}.convert(document="{}")'.format(document))

    # TODO: put the conversion-handling bits here
    # TODO: CONVERS_FINISH.emit() should be called with the converted Element or ElementTree

    inbound.CONVERSION_FINISH.emit(converted='<l-mei stuff>')
    lychee.log('{}.convert() after finish signal'.format(__name__))


def convert_accidental_abjad_to_mei(abjad_accidental_string):
    # Helper that converts an Abjad accidental string to an mei accidental string.
    accidental_dictionary = {'': '', 'f': 'f', 's': 's', 'ff': 'ff', 'ss': 'x', 
                            'tqs': 'su', 'qs': 'sd', 'tqf': 'fd', 'qf': 'fu'}
    return accidental_dictionary[abjad_accidental_string]

def add_xml_id_to_abjad_object_and_mei_element_pair(abjad_object, mei_element):
    if isinstance(abjad_object, NoteHead):
        parent_chord = abjad_object.client
        print type(parent_chord)
        parentage = inspect(parent_chord).get_parentage()
    else:
        parentage = inspect(abjad_object).get_parentage()
    id_string = str(abjad_object) + str(parentage.score_index)
    abjad_id = six.b(id_string)
    hasher = hashlib.new('SHA256', abjad_id)
    the_xmlid = hasher.hexdigest()
    if not isinstance(abjad_object, NoteHead):
        attach(the_xmlid, abjad_object)
    mei_element.set(_XMLNS, the_xmlid)


def abjad_note_to_mei_note(abjad_note):
        #also handles abjad NoteHead objects (which have pitch and octave attrs but no dur)
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
        mei_note = ETree.Element("{}note".format(_MEINS), dictionary)
        if duration:
            mei_note.set('dur',str(duration))
        if dots:
            mei_note.set('dots',str(dots))
        if accidental:
            if is_cautionary:
                accid = ETree.SubElement(mei_note,'{}accid'.format(_MEINS),accid=accidental,func='cautionary')
                
            else:
                mei_note.set('accid.ges', accidental)
                if is_forced:
                    mei_note.set('accid', accidental)
        else:
            if is_cautionary:
                accid = ETree.SubElement(mei_note,'{}accid'.format(_MEINS),accid='n',func='cautionary')
            if is_forced:
                mei_note.set('accid.ges', 'n')
                mei_note.set('accid', 'n')
        if not isinstance(abjad_note, NoteHead):
            add_xml_id_to_abjad_object_and_mei_element_pair(abjad_note, mei_note)
        return mei_note

def abjad_rest_to_mei_rest(abjad_rest):
    duration = abjad_rest.written_duration.lilypond_duration_string
    dots = abjad_rest.written_duration.dot_count
    mei_rest = ETree.Element('{}rest'.format(_MEINS))
    if dots:
        dot_index = duration.find('.')
        dur_number_string = duration[:dot_index]
        mei_rest.set('dots',str(dots))
    else:
        dur_number_string = duration
    mei_rest.set('dur',dur_number_string)
    add_xml_id_to_abjad_object_and_mei_element_pair(abjad_rest, mei_rest)
    return mei_rest


def abjad_chord_to_mei_chord(abjad_chord):
    mei_chord = ETree.Element('{}chord'.format(_MEINS))
    dots = abjad_chord.written_duration.dot_count
    dur_string = abjad_chord.written_duration.lilypond_duration_string
    if dots:
        mei_chord.set('dots',str(abjad_chord.written_duration.dot_count))
        dur_string = dur_string[:dur_string.find('.')]
    mei_chord.set('dur',dur_string)
    for head in abjad_chord.note_heads:
        mei_note = abjad_note_to_mei_note(head)
        mei_chord.append(mei_note)
    add_xml_id_to_abjad_object_and_mei_element_pair(abjad_chord, mei_chord)
    return mei_chord

def abjad_leaf_to_mei_element(abjad_object):
    if isinstance(abjad_object, Rest):
        return abjad_rest_to_mei_rest(abjad_object)
    elif isinstance(abjad_object, (Note,NoteHead)):
        return abjad_note_to_mei_note(abjad_object)
    elif isinstance(abjad_object, Chord):
        return abjad_chord_to_mei_chord(abjad_object)

def abjad_voice_to_mei_layer(abjad_voice):
    mei_layer = ETree.Element('{}layer'.format(_MEINS),n="1")
    for child in abjad_voice:
        mei_layer.append(abjad_leaf_to_mei_element(child))
    add_xml_id_to_abjad_object_and_mei_element_pair(abjad_voice, mei_layer)
    return mei_layer

def abjad_staff_to_mei_staff(abjad_staff):
    mei_staff = ETree.Element('{}staff'.format(_MEINS),n='1')
    if len(abjad_staff) != 0:
        if abjad_staff.is_simultaneous:
            for x,voice in enumerate(abjad_staff):
                mei_layer = abjad_voice_to_mei_layer(voice)
                add_xml_id_to_abjad_object_and_mei_element_pair(abjad_staff, mei_layer)
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
    add_xml_id_to_abjad_object_and_mei_element_pair(abjad_staff, mei_staff)
    return mei_staff

def abjad_score_to_mei_section(abjad_score):
    if len(abjad_score) == 0:
        mei_section = ETree.Element('{}section'.format(_MEINS),n='1')
        add_xml_id_to_abjad_object_and_mei_element_pair(abjad_score, mei_section)
        return mei_section
    mei_section = ETree.Element('{}section'.format(_MEINS), n='1')
    add_xml_id_to_abjad_object_and_mei_element_pair(abjad_score, mei_section)
    score_def = ETree.Element('{}scoreDef'.format(_MEINS))
    score_def.set(_XMLNS, mei_section.get(_XMLNS) + 'scoreDef')
    mei_section.append(score_def)
    mei_main_staff_group = ETree.Element('{}staffGrp'.format(_MEINS),symbol='line')
    score_def.append(mei_main_staff_group)
    staffCounter = 1
    for component in abjad_score:
        if isinstance(component, Staff):
            abjad_staff = component
            mei_staff = abjad_staff_to_mei_staff(abjad_staff)
            mei_staff.set('n', str(staffCounter))
            mei_section.append(mei_staff)
            add_xml_id_to_abjad_object_and_mei_element_pair(abjad_staff, mei_staff)
            staff_def = ETree.Element('{}staffDef'.format(_MEINS),lines='5',n=str(staffCounter))
            staff_def.set(_XMLNS, mei_staff.get(_XMLNS) + 'staffDef')
            mei_main_staff_group.append(staff_def)
            staffCounter += 1
        elif isinstance(component, StaffGroup):
            abjad_staff_group = component
            mei_staff_group = ETree.Element('{}staffGrp'.format(_MEINS),symbol='bracket')
            add_xml_id_to_abjad_object_and_mei_element_pair(abjad_staff_group, mei_staff_group)
            mei_main_staff_group.append(mei_staff_group)
            for staff in abjad_staff_group:
                abjad_staff = component
                mei_staff = abjad_staff_to_mei_staff(abjad_staff)
                add_xml_id_to_abjad_object_and_mei_element_pair(abjad_staff, mei_staff)
                mei_staff.set('n', str(staffCounter))
                mei_section.append(mei_staff)
                staff_def = ETree.Element('{}staffDef'.format(_MEINS),lines='5',n=str(staffCounter))
                staff_def.set(_XMLNS, mei_staff.get(_XMLNS) + 'staffDef')
                mei_staff_group.append(staff_def)
                staffCounter += 1
    return mei_section

'''
def empty_abjad_tuplet_to_mei_tupletspan_element(abjad_tuplet):
        if hasattr(abjad_tuplet, 'multiplier'):
            numerator = abjad_tuplet.multiplier.numerator
            denominator = abjad_tuplet.multiplier.denominator
            tupletspan = ETree.Element('tupletspan',num=denominator, numBase=numerator)
            return tupletspan
        elif hasattr(abjad_tuplet, 'target_duration'):
            dots = abjad_tuplet.target_duration.dot_count
            dur = abjad_tuplet.target_duration.lilypond_duration_string
            tupletspan = ETree.Element('tupletspan', dur=dur, dots=dots)
            return tupletspan

def abjad_tuplet_to_mei_tupletspan(abjad_tuplet):
    if len(abjad_tuplet) == 0:
        return empty_abjad_tuplet_to_mei_tupletspan_element(abjad_tuplet)
    # set up output
    outermost_span = ETree.Element('tupletspan')
    duration = inspect(abjad_tuplet).get_duration()
    dur = duration.lilypond_duration_string
        output_list = [outermost_span]
    for component in abjad_tuplet:
        #
    #otherwise return list of tupletspan and leaf elements
    tupletspan = ETree.Element('tupletspan',n='1')
'''