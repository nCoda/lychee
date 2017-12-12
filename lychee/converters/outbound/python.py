#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/python.py
# Purpose:                Converts a Lychee-MEI document to Python (an Abjad script).
#
# Copyright (C) 2017 Christopher Antila
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
#-------------------------------------------------------------------------
"""
Converts a Lychee-MEI document to Python (an Abjad script).

Currently this is a stub module that always returns an empty string.
"""

from lychee.logs import OUTBOUND_LOG as log


@log.wrap('info', 'convert LMEI to Python')
def convert(document, **kwargs):
    """
    Convert an MEI document into a Python (Abjad) script.

    :param document: The MEI document. Must be provided as a kwarg.
    :type document: :class:`xml.etree.ElementTree.Element` or
        :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding Python script.
    :rtype: str
    :raises: :exc:`lychee.exceptions.OutboundConversionError` when there is a forseeable error.
    """
    return ''
