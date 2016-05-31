#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/abjad_to_lmei.py
# Purpose:                Converts an abjad document to an lmei document.
#
# Copyright (C) 2016 Jeffrey Treviño, Christopher Antila
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

from abjad.tools.abctools.AbjadObject import AbjadObject
import unittest

from lychee.namespaces import xml

#are the objects of the same class?
#if so, are their formatted strings equal?

SAME_CLASS_ERROR = 'Objects are not the same class ({0} and {1})'
STRING_FORMAT_ERROR = 'Object strings are not equal ("{0}" and "{1}")'


class AbjadTestCase(unittest.TestCase):

    def assertEqual(self, first, second, msg=None):
        if isinstance(first, AbjadObject):
            if type(first) != type(second):
                raise AssertionError(SAME_CLASS_ERROR.format(type(first), type(second)))
            elif format(first) != format(second):
                raise AssertionError(STRING_FORMAT_ERROR.format(first, second))
        else:
            super(AbjadTestCase, self).assertEqual(first, second, msg)

    def assertAttribsEqual(self, with_id_dict, without_id_dict):
        with_id_dict = dict(with_id_dict)
        without_id_dict = dict(without_id_dict)
        with_id_dict_xml_id = with_id_dict.get(xml.ID, None)
        without_id_dict_xml_id = without_id_dict.get(xml.ID, None)
        if isinstance(with_id_dict, dict):
            if type(with_id_dict) != type(without_id_dict):
                raise AssertionError(SAME_CLASS_ERROR)
        with_id_copy = with_id_dict.copy()
        if with_id_dict_xml_id:
            del(with_id_copy[xml.ID])
        self.assertEqual(with_id_copy, without_id_dict)
