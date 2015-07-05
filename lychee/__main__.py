#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/__main__.py
# Purpose:                Module the runs Lychee as a program.
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
Module that runs Lychee as a program.
'''

from lychee import signals
from signals import outbound

# register these fake "listeners" that will pretend they want data in whatever formats
def generic_listener(dtype):
    #print("I'm listening for {}!".format(dtype))
    outbound.I_AM_LISTENING.emit(dtype=dtype)

def abj_listener(**kwargs):
    generic_listener('abjad')

def ly_listener(**kwargs):
    generic_listener('lilypond')

def mei_listener(**kwargs):
    generic_listener('mei')

outbound.WHO_IS_LISTENING.connect(abj_listener)
outbound.WHO_IS_LISTENING.connect(ly_listener)
outbound.WHO_IS_LISTENING.connect(mei_listener)

# this is what starts a test "action"
signals.ACTION_START.emit(dtype='LilyPond', doc='c4. d8')
