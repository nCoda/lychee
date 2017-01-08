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


def note(m_note):
    '''
    '''
    assert m_note.tag == mei.NOTE
    post = m_note.get('pname')
    if m_note.get('accid.ges'):
        post += _VALID_ACCIDENTALS[m_note.get('accid.ges')]
    post += _OCTAVE_TO_MARK[m_note.get('oct')]
    if m_note.get('accid'):
        post += '!'
    post += duration(m_note)
    return post


def rest(m_rest):
    '''
    '''
    assert m_rest.tag == mei.REST
    post = 'r'
    post += duration(m_rest)
    return post


def chord(m_chord):
    '''
    '''
    assert m_chord.tag == mei.CHORD
    l_chord = []
    for m_note in m_chord.iter(tag=mei.NOTE):
        l_chord.append(note(m_note))

    l_chord = '<{0}>{1}'.format(' '.join(l_chord), duration(m_chord))

    return l_chord


def measure_rest(m_measure_rest):
    '''
    '''
    if m_measure_rest.tag != mei.M_REST:
        raise exceptions.OutboundConversionError("measure_rest was called on an XML node that isn't <mei:mRest>")
    l_measure_rest = 'R'
    l_measure_rest += duration(m_measure_rest)
    return l_measure_rest


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
            else:
                action.failure(
                    'missed a {tag_name} in a <{container_name}>',
                    tag_name=elem.tag,
                    container_name=m_container.tag,
                    )

    return post


def layer(m_layer):
    '''Convert an MEI layer element to a LilyPond string.'''
    assert m_layer.tag == mei.LAYER
    post = ['%{{ l.{} %}}'.format(m_layer.get('n'))]
    post.extend(sequential_music(m_layer))
    return ' '.join(post)


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


def measure(m_meas):
    '''
    '''
    assert m_meas.tag == mei.MEASURE
    before = ['%{{ m.{} %}}'.format(m_meas.get('n'))]
    after = ['|\n']
    post = before + layers(m_meas) + after
    return ' '.join(post)


def clef(m_staffdef):
    '''
    '''
    assert m_staffdef.tag == mei.STAFF_DEF
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
            return '\n'

        return '\\clef "{0}"\n'.format(post)

    else:
        return '\n'


def key(m_staffdef):
    '''
    '''
    assert m_staffdef.tag == mei.STAFF_DEF
    CONV = {
        '7f': 'ces',
        '6f': 'ges',
        '5f': 'des',
        '4f': 'aes',
        '3f': 'ees',
        '2f': 'bes',
        '1f': 'f',
        '0': 'c',
        '1s': 'g',
        '2s': 'd',
        '3s': 'a',
        '4s': 'e',
        '5s': 'b',
        '6s': 'fis',
        '7s': 'cis',
    }
    if m_staffdef.get('key.sig'):
        if m_staffdef.get('key.sig') in CONV:
            post = CONV[m_staffdef.get('key.sig')]
            post = '\\key {0} \\major\n'.format(post)
            return post

        else:
            return '\n'

    else:
        return '\n'


def meter(m_staffdef):
    '''
    '''
    assert m_staffdef.tag == mei.STAFF_DEF
    if m_staffdef.get('meter.count') and m_staffdef.get('meter.unit'):
        return '\\time {0}/{1}\n'.format(m_staffdef.get('meter.count'), m_staffdef.get('meter.unit'))
    else:
        return '\n'


def staff(m_staff, m_staffdef):
    '''
    '''
    assert m_staff.tag == mei.STAFF
    assert m_staffdef.tag == mei.STAFF_DEF

    post = [
        '\\new Staff {\n',
        '%{{ staff {0} %}}\n'.format(m_staff.get('n')),
        '\\set Staff.instrumentName = "{0}"\n'.format(m_staffdef.get('label', '')),
        clef(m_staffdef),
        key(m_staffdef),
        meter(m_staffdef),
    ]

    there_are_no_measures = True
    for elem in m_staff.iterchildren(tag=mei.MEASURE):
        post.append(measure(elem))
        there_are_no_measures = False

    if there_are_no_measures:
        post.append(' '.join(layers(m_staff)) + '\n')

    post.append('}\n')

    return ''.join(post)


def section(m_section):
    '''
    '''
    assert m_section.tag == mei.SECTION

    post = [
        '\\version "2.18.2"\n',
        '\\score {\n',
        '<<\n',
    ]

    for m_staffdef in m_section.iterfind('.//{0}'.format(mei.STAFF_DEF)):
        query = './/{tag}[@n="{n}"]'.format(tag=mei.STAFF, n=m_staffdef.get('n'))
        post.append(staff(m_section.find(query), m_staffdef))

    post.append('>>\n')
    post.append('\\layout { }\n')
    post.append('}\n')

    return ''.join(post)
