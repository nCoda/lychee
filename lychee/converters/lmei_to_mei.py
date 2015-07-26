#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/lmei_to_mei.py
# Purpose:                Converts a Lychee-MEI document to a more conventional MEI document.
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
Converts a Lychee-MEI document to a more conventional document.
'''

from lxml import etree

import lychee
from lychee.signals import outbound


_MEINS = '{http://www.music-encoding.org/ns/mei}'


def convert(document, **kwargs):
    '''
    Convert a Lychee-MEI document into an MEI document.

    :param document: The Lychee-MEI document.
    :type document: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding MEI document.
    :rtype: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    '''
    outbound.CONVERSION_STARTED.emit()
    lychee.log('{}.convert(document={})'.format(__name__, document))

    if '{}section'.format(_MEINS) != document.tag:
        outbound.CONVERSION_ERROR.emit(msg='LMEI-to-MEI did not receive a <section>')
        return

    section = change_measure_hierarchy(document)

    score = etree.Element('{}score'.format(_MEINS))
    score.append(section)
    mdiv = etree.Element('{}mdiv'.format(_MEINS))
    mdiv.append(score)
    body = etree.Element('{}body'.format(_MEINS))
    body.append(mdiv)
    music = etree.Element('{}music'.format(_MEINS))
    music.append(body)
    mei = etree.Element('{}mei'.format(_MEINS))
    mei.append(music)

    outbound.CONVERSION_FINISH.emit(converted=mei)
    lychee.log('{}.convert() after finish signal'.format(__name__))


def change_measure_hierarchy(lmei_section):
    '''
    Convert a <section> with measure-within-staff hierarchy to staff-within-measure hierarchy. That
    represents a conversion from Lychee-MEI to standard MEI.

    :param lmei_section: The <section> to convert.
    :type lmei_section: :class:`xml.etree.ElementTree.Element`
    :returns: A converted <section>.
    :rtype: :class:`xml.etree.ElementTree.Element`
    '''

    section = etree.Element('{}section'.format(_MEINS))
    section.append(lmei_section.find('.//{}scoreDef'.format(_MEINS)))
    measure_num = 0
    ran_out_of_measures = False

    while not ran_out_of_measures:
        measure_num += 1
        xpath_query = './/{meins}measure[@n="{n}"]'.format(meins=_MEINS, n=measure_num)
        staffs = lmei_section.findall(xpath_query)

        if 0 == len(staffs):
            ran_out_of_measures = True
            continue

        measure = etree.Element('{}measure'.format(_MEINS), n=str(measure_num))

        for i, each in enumerate(staffs):
            each.tag = '{}staff'.format(_MEINS)
            each.set('n', str(i+1))
            measure.append(each)

        section.append(measure)

    return section
