#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/mei_to_lmei.py
# Purpose:                Converts a conventional MEI document to a Lychee-MEI document.
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
Converts a conventional MEI document to a Lychee-MEI document.
'''

import lychee
from lychee.signals import inbound

def convert(**kwargs):
    '''
    Convert an MEI document into a Lychee-MEI document.

    :param document: The MEI document. Must be provided as a kwarg.
    :type document: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding Lychee-MEI document.
    :rtype: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    '''
    inbound.CONVERSION_STARTED.emit()
    lychee.log('{}.convert(document="{}")'.format(__name__, kwargs['document']))
    #inbound.CONVERSION_ERROR.emit()
    inbound.CONVERSION_FINISH.emit(converted='<l-mei stuff>')
    lychee.log('{}.convert() after finish signal'.format(__name__))
