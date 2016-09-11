#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               scripts/ly_to_lmei_to_ly.py
# Purpose:                Converts a LilyPond document to MEI and back.
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
Converts a LilyPond document to MEI and back.
'''

from lychee.converters.inbound import lilypond as inbound_lilypond
from lychee.converters.outbound import lilypond as outbound_lilypond


def ly_to_lmei_to_ly(lilypond_string):
    mei_thing = inbound_lilypond.convert(lilypond_string)
    converted_lilypond_string = outbound_lilypond.convert(mei_thing)
    return converted_lilypond_string


if __name__ == '__main__':
    from helper_utils import run_conversion_helper_script

    run_conversion_helper_script(
        core_function=ly_to_lmei_to_ly,
        description='Converts a LilyPond document to MEI and back.',
        input_file_type='LilyPond',
        output_file_type='LilyPond',
        )
