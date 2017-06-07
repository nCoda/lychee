#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/mei_to_ly.py
# Purpose:                Converts an MEI document to a LilyPond document.
#
# Copyright (C) 2016 Christopher Antila
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
Converts an MEI document to a LilyPond document.

.. warning::
    This module is intended for internal *Lychee* use only, so the API may change without notice.
    If you wish to use this module outside *Lychee*, please contact us to discuss the best way.

.. tip::
    We recommend that you use the converters indirectly.
    Refer to :ref:`how-to-use-converters` for more information.
'''

from lychee import exceptions
from lychee.logs import OUTBOUND_LOG as log
from lychee.namespaces import mei
from lychee.utils import lilypond_utils


def check_tag(m_thing, tag_name):
    if m_thing.tag != tag_name:
        raise exceptions.OutboundConversionError(
            "Wrong tag: expected <{}>, found <{}>."
            .format(m_thing.tag, tag_name))


@log.wrap('info', 'convert LMEI to LilyPond')
def convert(document, **kwargs):
    '''
    Convert an MEI document into a LilyPond document.

    :param document: The MEI document. Must be provided as a kwarg.
    :type document: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding LilyPond document.
    :rtype: str
    :raises: :exc:`lychee.exceptions.OutboundConversionError` when there is a forseeable error.
    '''
    CONV_FUNCS = {
        mei.NOTE: note,
        mei.REST: rest,
        mei.M_REST: measure_rest,
        mei.LAYER: layer,
        mei.MEASURE: measure,
        mei.STAFF: staff,
        mei.SECTION: section,
    }
    if document.tag in CONV_FUNCS:
        return CONV_FUNCS[document.tag](document)
    else:
        raise exceptions.OutboundConversionError('LMEI-to-LilyPond cannot do {0} elements'.format(document.tag))


_OCTAVE_TO_MARK = {
    '8': "'''''",
    '7': "''''",
    '6': "'''",
    '5': "''",
    '4': "'",
    '3': "",
    '2': ",",
    '1': ",,",
}

_VALID_ACCIDENTALS = {
    's': 'is',
    'f': 'es',
    'ss': 'isis',
    'ff': 'eses',
}


def duration(m_thing):
    '''
    Extract the duration of an MEI object -- note, chord, or rest -- as a LilyPond duration string.
    '''
    post = m_thing.get('dur', '')
    dot_count = int(m_thing.get('dots', '0'))
    if dot_count < 0:
        raise exceptions.OutboundConversionError('Negative dot count')
    if dot_count > 0 and post == '':
        post = '4'
    post += '.' * dot_count
    return post


def tie(m_thing):
    '''
    Find the LilyPond tie string of an MEI object.
    '''
    if m_thing.get('tie') in ('i', 'm'):
        return '~'
    return ''


def slur(m_thing):
    '''
    Find the LilyPond slur string of an MEI object.
    '''
    slur_attribute = m_thing.get('slur')
    if slur_attribute is None:
        return ''

    # MEI slurs consist of a letter (i/m/t) and a numerical
    # slur ID. We only want the letter here since overlapping
    # slurs are not yet supported.
    slur_letter = slur_attribute.strip()[0]
    if slur_letter == 'i':
        return '('
    elif slur_letter == 't':
        return ')'
    return ''


@log.wrap('debug', 'convert note')
def note(m_note):
    '''
    '''
    check_tag(m_note, mei.NOTE)
    m_accid = m_note.find(mei.ACCID)
    accid = m_note.get('accid.ges', '')
    if m_accid is not None:
        accid = m_accid.get('accid', '')
    post = lilypond_utils.translate_pitch_name(m_note.get('pname'), accid)
    post += _OCTAVE_TO_MARK[m_note.get('oct')]
    post += duration(m_note)
    post += tie(m_note)
    post += slur(m_note)
    return post


@log.wrap('debug', 'convert rest')
def rest(m_rest):
    '''
    '''
    check_tag(m_rest, mei.REST)
    post = 'r'
    post += duration(m_rest)
    return post


@log.wrap('debug', 'convert chord')
def chord(m_chord):
    '''
    '''
    check_tag(m_chord, mei.CHORD)
    l_notes = []
    for m_note in m_chord.iter(tag=mei.NOTE):
        l_notes.append(note(m_note))

    post = duration(m_chord)
    post += tie(m_chord)
    post += slur(m_chord)

    l_chord = '<{0}>{1}'.format(' '.join(l_notes), post)
    return l_chord


def measure_rest(m_measure_rest):
    '''
    '''
    if m_measure_rest.tag != mei.M_REST:
        raise exceptions.OutboundConversionError("measure_rest was called on an XML node that isn't <mei:mRest>")
    l_measure_rest = 'R'
    l_measure_rest += duration(m_measure_rest)
    return l_measure_rest


@log.wrap('debug', 'convert sequential music')
def sequential_music(m_container):
    '''
    Convert the contents of any MEI element, interpreted as a container of
    sequential music, to an array of LilyPond strings to be joined together
    with whitespace.
    '''
    post = []
    for elem in m_container.iterchildren('*'):
        with log.debug('convert element in a <{}>'.format(m_container.tag)) as action:
            if elem.tag == mei.NOTE:
                post.append(note(elem))
            elif elem.tag == mei.REST:
                post.append(rest(elem))
            elif elem.tag == mei.CHORD:
                post.append(chord(elem))
            elif elem.tag == mei.M_REST:
                post.append(measure_rest(elem))
            elif elem.tag == mei.STAFF_DEF:
                l_staff_def = staffdef(elem)
                # staffdef might return an empty string.
                if l_staff_def:
                    post.append(l_staff_def)
            else:
                action.failure(
                    'missed a {tag_name} in a <{container_name}>',
                    tag_name=elem.tag,
                    container_name=m_container.tag,
                    )

    return post


