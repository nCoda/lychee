#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               scripts/helper_utils.py
# Purpose:                Utilities for helper scripts.
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
Provides convenience functions to reduce code duplication in conversion helper scripts.
'''
import argparse
import sys


def add_infile_and_outfile(
        parser,
        input_file_type='',
        output_file_type='',
        ):

    # Don't use argparse.FileType. It leaves file pointers open.

    parser.add_argument(
        'infile',
        type=str,
        help='Input {0} file name.'.format(input_file_type),
        )

    parser.add_argument(
        'outfile',
        type=str,
        nargs='?',
        default=None,
        help='Output {0} file name. Defaults to stdout.'.format(output_file_type),
        )


def process_infile_and_outfile(core_function, input_file_name, output_file_name):

    def run(input_file, output_file):
        input_string = input_file.read()
        output_string = core_function(input_string)
        output_file.write(output_string)

    with open(input_file_name, 'r') as input_file:
        if output_file_name is None:
            run(input_file, sys.stdout)
            sys.stdout.flush()
        else:
            with open(output_file_name, 'w') as output_file:
                run(input_file, output_file)


def run_conversion_helper_script(
        core_function,
        description='',
        input_file_type='',
        output_file_type='',
        ):

    parser = argparse.ArgumentParser(description=description)

    add_infile_and_outfile(
        parser,
        input_file_type=input_file_type,
        output_file_type=output_file_type
        )

    args = parser.parse_args()

    process_infile_and_outfile(core_function, args.infile, args.outfile)