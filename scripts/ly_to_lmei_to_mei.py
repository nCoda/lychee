#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               scripts/ly_to_lmei.py
# Purpose:                Converts a LilyPond document to an MEI document.
#
# Copyright (C) 2016 Nathan Ho
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
Converts a LilyPond document to an LMEI document and then to an MEI document.
'''

from lxml import etree
from lychee.converters.inbound import lilypond
from lychee.converters.outbound import mei


def ly_string_to_lmei_element(lilypond_string):
    lmei_element = lilypond.convert(lilypond_string)
    return lmei_element

def lmei_element_to_mei_string(lmei_element):
    mei_element = mei.create_measures(lmei_element)
    mei_string = etree.tostring(mei_element, pretty_print=True)
    return mei_string

def ly_string_to_mei_string(lilypond_string):
    lmei_element = lilypond.convert(lilypond_string)
    mei_string = lmei_element_to_mei_string(lmei_element)
    return mei_string


if __name__ == '__main__':
    from helper_utils import run_conversion_helper_script

    run_conversion_helper_script(
        core_function=ly_string_to_mei_string,
        description='Converts a LilyPond document to an LMEI and then an MEI document.',
        input_file_type='LilyPond',
        output_file_type='MEI',
        )
