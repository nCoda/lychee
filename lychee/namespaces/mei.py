#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/namespaces/mei.py
# Purpose:                Constants for the "MEI" XML namespace.
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
Constants for the "MEI" XML namespace.
'''

# NOTE: please keep this list alphabetical!
# NOTE: the weird string after each constant makes Sphinx show the constant in the API.

from lxml import etree


# namespace
MEINS = '{http://www.music-encoding.org/ns/mei}'
etree.register_namespace('mei', MEINS[1:-1])

# tag names
ACCID = '{}accid'.format(MEINS)
'An MEI tag name.'
ARRANGER = '{}arranger'.format(MEINS)
'An MEI tag name.'
AUDIENCE = '{}audience'.format(MEINS)
'An MEI tag name.'
AUTHOR = '{}author'.format(MEINS)
'An MEI tag name.'
BEAM = '{}beam'.format(MEINS)
'An MEI tag name.'
BEAM_SPAN = '{}beamSpan'.format(MEINS)
'An MEI tag name.'
BODY = '{}body'.format(MEINS)
'An MEI tag name.'
CHORD = '{}chord'.format(MEINS)
'An MEI tag name.'
CLASSIFICATION = '{}classification'.format(MEINS)
'An MEI tag name.'
COMPOSER = '{}composer'.format(MEINS)
'An MEI tag name.'
CONTENTS = '{}contents'.format(MEINS)
'An MEI tag name.'
CONTEXT = '{}context'.format(MEINS)
'An MEI tag name.'
EDITOR = '{}editor'.format(MEINS)
'An MEI tag name.'
FILE_DESC = '{}fileDesc'.format(MEINS)
'An MEI tag name.'
FUNDER = '{}funder'.format(MEINS)
'An MEI tag name.'
HISTORY = '{}history'.format(MEINS)
'An MEI tag name.'
KEY = '{}key'.format(MEINS)
'An MEI tag name.'
LANG_USAGE = '{}langUsage'.format(MEINS)
'An MEI tag name.'
LAYER = '{}layer'.format(MEINS)
'An MEI tag name.'
LIBRETTIST = '{}librettist'.format(MEINS)
'An MEI tag name.'
LYRICIST = '{}lyricist'.format(MEINS)
'An MEI tag name.'
MDIV = '{}mdiv'.format(MEINS)
'An MEI tag name.'
MEASURE = '{}measure'.format(MEINS)
'An MEI tag name.'
MEI = '{}mei'.format(MEINS)
'An MEI tag name.'
MEI_CORPUS = '{}meiCorpus'.format(MEINS)
'An MEI tag name.'
MEI_HEAD = '{}meiHead'.format(MEINS)
'An MEI tag name.'
M_REST = '{}mRest'.format(MEINS)
'An MEI tag name.'
MENSURATION = '{}mensuration'.format(MEINS)
'An MEI tag name.'
METER = '{}meter'.format(MEINS)
'An MEI tag name.'
MUSIC = '{}music'.format(MEINS)
'An MEI tag name.'
NAME = '{}name'.format(MEINS)
'An MEI tag name.'
NOTE = '{}note'.format(MEINS)
'An MEI tag name.'
NOTES_STMT = '{}notesStmt'.format(MEINS)
'An MEI tag name.'
PERF_MEDIUM = '{}perfMedium'.format(MEINS)
'An MEI tag name.'
PERS_NAME = '{}persName'.format(MEINS)
'An MEI tag name.'
PTR = '{}ptr'.format(MEINS)
'An MEI tag name.'
PUB_STMT = '{}pubStmt'.format(MEINS)
'An MEI tag name.'
RESP_STMT = '{}respStmt'.format(MEINS)
'An MEI tag name.'
REST = '{}rest'.format(MEINS)
'An MEI tag name.'
REVISION_DESC = '{}revisionDesc'.format(MEINS)
'An MEI tag name.'
SCORE = '{}score'.format(MEINS)
'An MEI tag name.'
SCORE_DEF = '{}scoreDef'.format(MEINS)
'An MEI tag name.'
SECTION = '{}section'.format(MEINS)
'An MEI tag name.'
SPACE = '{}space'.format(MEINS)
'An MEI tag name.'
SPONSOR = '{}sponsor'.format(MEINS)
'An MEI tag name.'
STAFF = '{}staff'.format(MEINS)
'An MEI tag name.'
STAFF_DEF = '{}staffDef'.format(MEINS)
'An MEI tag name.'
STAFF_GRP = '{}staffGrp'.format(MEINS)
'An MEI tag name.'
TITLE = '{}title'.format(MEINS)
'An MEI tag name.'
TITLE_STMT = '{}titleStmt'.format(MEINS)
'An MEI tag name.'
TUPLET_SPAN = '{}tupletSpan'.format(MEINS)
'An MEI tag name.'
UNPUB = '{}unpub'.format(MEINS)
'An MEI tag name.'
WORK_DESC = '{}workDesc'.format(MEINS)
'An MEI tag name.'
WORK = '{}work'.format(MEINS)
'An MEI tag name.'

# attribute names
