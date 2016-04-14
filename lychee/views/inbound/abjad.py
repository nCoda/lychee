#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/views/inbound/abjad.py
# Purpose:                Inbound views processing for Abjad.
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
Inbound views processing for Abjad.
'''

from lychee import DEBUG
from lychee.namespaces import xml
from lychee import signals


# translatable strings
# error messages
_GENERIC_ERROR = 'Unexpected error during inbound views: {0}'


def place_view(converted, document, session, **kwargs):
    '''
    Do the inbound views processing for Abjad (place the external view into the full document).

    Arguments as per :const:`lychee.signals.inbound.VIEWS_START`.
    '''
    signals.inbound.VIEWS_STARTED.emit()
    try:
        post = _place_view(converted, document, session)
    except Exception as exc:
        if DEBUG:
            raise
        else:
            signals.inbound.VIEWS_ERROR.emit(msg=_GENERIC_ERROR.format(repr(exc)))
    else:
        signals.inbound.VIEWS_FINISH.emit(views_info=post)


def _place_view(converted, document, session):
    '''
    '''
    pass
