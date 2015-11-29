#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/namespaces/mei.py
# Purpose:                Constants for the "MEI" XML namespace.
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
Constants for the "MEI" XML namespace.
'''


# NOTE: please keep this list alphabetical!

# namespace
MEINS = '{http://www.music-encoding.org/ns/mei}'

# tag names
BODY = '{}body'.format(MEINS)
MDIV = '{}mdiv'.format(MEINS)
MEASURE = '{}measure'.format(MEINS)
MEI = '{}mei'.format(MEINS)
MEI_CORPUS = '{}meiCorpus'.format(MEINS)
MEI_HEAD = '{}meiHead'.format(MEINS)
MUSIC = '{}music'.format(MEINS)
PTR = '{}ptr'.format(MEINS)
SCORE = '{}score'.format(MEINS)
SCORE_DEF = '{}scoreDef'.format(MEINS)
SECTION = '{}section'.format(MEINS)
STAFF = '{}staff'.format(MEINS)

# attribute names
