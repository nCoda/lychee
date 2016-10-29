#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/exceptions.py
# Purpose:                Errors and Warnings for Lychee-specific error conditions.
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
Errors and Warnings for Lychee-specific error conditions.
'''

import six


class LycheeError(Exception):
    '''
    Base class for all Lychee-specific errors.
    '''
    pass


class LycheeWarning(UserWarning):
    '''
    Base class for all Lychee-specific warnings.
    '''
    pass


class DocumentError(LycheeError):
    '''
    Generic base for errors related to the handling of Lychee's internal MEI document.
    '''
    pass


if six.PY2:
    class FileNotFoundError(DocumentError):
        '''
        Generic base for errors that indicate a file from an MEI document cannot be loaded. This is
        a subclass of :class:`DocumentError` in Python 2, and an alias to :exc:`FileNotFoundError`
        in Python 3. It's held in this module so Lychee code may use the same symbol in both
        Python versions.
        '''
        pass
else:
    FileNotFoundError = FileNotFoundError


class SectionNotFoundError(FileNotFoundError):
    '''
    Error indicating a <section> with a particular @xml:id attribute is needed but can't be found.
    '''
    pass


class HeaderNotFoundError(FileNotFoundError):
    '''
    Error indicating the <meiHead> section is needed but can't be found.
    '''
    pass


class InvalidDocumentError(DocumentError):
    '''
    Generic base for errors indicating that (part of) an MEI document is invalid.
    '''
    pass


class InvalidFileError(InvalidDocumentError):
    '''
    Indicating that a file exists and could be loaded, but contains something other than a (portion
    of a) valid MEI document.
    '''
    pass


class CannotSaveError(DocumentError):
    '''
    Error indicating the MEI document could not be saved as requested.
    '''
    pass


class LycheeMEIWarning(LycheeWarning):
    '''
    When the Lychee-MEI specification (or MEI specification) has not been followed, so a function
    cannot produce useful data, but the function's caller may be able to save the situation (for
    example by continuing a file export with some data missing).

    Use :class:`LycheeMEIError` correct operation is not possible.
    '''
    pass


class LycheeMEIError(LycheeError):
    '''
    When the Lychee-MEI specification (or MEI specification) has not been followed, and correct
    operation is not possible.

    Use :class:`LycheeMEIWarning` when a function cannot produce useful data but its caller may be
    able to correct the situation.
    '''
    pass


class RepositoryError(LycheeError):
    '''
    When there was an error related to Lychee's repository.
    '''
    pass


class InvalidDataTypeError(LycheeError):
    '''
    When an error is caused by an invalid data type.
    '''
    pass


class ConversionError(LycheeError):
    '''
    When an error occurs during conversion.
    '''
    pass


class InboundConversionError(ConversionError):
    '''
    When an error occurs during inbound conversion.
    '''
    pass


class OutboundConversionError(ConversionError):
    '''
    When an error occurs during outbound conversion.
    '''
    pass


class ViewsError(LycheeError):
    '''
    When an error occurs while processing "view" information.
    '''
    pass


class LilyPondError(InboundConversionError):
    '''
    An error caused by incorrect LilyPond during inbound conversion.

    An error during outbound conversion to LilyPond would be a :exc:`LycheeMEIError`.
    '''
    pass
