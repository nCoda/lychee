#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/ly_to_mei_new.py
# Purpose:                Converts a LilyPond document to a Lychee-MEI document.
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
Converts a LilyPond document to a Lychee-MEI document.

.. warning::
    This module is intended for internal *Lychee* use only, so the API may change without notice.
    If you wish to use this module outside *Lychee*, please contact us to discuss the best way.

.. tip::
    We recommend that you use the converters indirectly.
    Refer to :ref:`how-to-use-converters` for more information.
'''

# NOTE for Lychee developers:
#
# The module "lychee.converters.lilypond_parser" is autogenerated from "lilypond.ebnf" using Grako.
#
# Run this command in this directory to regenerate the "lilypond_parser" module after you update
# the EBNF grammar specification:
# $ python -m grako -c -o lilypond_parser.py lilypond.ebnf

from lxml import etree

from lychee.converters.inbound import lilypond_parser
from lychee import exceptions
from lychee.logs import INBOUND_LOG as log
from lychee.namespaces import mei
from lychee.signals import inbound


_ACCIDENTAL_MAPPING = {
    'eses': 'ff',
    'es': 'f',
    'is': 's',
    'isis': 'ss',
}
_OCTAVE_MAPPING = {
    ",,": '1',
    ",": '2',
    "'''''": '8',
    "''''": '7',
    "'''": '6',
    "''": '5',
    "'": '4',
    None: '3'
}


def check(condition, message=None):
    """
    Check that ``condition`` is ``True``.

    :param bool condition: This argument will be checked to be ``True``.
    :param str message: A failure message to use if the check does not pass.
    :raises: :exc:`exceptions.LilyPondError` when ``condition`` is anything other than ``True``.

    Use this function to guarantee that something is the case. This function replaces the ``assert``
    statement but is always executed (not only in debug mode).

    **Example 1**

    >>> check(5 == 5)

    The ``5 == 5`` evaluates to ``True``, so the function returns just fine.

    **Example 2**

    >>> check(5 == 4)

    The ``5 == 4`` evaluates to ``False``, so the function raises an :exc:`exceptions.LilyPondError`.
    """
    message = 'check failed' if message is None else message
    if condition is not True:
        raise exceptions.LilyPondError(message)


def convert(document, **kwargs):
    '''
    Convert a LilyPond document into an MEI document. This is the entry point for Lychee conversions.

    :param str document: The LilyPond document.
    :returns: The corresponding MEI document.
    :rtype: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    '''
    inbound.CONVERSION_STARTED.emit()
    section = convert_no_signals(document)
    inbound.CONVERSION_FINISH.emit(converted=section)


def convert_no_signals(document):
    '''
    It's the convert() function that returns the converted document rather than emitting it with
    the CONVERSION_FINISHED signal. Mostly for testing.
    '''

    with log.info('parse LilyPond') as action:
        parser = lilypond_parser.LilyPondParser(parseinfo=False)
        parsed = parser.parse(document, filename='file', trace=False)

    with log.info('convert LilyPond') as action:
        if 'score' in parsed:
            check_version(parsed)
        elif 'staff' in parsed:
            parsed = {'score': [parsed]}
        elif isinstance(parsed, list) and 'measure' in parsed[0]:
            parsed = {'score': [{'staff': {'measures': parsed}}]}
        else:
            raise RuntimeError('need score, staff, or measures for the top-level thing')

        converted = do_file(parsed)

    return converted


@log.wrap('info', 'check syntax version', 'action')
def check_version(parsed, action):
    '''
    Guarantees the version is at least somewhat compatible.

    If the major version is not '2', raises.
    If the minor version is other than '18', warns.
    '''
    if parsed['version']:
        if parsed['version'][0] != '2':
            raise RuntimeError('inbound LilyPond parser expects version 2.18.x')
        elif parsed['version'][1] != '18':
            action.failure('inbound LilyPond parser expects version 2.18.x')
    else:
        action.failure('missing version info')


def do_file(parsed):
    '''
    Take the parsed result of a whole file and convert it.

    :param dict parsed: The LilyPond file straight from the parser.
    :returns: A converted ``<section>`` element in Lychee-MEI.
    :rtype: :class:`lxml.etree.Element`
    '''
    m_section = etree.Element(mei.SECTION)
    m_scoredef = etree.SubElement(m_section, mei.SCORE_DEF)
    m_staffgrp = etree.SubElement(m_scoredef, mei.STAFF_GRP)

    staff_n = 1
    for l_staff in parsed['score']:
        m_staffdef = etree.SubElement(m_staffgrp, mei.STAFF_DEF, {'n': str(staff_n), 'lines': '5'})
        do_staff(l_staff, m_section, staff_n, m_staffdef)
        staff_n += 1

    return m_section


