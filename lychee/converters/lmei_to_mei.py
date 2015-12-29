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
from lychee.namespaces import mei
from lychee.signals import outbound

_ERR_INPUT_NOT_SECTION = 'LMEI-to-MEI did not receive a <section>'


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

    if not isinstance(document, etree._Element) or mei.SECTION != document.tag:
        outbound.CONVERSION_ERROR.emit(msg=_ERR_INPUT_NOT_SECTION)
        return

    outbound.CONVERSION_FINISH.emit(converted=wrap_section_element(change_measure_hierarchy(document)))
    lychee.log('{}.convert() after finish signal'.format(__name__))


def wrap_section_element(section):
    '''
    Wrap a <section> element in <score>, <mdiv>, <body>, <music>, and <mei> so that it can stand as
    an independent document.

    :param section: The <section> eleemnt to wrap.
    :type section: :class:`xml.etree.ElementTree.Element`
    :returns: The corresponding <mei> element.
    :rtype: :class:`xml.etree.ElementTree.Element`
    '''
    score = etree.Element(mei.SCORE)
    score.append(section)
    mdiv = etree.Element(mei.MDIV)
    mdiv.append(score)
    body = etree.Element(mei.BODY)
    body.append(mdiv)
    music = etree.Element(mei.MUSIC)
    music.append(body)
    post = etree.Element(mei.MEI)
    post.append(music)

    return post


def change_measure_hierarchy(lmei_section):
    '''
    Convert a <section> with measure-within-staff hierarchy to staff-within-measure hierarchy. That
    represents a conversion from Lychee-MEI to standard MEI.

    :param lmei_section: The <section> to convert.
    :type lmei_section: :class:`xml.etree.ElementTree.Element`
    :returns: A converted <section>.
    :rtype: :class:`xml.etree.ElementTree.Element`
    '''

    section = etree.Element(mei.SECTION)
    scoreDef = lmei_section.find('.//{}'.format(mei.SCORE_DEF))
    if scoreDef is not None:
        section.append(scoreDef)
    measure_num = 0
    still_have_measures = True

    while still_have_measures:
        measure_num += 1
        xpath_query = './/{tag}[@n="{n}"]'.format(tag=mei.MEASURE, n=measure_num)
        staffs = lmei_section.findall(xpath_query)

        if 0 == len(staffs):
            still_have_measures = False
            continue

        measure = etree.Element(mei.MEASURE, n=str(measure_num))

        for i, each in enumerate(staffs):
            each.tag = mei.STAFF
            each.set('n', str(i+1))
            measure.append(each)

        section.append(measure)

    return section