@log.wrap('debug', 'convert layer')
def layer(m_layer):
    '''Convert an MEI layer element to a LilyPond string.'''
    check_tag(m_layer, mei.LAYER)
    post = ['%{{ l.{} %}}'.format(m_layer.get('n'))]
    post.extend(sequential_music(m_layer))
    return ' '.join(post)


@log.wrap('debug', 'convert parallel music')
def layers(m_container):
    '''
    Convert the contents of any MEI element containing multiple layers,
    interpreted as parallel music, to an array of LilyPond strings to be
    joined together with whitespace.
    '''
    before_layers = []
    after_layers = []
    layers = []
    for elem in m_container.iterchildren(tag=mei.LAYER):
        layers.append(layer(elem))

    if len(layers) > 1:
        before_layers.append('<< {')
        after_layers.insert(0, '} >>')
        layers = [' } \\\ { '.join(layers)]

    post = before_layers + layers + after_layers
    return post


@log.wrap('debug', 'convert measure')
def measure(m_meas):
    '''
    '''
    check_tag(m_meas, mei.MEASURE)
    before = ['%{{ m.{} %}}'.format(m_meas.get('n'))]
    after = ['|\n']
    post = before + layers(m_meas) + after
    return ' '.join(post)


@log.wrap('debug', 'convert clef')
def clef(m_staffdef):
    '''
    '''
    check_tag(m_staffdef, mei.STAFF_DEF)
    if m_staffdef.get('clef.shape') and m_staffdef.get('clef.line'):
        shape = m_staffdef.get('clef.shape')
        line = m_staffdef.get('clef.line')
        if shape == 'F' and line == '4':
            post = 'bass'
        elif shape == 'C' and line == '4':
            post = 'tenor'
        elif shape == 'C' and line == '3':
            post = 'alto'
        elif shape == 'G' and line == '2':
            post = 'treble'
        else:
            return ''
        return '\\clef "{0}"'.format(post)

    else:
        return ''


@log.wrap('debug', 'convert key signature')
def key(m_staffdef):
    '''
    '''
    check_tag(m_staffdef, mei.STAFF_DEF)
    CONV = {
        '7f': ('c', 'f'),
        '6f': ('g', 'f'),
        '5f': ('d', 'f'),
        '4f': ('a', 'f'),
        '3f': ('e', 'f'),
        '2f': ('b', 'f'),
        '1f': ('f', ''),
        '0': ('c', ''),
        '1s': ('g', ''),
        '2s': ('d', ''),
        '3s': ('a', ''),
        '4s': ('e', ''),
        '5s': ('b', ''),
        '6s': ('f', 's'),
        '7s': ('c', 's'),
    }
    if m_staffdef.get('key.sig'):
        if m_staffdef.get('key.sig') in CONV:
            pitch_name, accidental = CONV[m_staffdef.get('key.sig')]
            post = '\\key {0} \\major'.format(
                lilypond_utils.translate_pitch_name(
                    pitch_name, accidental))
            return post

        else:
            return ''

    else:
        return ''


@log.wrap('debug', 'convert time signature')
def meter(m_staffdef):
    '''
    '''
    check_tag(m_staffdef, mei.STAFF_DEF)
    if m_staffdef.get('meter.count') and m_staffdef.get('meter.unit'):
        return '\\time {0}/{1}'.format(m_staffdef.get('meter.count'), m_staffdef.get('meter.unit'))
    else:
        return ''


@log.wrap('info', 'convert inline staffdef')
def staffdef(m_staffdef):
    '''
    Convert an "inline" staffDef (one that appears inside a layer) to
    LilyPond code.
    '''
    check_tag(m_staffdef, mei.STAFF_DEF)
    post = []
    l_clef = clef(m_staffdef)
    l_key = key(m_staffdef)
    l_meter = meter(m_staffdef)
    if l_clef:
        post.append(l_clef)
    if l_key:
        post.append(l_key)
    if l_meter:
        post.append(l_meter)
    return ' '.join(post)


@log.wrap('info', 'convert staff')
def staff(m_staff, m_staffdef):
    '''
    '''
    check_tag(m_staff, mei.STAFF)
    check_tag(m_staffdef, mei.STAFF_DEF)

    post = [
        '\\new Staff {\n',
        '%{{ staff {0} %}}\n'.format(m_staff.get('n')),
        '\\set Staff.instrumentName = "{0}"\n'.format(m_staffdef.get('label', '')),
        clef(m_staffdef) + '\n',
        key(m_staffdef) + '\n',
        meter(m_staffdef) + '\n',
    ]

    there_are_no_measures = True
    for elem in m_staff.iterchildren(tag=mei.MEASURE):
        post.append(measure(elem))
        there_are_no_measures = False

    if there_are_no_measures:
        post.append(' '.join(layers(m_staff)) + '\n')

    post.append('}\n')

    return ''.join(post)


@log.wrap('info', 'convert section')
def section(m_section):
    '''
    '''
    check_tag(m_section, mei.SECTION)

    post = [
        '\\version "2.18.2"\n',
        '\\score {\n',
        '<<\n',
    ]

    for m_staffdef in m_section.iterfind('./{}//{}'.format(mei.SCORE_DEF, mei.STAFF_DEF)):
        query = './/{tag}[@n="{n}"]'.format(tag=mei.STAFF, n=m_staffdef.get('n'))
        post.append(staff(m_section.find(query), m_staffdef))

    post.append('>>\n')
    post.append('\\layout { }\n')
    post.append('}\n')

    return ''.join(post)
