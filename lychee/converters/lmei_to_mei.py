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
    print('{}.convert(document={})'.format(__name__, document))

    if '{}section'.format(_MEINS) != document.tag:
        outbound.CONVERSION_ERROR.emit(msg='LMEI-to-MEI did not receive a <section>')
        return

    scoreDef = etree.Element('{}scoreDef'.format(_MEINS))
    staffGrp = etree.Element('{}staffGrp'.format(_MEINS), attrib={'symbol': 'line'})
    staffDef = etree.Element('{}staffDef'.format(_MEINS), attrib={'n': '1', 'lines': '5'})
    staffGrp.append(staffDef)
    scoreDef.append(staffGrp)
    document.insert(0, scoreDef)

    score = etree.Element('{}score'.format(_MEINS))
    score.append(document)
    mdiv = etree.Element('{}mdiv'.format(_MEINS))
    mdiv.append(score)
    body = etree.Element('{}body'.format(_MEINS))
    body.append(mdiv)
    music = etree.Element('{}music'.format(_MEINS))
    music.append(body)
    mei = etree.Element('{}mei'.format(_MEINS))
    mei.append(music)

    outbound.CONVERSION_FINISH.emit(converted=mei)
    print('{}.convert() after finish signal'.format(__name__))