def do_staff(l_staff, m_section, staff_n, m_staffdef):
    '''
    :param dict l_staff: A LilyPond staff from the parser.
    :param m_section: An MEI ``<section>`` element to put this staff into.
    :type m_section: :class:`lxml.etree.Element`
    :param int staff_n: The @n value for this ``<staff>``.
    '''
    m_staff = etree.SubElement(m_section, mei.STAFF, {'n': str(staff_n)})

    measure_n = 1
    for l_measure in l_staff['staff']['measures']:
        do_measure(l_measure, m_staff, measure_n, m_staffdef)
        measure_n += 1

    return m_staff


def set_initial_clef(l_clef, m_staffdef):
    '''
    Set a Lilypond ``\clef`` command as the initial clef for a staff.
    '''
    assert l_clef['ly_type'] == 'clef'

    if l_clef['type'] == 'bass':
        m_staffdef.set('clef.shape', 'F')
        m_staffdef.set('clef.line', '4')
    elif l_clef['type'] == 'tenor':
        m_staffdef.set('clef.shape', 'C')
        m_staffdef.set('clef.line', '4')
    elif l_clef['type'] == 'alto':
        m_staffdef.set('clef.shape', 'C')
        m_staffdef.set('clef.line', '3')
    elif l_clef['type'] == 'treble':
        m_staffdef.set('clef.shape', 'G')
        m_staffdef.set('clef.line', '2')

    return m_staffdef


def set_initial_time(l_time, m_staffdef):
    '''
    Set a Lilypond ``\time`` command as the initial time signature for a staff.
    '''
    assert l_time['ly_type'] == 'time'

    m_staffdef.set('meter.count', l_time['count'])
    m_staffdef.set('meter.unit', l_time['unit'])

    return m_staffdef


def set_initial_key(l_key, m_staffdef):
    '''
    Set a LilyPond ``\key`` command as the initial key signature for a staff.

    NOTE: this function supports major keys only, for now, and will raise RuntimeError on minor.
    '''
    assert l_key['ly_type'] == 'key'
    assert l_key['mode'] == 'major'

    CONV = {
        'ces': '7f',
        'ges': '6f',
        'des': '5f',
        'aes': '4f',
        'ees': '3f',
        'bes': '2f',
        'f': '1f',
        'c': '0',
        'g': '1s',
        'd': '2s',
        'a': '3s',
        'e': '4s',
        'b': '5s',
        'fis': '6s',
        'cis': '7s',
    }

    if l_key['accid']:
        keynote = l_key['keynote'] + l_key['accid']
    else:
        keynote = l_key['keynote']

    m_staffdef.set('key.sig', CONV[keynote])

    return m_staffdef


def set_instrument_name(l_name, m_staffdef):
    '''
    Set a Lilypond ``\set Staff.instrumentName`` command as the staff's instrument name.
    '''
    assert l_name['ly_type'] == 'instr_name'

    m_staffdef.set('label', l_name['instrument_name'])

    return m_staffdef


def do_measure(l_measure, m_staff, measure_n, m_staffdef):
    '''
    :param dict l_measure: A LilyPond measure from the parser.
    :param m_staff: An MEI ``<staff>`` element to put this measure into.
    :type m_staff: :class:`lxml.etree.Element`
    :param int measure_n: The @n value for this ``<measure>``.
    '''
    assert l_measure['ly_type'] == 'measure'

    m_measure = etree.SubElement(m_staff, mei.MEASURE, {'n': str(measure_n)})

    options_converters = {
        'clef': set_initial_clef,
        'key': set_initial_key,
        'instr_name': set_instrument_name,
        'time': set_initial_time,
    }
    if l_measure['settings']:
        # We should only use the <staffDef> given to us, which is for the <staff> as a whole, if
        # this is the first <measure>. Otherwise we'll make a <measure>-specific <staffDef>.
        if measure_n > 1:
            m_staffdef = etree.SubElement(m_measure, mei.STAFF_DEF)
        for setting in l_measure['settings']:
            if setting['ly_type'] in options_converters:
                options_converters[setting['ly_type']](setting, m_staffdef)

    layer_n = 1
    for l_layer in l_measure['measure']['layers']:
        if l_layer['ly_type'] == 'layer':
            # might also be 'barcheck' which is useless
            do_layer(l_layer, m_measure, layer_n)
            layer_n += 1

    return m_measure


