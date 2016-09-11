#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/utils/elements_equal.py
# Purpose:                Tests for equality of two lxml objects.
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
Tests for equality of two lxml objects.
'''
from lychee.namespaces import lychee as lyns
from lychee.namespaces import xml as xmlns


def elements_equal(first, second):
    '''
    Type-specific equality function for :class:`lxml.etree.Element` and
    :class:`lxml.etree.ElementTree` objects. Ignores xml:id attributes.
    '''
    first_list = [x for x in first.iter()]
    second_list = [x for x in second.iter()]
    if len(first_list) != len(second_list):
        # different number of children
        return False
    for i in range(len(first_list)):
        if first_list[i].tag != second_list[i].tag:
            # tags don't match
            return False
        first_keys = [x for x in first_list[i].keys() if x != xmlns.ID]
        second_keys = [x for x in second_list[i].keys() if x != xmlns.ID]
        if len(first_keys) != len(second_keys):
            # different number of attributes
            return False
        for key in first_keys:
            if key == lyns.VERSION:
                if first_list[i].get(key) is None:
                    return False
                if second_list[i].get(key) is None:
                    return False
            else:
                if first_list[i].get(key) != second_list[i].get(key):
                    # elements are not equal
                    return False
    return True
