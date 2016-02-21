#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/lmei_to_verovio.py
# Purpose:                Converts a Lychee-MEI document to special MEI that Verovio will accept.
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
Converts a Lychee-MEI document to special MEI that Verovio will accept.

This module runs the same conversions as :mod:`lmei_to_mei`, and makes the following two changes:

#. Convert the document to a string with an XML declaration that uses double quotes. Note that,
   although the XML declaration is not strictly required, and although it may use single quote
   marks around the attribute values, Verovio will not accept such a document.
#. Remove the "mei:" namespace from all tag names. In proper XML, such tag namespaces *may* be
   omitted in some situations, but Verovio again will not attempt to parse an MEI document where
   this is not the situation.

These limitations in Verovio likely arise from the "pugixml" library. They are trivial enough, and
do not require breaking conformance with XML, so we'll just work with what we have.
'''

# NOTE: tests for this module are held in "test_lmei_to_mei.py"

from lxml import etree

import lychee
from lychee.converters import lmei_to_mei
from lychee.namespaces import mei
from lychee.signals import outbound


_ERR_INPUT_NOT_SECTION = 'LMEI-to-Verovio did not receive a <section>'
_XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>'


def convert(document, **kwargs):
    '''
    Convert a Lychee-MEI document into a Verovio-compliant MEI document.

    :param document: The Lychee-MEI document.
    :type document: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding Verovio-compliant MEI document.
    :rtype: unicode
    '''
    outbound.CONVERSION_STARTED.emit()
    lychee.log('{}.convert(document={})'.format(__name__, document))

    if not isinstance(document, etree._Element) or mei.SECTION != document.tag:
        outbound.CONVERSION_ERROR.emit(msg=_ERR_INPUT_NOT_SECTION)
        return

    outbound.CONVERSION_FINISH.emit(converted=export_for_verovio(document))
    lychee.log('{}.convert() after finish signal'.format(__name__))


def export_for_verovio(document):
    '''
    Run the LMEI-to-MEI conversion, then export to a string with XML declaration, and remove the
    "mei:" namespacing in all the tags.

    :param document: The LMEI document to convert to a Verovio-compliant XML string.
    :type document: :class:`xml.etree.ElementTree.Element`
    :returns: A string for Verovio.
    :rtype: unicode
    '''
    document = lmei_to_mei.wrap_section_element(lmei_to_mei.change_measure_hierarchy(document))
    document = etree.tostring(document, encoding=unicode)
    document = document.replace('mei:', '')
    document = _XML_DECLARATION + document
    return document
