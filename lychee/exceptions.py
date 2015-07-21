#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/document/document.py
# Purpose:                Contains an object representing an MEI document.
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
Errors and Warnings for Lychee-specific error conditions.
'''


class LycheeError(Exception):
    '''
    Base class for all Lychee-specific errors.
    '''
    pass


class DocumentError(LycheeError):
    '''
    Generic exception for errors related to the handling of Lychee's internal MEI document.
    '''
    pass


class SectionNotFoundError(DocumentError):
    '''
    Error indicating a <section> with a particular @xml:id attribute is needed but can't be found.
    '''
    pass


class HeaderNotFoundError(DocumentError):
    '''
    Error indicating the <meiHead> section is needed but can't be found.
    '''
    pass


class CannotSaveError(DocumentError):
    '''
    Error indicating the MEI document could not be saved as requested.
    '''
    pass
