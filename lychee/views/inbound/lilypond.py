#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/views/inbound/lilypond.py
# Purpose:                Inbound views processing for LilyPond.
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
Inbound views processing for LilyPond.
'''

import json
import os.path
import random

import lychee
from lychee.namespaces import mei, xml
from lychee import signals


# translatable strings
# error messages
_GENERIC_ERROR = 'Unexpected error during inbound views: {0}'


def place_view(converted, document, session, **kwargs):
    '''
    Do the inbound views processing for Abjad (place the external view into the full document).

    Arguments as per :const:`lychee.signals.inbound.VIEWS_START`.
    '''
    signals.inbound.VIEWS_STARTED.emit()
    try:
        section_id = kwargs['views_info'] if 'views_info' in kwargs else None
        post = _place_view(converted, document, session, section_id)
    except Exception as exc:
        if lychee.DEBUG:
            raise
        else:
            signals.inbound.VIEWS_ERROR.emit(msg=_GENERIC_ERROR.format(repr(exc)))
    else:
        signals.inbound.VIEWS_FINISH.emit(views_info=post)


def _place_view(converted, document, session, section_id):
    '''
    Do the actual work for :func:`place_view`. That is a public wrapper function for error handling,
    and this is a private function with easier testing.
    '''
    if converted.tag != mei.SECTION:
        raise NotImplementedError('LilyPond inbound views must receive a <section>')

    xmlid = section_id if section_id else 'Sme-s-m-l-e{}'.format(_seven_digits())
    converted.set(xml.ID, xmlid)

    for staff in converted.iter(tag=mei.STAFF):
        _add_ids_staff(staff, xmlid)

    return xmlid


def _seven_digits():  # NB: copied from lychee.document
    '''
    Produce a string of seven pseudo-random digits.

    :returns: A string with seven pseudo-random digits.
    :rtype: str

    .. note:: The first character will never be 0, so you can rely on the output from this function
        being greater than or equal to one million, and strictly less than ten million.
    '''
    digits = '1234567890'
    len_digits = len(digits)
    post = [None] * 7
    for i in range(7):
        post[i] = digits[random.randrange(0, len_digits)]
    post = ''.join(post)

    if post[0] == '0':
        return _seven_digits()
    else:
        return post


def _add_ids_staff(staff, sect_id):
    # - get a <staff> and make its xmlid
    # - iterate all the children:
    #   - if measure, call _add_ids_to_measure()
    #   - else make its xmlid
    sect_digits = sect_id[-7:]
    staff_digits = None

    staff_digits = _seven_digits()
    xmlid = 'S{0}-sme-m-l-e{1}'.format(sect_digits, staff_digits)
    staff.set(xml.ID, xmlid)

    for child in staff.iterchildren():
        if child.tag == mei.MEASURE:
            _add_ids_measure(child, sect_id, xmlid)
        else:
            xmlid = 'S{0}-s{1}-m-l-e{2}'.format(sect_digits, staff_digits, _seven_digits())
            child.set(xml.ID, xmlid)


def _add_ids_measure(meas, sect_id, staff_id):
    # - get a <measure> and make its xmlid
    # - iterate all the children:
    #   - if layer, call _add_ids_to_layer()
    #   - else make its xmlid
    sect_digits = sect_id[-7:]
    staff_digits = staff_id[-7:]
    meas_digits = None

    meas_digits = _seven_digits()
    xmlid = 'S{0}-s{1}-mme-l-e{2}'.format(sect_digits, staff_digits, meas_digits)
    meas.set(xml.ID, xmlid)

    for child in meas.iterchildren():
        if child.tag == mei.LAYER:
            _add_ids_layer(child, sect_id, staff_id, xmlid)
        else:
            xmlid = 'S{0}-s{1}-m{2}-l-e{3}'.format(sect_digits, staff_digits, meas_digits, _seven_digits())
            child.set(xml.ID, xmlid)


def _add_ids_layer(layer, sect_id, staff_id, meas_id):
    # - get a <layer> and make its xmlid
    # - iterate all the children:
    #   - call _add_ids_to_layer()
    sect_digits = sect_id[-7:]
    staff_digits = staff_id[-7:]
    meas_digits = meas_id[-7:]
    layer_digits = None

    layer_digits = _seven_digits()
    xmlid = 'S{0}-s{1}-m{2}-lme-e{3}'.format(sect_digits, staff_digits, meas_digits, layer_digits)
    layer.set(xml.ID, xmlid)

    for child in layer.iterchildren():
        _add_ids_element(child, sect_id, staff_id, meas_id, xmlid)


def _add_ids_element(elem, sect_id, staff_id, meas_id, layer_id):
    sect_digits = sect_id[-7:]
    staff_digits = staff_id[-7:]
    meas_digits = meas_id[-7:]
    layer_digits = layer_id[-7:]

    xmlid = 'S{0}-s{1}-m{2}-l{3}-e{4}'.format(sect_digits, staff_digits, meas_digits, layer_digits, _seven_digits())
    elem.set(xml.ID, xmlid)
