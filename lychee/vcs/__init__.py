#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/vcs/__init__.py
# Purpose:                Initialize the "vcs" module.
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
Initialize the :mod:`vcs` module.
'''

from lychee.signals import vcs


def document_processor(**kwargs):
    vcs.STARTED.emit()
    print('{}.document_processor()'.format(__name__, kwargs))
    #vcs.ERROR.emit()
    vcs.FINISH.emit()
    print('{}.document_processor() after finish signal'.format(__name__))


vcs.START.connect(document_processor)
