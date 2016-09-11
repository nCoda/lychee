#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               scripts/lmei_to_ly.py
# Purpose:                Converts an MEI document to a LilyPond document.
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
Converts an MEI document to a LilyPond document.
'''

from lxml import etree
from lychee.converters.outbound import lilypond


def lmei_to_ly(lmei_string):
    mei_thing = etree.fromstring(lmei_string)
    lilypond_string = lilypond.convert(mei_thing)
    return lilypond_string


if __name__ == '__main__':
    from helper_utils import run_conversion_helper_script

    run_conversion_helper_script(
        core_function=lmei_to_ly,
        description='Converts an MEI document to a LilyPond document.',
        input_file_type='LMEI',
        output_file_type='LilyPond',
        )
