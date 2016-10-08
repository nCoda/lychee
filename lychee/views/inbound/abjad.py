#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/views/inbound/abjad.py
# Purpose:                Inbound views processing for Abjad.
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
Inbound views processing for Abjad.
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


# temporary storage
# these mappings should be stored in the repository, held in memory only at runtime
_ids_atom = {}  # Abjad-to-LMEI @xml:id mapping
_ids_mtoa = {}  # LMEI-to-Abjad @xml:id mapping


def place_view(converted, document, session, **kwargs):
    '''
    Do the inbound views processing for Abjad (place the external view into the full document).

    Arguments as per :const:`lychee.signals.inbound.VIEWS_START`.
    '''
    signals.inbound.VIEWS_STARTED.emit()
    section_id = kwargs['views_info'] if 'views_info' in kwargs else None
    post = _place_view(converted, document, session, section_id)
    signals.inbound.VIEWS_FINISH.emit(views_info=post)


def _place_view(converted, document, session, section_id):
    '''
    Do the actual work for :func:`place_view`. That is a public wrapper function for error handling,
    and this is a private function with easier testing.
    '''
    global _ids_atom

    if converted.tag != mei.SECTION:
        raise NotImplementedError('Abjad inbound views must receive a <section>')

    path_to_atom_map = os.path.join(session.get_repo_dir(), 'atom_xmlids.json')
    if len(_ids_atom) == 0:
        if os.path.exists(path_to_atom_map):
            with open(path_to_atom_map, 'r') as thefile:
                _ids_atom = json.load(thefile)

    # TODO: load the "mtoa" map

    if section_id:
        converted.set(xml.ID, section_id)

    if converted.get(xml.ID) in _ids_atom:
        # It's not a new section.
        # Fetch the existing ID, set it on the <section>, then return the ID.
        xmlid = _ids_atom[converted.get(xml.ID)]
        converted.set(xml.ID, xmlid)

        for staff in converted.iter(tag=mei.STAFF):
            _ids_atom.update(_add_ids_staff(staff, _ids_atom, xmlid))

        # @xmlid values elsewhere in the tree may have changed
        with open(path_to_atom_map, 'w') as thefile:
            json.dump(_ids_atom, thefile)

        return xmlid

    else:
        print('The Abjad-given ID is {}'.format(converted.get(xml.ID)))
        # It's a new section.
        # Generate a new ID, set it in the mappings, set it on the <section>, then return the ID.
        xmlid = section_id if section_id else 'Sme-s-m-l-e{}'.format(_seven_digits())
        _ids_atom[converted.get(xml.ID)] = xmlid
        _ids_atom[xmlid] = converted.get(xml.ID)
        converted.set(xml.ID, xmlid)

        for staff in converted.iter(tag=mei.STAFF):
            _ids_atom.update(_add_ids_staff(staff, _ids_atom, xmlid))

        with open(path_to_atom_map, 'w') as thefile:
            json.dump(_ids_atom, thefile)

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


def _add_ids_staff(staff, id_map, sect_id):
    # - get a <staff> and make its xmlid
    # - iterate all the children:
    #   - if measure, call _add_ids_to_measure()
    #   - else make its xmlid
    sect_digits = sect_id[-7:]
    staff_digits = None

    if staff.get(xml.ID) in id_map:
        xmlid = id_map[staff.get(xml.ID)]
        staff_digits = xmlid[-7:]
        staff.set(xml.ID, xmlid)
    else:
        staff_digits = _seven_digits()
        xmlid = 'S{0}-sme-m-l-e{1}'.format(sect_digits, staff_digits)
        id_map[staff.get(xml.ID)] = xmlid
        staff.set(xml.ID, xmlid)

    for child in staff.iterchildren():
        if child.tag == mei.MEASURE:
            id_map.update(_add_ids_measure(child, id_map, sect_id, xmlid))
        elif child.get(xml.ID) in id_map:
            child.set(xml.ID, id_map[child.get(xml.ID)])
        else:
            xmlid = 'S{0}-s{1}-m-l-e{2}'.format(sect_digits, staff_digits, _seven_digits())
            id_map[child.get(xml.ID)] = xmlid
            child.set(xml.ID, xmlid)

    return id_map


def _add_ids_measure(meas, id_map, sect_id, staff_id):
    # - get a <measure> and make its xmlid
    # - iterate all the children:
    #   - if layer, call _add_ids_to_layer()
    #   - else make its xmlid
    sect_digits = sect_id[-7:]
    staff_digits = staff_id[-7:]
    meas_digits = None

    if meas.get(xml.ID) in id_map:
        xmlid = id_map[meas.get(xml.ID)]
        meas_digits = xmlid[-7:]
        meas.set(xml.ID, xmlid)
    else:
        meas_digits = _seven_digits()
        xmlid = 'S{0}-s{1}-mme-l-e{2}'.format(sect_digits, staff_digits, meas_digits)
        id_map[meas.get(xml.ID)] = xmlid
        meas.set(xml.ID, xmlid)

    for child in meas.iterchildren():
        if child.tag == mei.LAYER:
            id_map.update(_add_ids_layer(child, id_map, sect_id, staff_id, xmlid))
        elif child.get(xml.ID) in id_map:
            child.set(xml.ID, id_map[child.get(xml.ID)])
        else:
            xmlid = 'S{0}-s{1}-m{2}-l-e{3}'.format(sect_digits, staff_digits, meas_digits, _seven_digits())
            id_map[child.get(xml.ID)] = xmlid
            child.set(xml.ID, xmlid)

    return id_map


def _add_ids_layer(layer, id_map, sect_id, staff_id, meas_id):
    # - get a <layer> and make its xmlid
    # - iterate all the children:
    #   - call _add_ids_to_layer()
    sect_digits = sect_id[-7:]
    staff_digits = staff_id[-7:]
    meas_digits = meas_id[-7:]
    layer_digits = None

    if layer.get(xml.ID) in id_map:
        xmlid = id_map[layer.get(xml.ID)]
        layer_digits = xmlid[-7:]
        layer.set(xml.ID, xmlid)
    else:
        layer_digits = _seven_digits()
        xmlid = 'S{0}-s{1}-m{2}-lme-e{3}'.format(sect_digits, staff_digits, meas_digits, layer_digits)
        id_map[layer.get(xml.ID)] = xmlid
        layer.set(xml.ID, xmlid)

    for child in layer.iterchildren():
        id_map.update(_add_ids_element(child, id_map, sect_id, staff_id, meas_id, xmlid))

    return id_map


def _add_ids_element(elem, id_map, sect_id, staff_id, meas_id, layer_id):
    sect_digits = sect_id[-7:]
    staff_digits = staff_id[-7:]
    meas_digits = meas_id[-7:]
    layer_digits = layer_id[-7:]

    if elem.get(xml.ID) in id_map:
        elem.set(xml.ID, id_map[elem.get(xml.ID)])
    else:
        xmlid = 'S{0}-s{1}-m{2}-l{3}-e{4}'.format(sect_digits, staff_digits, meas_digits, layer_digits, _seven_digits())
        id_map[elem.get(xml.ID)] = xmlid
        elem.set(xml.ID, xmlid)

    return id_map
