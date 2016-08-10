#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/namespaces/xlink.py
# Purpose:                Constants for the "XLink" namespace.
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
Constants for the "XLink" namespace.
'''


from lxml import etree


# NOTE: please keep this list alphabetical!

XLINKNS = '{http://www.w3.org/1999/xlink}'
etree.register_namespace('xlink', XLINKNS[1:-1])

ACTUATE = '{}actuate'.format(XLINKNS)
'An XLink attribute name.'
SHOW = '{}show'.format(XLINKNS)
'An XLink attribute name.'