def do_layer(l_layer, m_measure, layer_n):
    '''
    :param dict l_layer: A LilyPond layer from the parser.
    :param m_measure: An MEI ``<measure>`` element to put this layer into.
    :type m_measure: :class:`lxml.etree.Element`
    :param int layer_n: The @n value for this ``<layer>``.
    '''
    assert l_layer['ly_type'] == 'layer'

    m_layer = etree.SubElement(m_measure, mei.LAYER, {'n': str(layer_n)})

    node_converters = {
        'chord': do_chord,
        'note': do_note,
        'rest': do_rest,
        'spacer': do_spacer,
    }

    for obj in l_layer['layer']:
        if obj['ly_type'] in node_converters:
            node_converters[obj['ly_type']](obj, m_layer)

        else:
            raise RuntimeError()

    return m_layer


@log.wrap('debug', 'add octave', 'action')
def process_octave(l_oct, action):
    '''
    Convert an octave specifier from the parsed LilyPond into an MEI @oct attribute.

    :param str l_oct: The "octave" part of the LilyPond note as provided by Grako. May also be ``None``.
    :returns: The LMEI octave number.
    :rtype: str

    If the octave is not recognized, :func:`process_octave` emits a failure log message and returns
    the same value as if ``l_oct`` were ``None``.
    '''
    if l_oct in _OCTAVE_MAPPING:
        return _OCTAVE_MAPPING[l_oct]
    else:
        action.failure('unknown octave: {octave}', octave=l_oct)
        return _OCTAVE_MAPPING[None]


@log.wrap('debug', 'add accidental', 'action')
def process_accidental(l_accid, attrib, action):
    '''
    Add an accidental to the LMEI note, if required.

    :param l_accid: The LilyPond accidental as provided by Grako.
    :type l_accid: list of str
    :param dict attrib: The attributes for the MEI <note/> element *before* creation.
    :returns: The ``attrib`` argument.

    If the accidental is not recognized, :func:`process_accidental` emits a failure log message and
    returns the ``attrib`` argument unchanged.
    '''
    if l_accid:
        l_accid = ''.join(l_accid)
        if l_accid in _ACCIDENTAL_MAPPING:
            attrib['accid.ges'] = _ACCIDENTAL_MAPPING[l_accid]
        else:
            action.failure('unknown accidental: {accid}', accid=l_accid)

    return attrib


@log.wrap('debug', 'add forced accidental', 'action')
def process_forced_accid(l_note, attrib, action):
    '''
    Add a forced accidental to the LMEI note, if required.

    :param dict l_note: The LilyPond note from Grako.
    :param dict attrib: The attributes for the MEI <note/> element *before* creation.
    :returns: The ``attrib`` argument.
    '''
    if l_note['accid_force'] == '!':
        if 'accid.ges' in attrib:
            attrib['accid'] = attrib['accid.ges']
        else:
            # show a natural
            attrib['accid'] = 'n'

    return attrib


@log.wrap('debug', 'add cautionary accidental', 'action')
def process_caut_accid(l_note, m_note, action):
    '''
    Add a cautionary accidental to the LMEI note, if required.

    :param dict l_note: The LilyPond note from Grako.
    :param m_note: The MEI <note/> element.
    :type m_note: :class:`lxml.etree.Element`
    :returns: The ``m_note`` argument.
    '''
    if l_note['accid_force'] == '?':
        if m_note.get('accid.ges') is not None:
            attribs = {'accid': m_note.get('accid.ges'), 'func': 'caution'}
        else:
            # show a natural
            attribs = {'accid': 'n', 'func': 'caution'}
        etree.SubElement(m_note, mei.ACCID, attribs)

    return m_note


