#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/ly_to_mei.py
# Purpose:                Converts a LilyPond document to an MEI document.
#
# Copyright (C) 2015 Christopher Antila
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
Converts a LilyPond document to an MEI document.

At the moment, this file works on a series of space-separated notes---nothing else. For example, the
following LilyPond markup:::

    a4( b'16 c,,2)

produces something like this MEI markup:::

    <layer>
        <note dur="4" oct="3" pname="A" slur="i1" xml:id="4da1e537" />
        <note dur="16" oct="4" pname="B" xml:id="839fecca" />
        <note dur="2" oct="1" pname="C" slur="t1" xml:id="d4f1fda1" />
        <slur startid="#4da1e537" endid="#d4f1fda1" plist="#4da1e537 #839fecca #d4f1fda1"/>
    </layer>

Syntax Whitelist
===========================
This is a list of the currently-allowed syntax. If something does not appear on this list, it is
not picked up by the ``ly2mei`` program. The ``sillytest.ly`` file should use all the features at
least once.

    - [a..g] letter names for pitch (i.e., do not use rests, measure rests, or spaces)
    - explicit accidental display (i.e., the ``!`` and ``?`` characters after a pitch)
    - absolute octave entry (i.e., do not use ``\relative``)
    - durations specified on every note including 1, 2, 4, 8, 16, 32, 64, ... (not ``\longa`` etc.
        or dotted durations)
    - slurs *within a single measure*
    - multiple measures separated by ``|`` (including trailing bar-check)
    - clefs, except with octavation numbers, specifically the following varieties: treble, bass,
        alto, tenor, french, soprano, mezzosoprano, baritone, varbaritone, subbass, and percussion
'''

import random
import string
import sys

import six
from six.moves import range
from lxml import etree

from lychee.signals import inbound

_XMLNS = '{http://www.w3.org/XML/1998/namespace}'
_XMLID = '{}id'.format(_XMLNS)
_MEINS = '{http://www.music-encoding.org/ns/mei}'

_VALID_NOTE_LETTERS = {'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e', 'f': 'f', 'g': 'g',
                       'r': 'rest', 'R': 'REST', 's': 'space'}
_VALID_ACCIDENTALS = {'is': 's', 'es': 'f', 'isis': 'ss', 'eses': 'ff'}
LETTERS_AND_DIGITS = string.ascii_letters + string.digits

# Error Messages
_PITCH_CLASS_ERROR = 'Cannot decode pitch class: {}'
_SLUR_OPEN_WARNING = 'Slur already open in "{}"'

# register the 'mei' namespace
etree.register_namespace('mei', _MEINS[1:-1])


def convert(document, **kwargs):
    '''
    Convert a LilyPond document into an MEI document. This is the entry point for Lychee conversions.

    :param str document: The LilyPond document.
    :returns: The corresponding MEI document.
    :rtype: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    '''
    inbound.CONVERSION_STARTED.emit()

    measures = []
    for i, each_measure in enumerate(document.split('|')):
        elem = do_measure(each_measure)
        if elem is not None:
            elem.set('n', str(i + 1))
            measures.append(elem)

    # work everything into a <staff>
    staff = etree.Element('{}staff'.format(_MEINS), {'n': '1', _XMLID: make_id(32)})
    [staff.append(x) for x in measures]

    # make a <staffDef>
    scoreDef = etree.Element('{}scoreDef'.format(_MEINS))
    staffGrp = etree.Element('{}staffGrp'.format(_MEINS), attrib={'symbol': 'line'})
    staffDef = etree.Element('{}staffDef'.format(_MEINS), attrib={'n': '1', 'lines': '5'})
    staffGrp.append(staffDef)
    scoreDef.append(staffGrp)

    # put the first clef in the <staffDef> so it's cleaner
    first_clef = staff.find('.//{}clef'.format(_MEINS))
    staffDef.set('clef.shape', first_clef.get('shape'))
    staffDef.set('clef.line', first_clef.get('line'))
    # and remove that <clef> so it won't appear any more
    first_clef.getparent().remove(first_clef)

    # work everything into a <section>
    section = etree.Element('{}section'.format(_MEINS))
    section.append(scoreDef)
    section.append(staff)

    inbound.CONVERSION_FINISH.emit(converted=section)

def make_id(length=None):
    '''
    Generate a string with length characters, pseudorandomly chosen from capital and lowercase
    letters and numbers.

    :param int length: Optional number of characters in the generated string. Default is 7.
    :returns: A string with characters.
    :rtype: str
    '''
    if not length:
        length = 7
    post = [None] * length
    for i in range(length):
        post[i] = LETTERS_AND_DIGITS[random.randrange(0, len(LETTERS_AND_DIGITS))]
    return ''.join(post)

def find_lowest_of(here, these):
    """
    Finds the lowest (left-most) offset at which any of ``these`` appears in ``here``.

    **Examples**

    >>> find_lowest_of('hollaback', ['a', 'b', 'c'])
    4
    """
    for i, letter in enumerate(here):
        if letter in these:
            return i


def do_pitch_class(markup):
    """
    Given the part of a LilyPond note that includes the pitch class specification, find it. Rests
    and spacers also work, but note the return type below.

    :returns: A tuple indicating the required values for the @pname and @accid.ges attributes,
        respectively. If element 0 is ``'rest'``, ``'REST'``, or ``'space'``, it shall correspond
        to the <rest>, <mRest>, and <space> elements, respectively.
    :rtype: 2-tuple of str

    :raises: :exc:`RuntimeError` if the pitch class cannot be determined.

    **Examples**

    Usual pitch classes:

    >>> do_pitch_class('f')
    ('F', None)
    >>> do_pitch_class('fis')
    ('F', 's')
    >>> do_pitch_class('deses')
    ('D', 'ff')
    >>> do_pitch_class('es')
    ('E', 'f')

    Rests and spacers:

    >>> do_pitch_class('r')
    'rest', None
    >>> do_pitch_class('R')
    'REST', None
    >>> do_pitch_class('s')
    'space', None
    """

    if 1 == len(markup):
        if markup in _VALID_NOTE_LETTERS:
            return _VALID_NOTE_LETTERS[markup], None
        else:
            raise RuntimeError(_PITCH_CLASS_ERROR.format(markup))
    else:
        letter = do_pitch_class(markup[0])[0]
        accid = markup[1:]
        if 's' == accid and ('a' == letter or 'e' == letter):
            return letter, 's'
        elif accid in _VALID_ACCIDENTALS:
            return letter, _VALID_ACCIDENTALS[accid]
        else:
            raise RuntimeError(_PITCH_CLASS_ERROR.format(markup))


def do_note_block(markup):
    """
    Convert a "block" with a note and its related objects (articulations, dynamics, etc.).

    .. note:: You can figure out what to do for slurs based on the @slur attribute. If it's ``'i1'``
        or ``'t1'`` that means to start or end a slur, respectively. If it's ``'i2'`` or ``'t2'``
        it's for a phrasing slur.
    """
    PITCH_ENDERS =(',', "'", '1', '2', '4', '8', '!', '?')
    # figure out @pname and @accid.ges
    pname, accid_ges = do_pitch_class(markup[:find_lowest_of(markup, PITCH_ENDERS)])

    octave = 3
    stopped_at = 0
    accid = None  # may be None, a string for @accid, or an Element for <accid>

    # figure out @oct and @accid
    for i in range(1, len(markup)):
        each_char = markup[i]
        if each_char.isdigit():
            stopped_at = i
            break
        elif ',' == each_char:
            octave -= 1
        elif "'" == each_char:
            octave += 1
        elif '!' == each_char:
            accid = accid_ges if accid_ges is not None else 'n'
        elif '?' == each_char:
            accid = etree.Element('{}accid'.format(_MEINS), {'func': 'caution'})
            accid.set('accid', accid_ges if accid_ges is not None else 'n')
        else:
            pass  # TODO: panic

    # figure out @dur
    dur = ''
    for i in range(stopped_at, len(markup)):
        each_char = markup[i]
        if each_char.isdigit():
            dur += each_char
        else:
            stopped_at = i
            break

    # make the <note> element
    the_elem = etree.Element('{}note'.format(_MEINS),
                             {'pname': pname, 'dur': dur, 'oct': str(octave),
                              _XMLID: make_id(32)})

    # set @accid.ges and @accid, as required
    if accid_ges is not None:
        the_elem.set('accid.ges', accid_ges)
    if accid is not None:
        if isinstance(accid, six.string_types):
            the_elem.set('accid', accid)
        else:
            the_elem.append(accid)

    # figure out a slur
    if '(' in markup:
        the_elem.set('slur', 'i1')
    elif ')' in markup:
        the_elem.set('slur', 't1')

    return the_elem


def do_clef(markup):
    """
    Given the specification for a clef, return a <clef> element.

    ** Examples: **
    >>> do_clef('treble')
    <clef line="2" shape="G"/>
    >>> do_clef('"treble_8"')
    <clef line="2" shape="G" oct="3"/>
    """

    markup = markup.replace('"', '')

    # set the @shape and @line attributes
    if markup.startswith('treble') or markup.startswith('french'):
        shape = 'G'
        CLEF_LINES = {'french': '1', 'treble': '2'}
        line = CLEF_LINES[markup]
    elif markup.startswith('bass') or markup.startswith('varbaritone') or markup.startswith('subbass'):
        shape = 'F'
        CLEF_LINES = {'bass': '4', 'varbaritone': '3', 'subbass': '5'}
        line = CLEF_LINES[markup]
    elif markup.startswith('percussion'):
        shape = 'perc'
        line = '3'
    else:
        shape = 'C'
        CLEF_LINES = {'soprano': '1', 'mezzosoprano': '2', 'alto': '3', 'tenor': '4', 'baritone': '5'}
        line = CLEF_LINES[markup]

    elem = etree.Element('{}clef'.format(_MEINS), {'shape': shape, 'line': line})

    # set the @dis and @dis.place attributes
    # TODO: the "^8"-type things won't work yet because they clog up the dicts above
    if '^' in markup:
        elem.set('dis.place', 'above')
        elem.set('dis', markup[markup.find('^'):])
    elif '_' in markup:
        elem.set('dis.place', 'below')
        elem.set('dis', markup[markup.find('_'):])

    return elem


def do_measure(markup):
    """
    Process all the stuff in a single measure.

    (This is for a LilyPond measure, where there may be multiple voices, but [normally!] one staff).
    """
    list_of_elems = []
    slur_active = None
    markups = markup.split()
    for i, each_note in enumerate(markups):
        if each_note[0] in _VALID_NOTE_LETTERS:
            elem = do_note_block(each_note)
        elif '\clef' == each_note:
            elem = do_clef(markups[i + 1])
        list_of_elems.append(elem)

        if 'i1' == elem.get('slur'):
            if slur_active is not None:
                # previous slur wasn't closed
                raise RuntimeWarning(_SLUR_OPEN_WARNING.format(markup.strip()))
            else:
                slur_active = etree.Element('{}slur'.format(_MEINS),
                                            {'startid': '#{}'.format(elem.get(_XMLID)),
                                             _XMLID: make_id(32)})
        elif 't1' == elem.get('slur'.format(_MEINS)):
            slur_active.set('endid', '#{}'.format(elem.get(_XMLID)))
            list_of_elems.append(slur_active)
            slur_active = None

    if 0 == len(list_of_elems):
        # if the measure was somehow empty
        return None

    # NOTE: this is a bit of a lie for now, just to make it work
    # TODO: adjust @n for the voice number
    layer = etree.Element('{}layer'.format(_MEINS), {'n': '1', _XMLID: make_id(32)})
    [layer.append(x) for x in list_of_elems]
    measure = etree.Element('{}measure'.format(_MEINS), {'n': '1', _XMLID: make_id(32)})
    measure.append(layer)

    return measure
