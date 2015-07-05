#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/mei_to_abjad.py
# Purpose:                Converts an MEI document to an Abjad document.
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
Converts an MEI document to an Abjad document.
'''

from lychee.signals import outbound

def convert(**kwargs):
    '''
    Convert an MEI document into an Abjad document.

    :param document: The MEI document. Must be provided as a kwarg.
    :type document: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding MEI document.
    :rtype: object
    '''
    outbound.CONVERSION_STARTED.emit()
    print('{}.convert(document="{}")'.format(__name__, kwargs['document']))
    #outbound.CONVERSION_ERROR.emit()
    outbound.CONVERSION_FINISH.emit(converted='<Abjad stuff>')
    print('{}.convert() after finish signal'.format(__name__))