@log.wrap('debug', 'process dots', 'action')
def process_dots(l_node, attrib, action):
    """
    Handle the @dots attribute for a chord, note, rest, or spacer rest.

    :param dict l_node: The LilyPond node from Grako.
    :param dict attrib: The attribute dictionary that will be given to the :class:`Element` constructor.
    :returns: The ``attrib`` dictionary.

    Converts the "dots" member of ``l_node`` to the appropriate number in ``attrib``. If there is
    no "dots" member in ``l_node``, submit a "failure" log message and assume there are no dots.
    """
    if 'dots' in l_node:
        if l_node['dots']:
            attrib['dots'] = str(len(l_node['dots']))
    else:
        action.failure("missing 'dots' in the LilyPond node")

    return attrib


@log.wrap('debug', 'convert chord', 'action')
def do_chord(l_chord, m_layer, action):
    """
    Convert a LilyPond chord to an LMEI <chord/>.

    :param dict l_chord: The LilyPond chord from Grako.
    :param m_layer: The MEI <layer> that will hold the chord.
    :type m_layer: :class:`lxml.etree.Element`
    :returns: The new <chord/> element.
    :rtype: :class:`lxml.etree.Element`
    :raises: :exc:`exceptions.LilyPondError` if ``l_chord`` does not contain a Grako chord
    """
    check(l_chord['ly_type'] == 'chord', 'did not receive a chord')

    attrib = {'dur': l_chord['dur']}
    process_dots(l_chord, attrib)

    m_chord = etree.SubElement(m_layer, mei.CHORD, attrib)

    for l_note in l_chord['notes']:
        attrib = {
            'pname': l_note['pname'],
            'oct': process_octave(l_note['oct']),
        }

        process_accidental(l_note['accid'], attrib)
        process_forced_accid(l_note, attrib)

        m_note = etree.SubElement(m_chord, mei.NOTE, attrib)

        process_caut_accid(l_note, m_note)

    return m_chord


@log.wrap('debug', 'convert note', 'action')
def do_note(l_note, m_layer, action):
    """
    Convert a LilyPond note to an LMEI <note/>.

    :param dict l_note: The LilyPond note from Grako.
    :param m_layer: The MEI <layer> that will hold the note.
    :type m_layer: :class:`lxml.etree.Element`
    :returns: The new <note/> element.
    :rtype: :class:`lxml.etree.Element`
    :raises: :exc:`exceptions.LilyPondError` if ``l_note`` does not contain a Grako note
    """
    check(l_note['ly_type'] == 'note', 'did not receive a note')

    attrib = {
        'pname': l_note['pname'],
        'dur': l_note['dur'],
        'oct': process_octave(l_note['oct']),
    }

    process_accidental(l_note['accid'], attrib)
    process_forced_accid(l_note, attrib)
    process_dots(l_note, attrib)

    m_note = etree.SubElement(m_layer, mei.NOTE, attrib)

    process_caut_accid(l_note, m_note)

    return m_note


@log.wrap('debug', 'convert rest', 'action')
def do_rest(l_rest, m_layer, action):
    """
    Convert a LilyPond rest to an LMEI <rest/>.

    :param dict l_rest: The LilyPond rest from Grako.
    :param m_layer: The LMEI <layer> that will hold the rest.
    :type m_layer: :class:`lxml.etree.Element`
    :returns: The new <rest/> element.
    :rtype: :class:`lxml.etree.Element`
    :raises: :exc:`exceptions.LilyPondError` if ``l_rest`` does not contain a Grako rest
    """
    check(l_rest['ly_type'] == 'rest', 'did not receive a rest')

    attrib = {
        'dur': l_rest['dur'],
    }

    process_dots(l_rest, attrib)

    m_rest = etree.SubElement(m_layer, mei.REST, attrib)

    return m_rest


@log.wrap('debug', 'convert spacer', 'action')
def do_spacer(l_spacer, m_layer, action):
    """
    Convert a LilyPond spacer rest to an LMEI <space/>.

    :param dict l_spacer: The LilyPond spacer rest from Grako.
    :param m_layer: The LMEI <layer> that will hold the space.
    :type m_layer: :class:`lxml.etree.Element`
    :returns: The new <space/> element.
    :rtype: :class:`lxml.etree.Element`
    :raises: :exc:`exceptions.LilyPondError` if ``l_spacer`` does not contain a Grako spacer rest
    """
    check(l_spacer['ly_type'] == 'spacer', 'did not receive a spacer rest')

    attrib = {
        'dur': l_spacer['dur'],
    }

    process_dots(l_spacer, attrib)

    m_space = etree.SubElement(m_layer, mei.SPACE, attrib)

    return m_space
