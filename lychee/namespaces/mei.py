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

# namespace
MEINS = '{http://www.music-encoding.org/ns/mei}'

# tag names
ARRANGER = '{}arranger'.format(MEINS)
AUDIENCE = '{}audience'.format(MEINS)
AUTHOR = '{}author'.format(MEINS)
BODY = '{}body'.format(MEINS)
CLASSIFICATION = '{}classification'.format(MEINS)
COMPOSER = '{}composer'.format(MEINS)
CONTENTS = '{}contents'.format(MEINS)
CONTEXT = '{}context'.format(MEINS)
EDITOR = '{}editor'.format(MEINS)
FILE_DESC = '{}fileDesc'.format(MEINS)
FUNDER = '{}funder'.format(MEINS)
HISTORY = '{}history'.format(MEINS)
KEY = '{}key'.format(MEINS)
LANG_USAGE = '{}langUsage'.format(MEINS)
LIBRETTIST = '{}librettist'.format(MEINS)
LYRICIST = '{}lyricist'.format(MEINS)
MDIV = '{}mdiv'.format(MEINS)
MEASURE = '{}measure'.format(MEINS)
MEI = '{}mei'.format(MEINS)
MEI_CORPUS = '{}meiCorpus'.format(MEINS)
MEI_HEAD = '{}meiHead'.format(MEINS)
MENSURATION = '{}mensuration'.format(MEINS)
METER = '{}meter'.format(MEINS)
MUSIC = '{}music'.format(MEINS)
NAME = '{}name'.format(MEINS)
NOTES_STMT = '{}notesStmt'.format(MEINS)
PERF_MEDIUM = '{}perfMedium'.format(MEINS)
PERS_NAME = '{}persName'.format(MEINS)
PTR = '{}ptr'.format(MEINS)
PUB_STMT = '{}pubStmt'.format(MEINS)
RESP_STMT = '{}respStmt'.format(MEINS)
REVISION_DESC = '{}revisionDesc'.format(MEINS)
SCORE = '{}score'.format(MEINS)
SCORE_DEF = '{}scoreDef'.format(MEINS)
SECTION = '{}section'.format(MEINS)
SPONSOR = '{}sponsor'.format(MEINS)
STAFF = '{}staff'.format(MEINS)
STAFF_DEF = '{}staffDef'.format(MEINS)
STAFF_GRP = '{}staffGrp'.format(MEINS)
TITLE = '{}title'.format(MEINS)
TITLE_STMT = '{}titleStmt'.format(MEINS)
UNPUB = '{}unpub'.format(MEINS)
WORK_DESC = '{}workDesc'.format(MEINS)
WORK = '{}work'.format(MEINS)

# attribute names
