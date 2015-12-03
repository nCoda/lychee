#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/inbound.py
# Purpose:                Signals for the "inbound" step.
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
Signals for the "inbound" step.
'''

from . import signal


CONVERSION_START = signal.Signal(args=['document'], name='inbound.CONVERSION_START')
'''
Emitted when the inbound conversion will start (i.e., this signal is emitted to cause a converter
module to start the conversion).

:kwarg object document: The inbound musical document. The required type is determined by each
    converter module individually.
'''

CONVERSION_STARTED = signal.Signal(name='inbound.CONVERSION_STARTED')
# TODO: should this include info about the conversion started?
'''
Emitted as soon as the inbound conversion has started (i.e., as soon as the converter module has
begun to process data).
'''

CONVERSION_FINISH = signal.Signal(args=['converted'], name='inbound.CONVERSION_FINISH')
'''
Emitted just before the inbound conversion finishes (i.e., emitting this signal is the last action
of an inbound conversion module).

:kwarg converted: The inbound musical document, converted to Lychee-MEI format.
:type converted: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
'''

CONVERSION_FINISHED = signal.Signal(name='inbound.CONVERSION_FINISHED')
# TODO: should this include info about what was converted?
'''
Emitted when the inbound conversion is finished, before any "views" information is processed.
'''

CONVERSION_ERROR = signal.Signal(args=['msg'], name='inbound.CONVERSION_ERROR')
'''
Emitted when there's an error during the in bound conversion step.

:kwarg str msg: A descriptive error message for the log file.
'''

VIEWS_START = signal.Signal(args=['dtype', 'doc', 'converted'], name='inbound.VIEWS_START')
'''
Emitted when the inbound view processing will start (i.e., this signal is emitted to cause the views
module to start its bit).

:kwarg str dtype: The format (data type) of the inbound musical document. LilyPond, Abjad, etc.
:kwarg object doc: The inbound musical document. The required type is determined by each converter
    module individually.
:kwarg converted: The inbound musical document, converted to Lychee-MEI format.
:type converted: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
'''

VIEWS_STARTED = signal.Signal(name='inbound.VIEWS_STARTED')
# TODO: should this include information about the view being processed?
'''
Emitted as soon as the views module begins its inbound processing (i.e., as soon as the views module
has begun to process data).
'''

VIEWS_FINISH = signal.Signal(args=['views_info'], name='inbound.VIEWS_FINISH')
'''
Emitted just before the views module finishes its inbound processing (i.e., just before the views
module returns).

:kwarg views_info: Information about the inbound "view."
'''

VIEWS_FINISHED = signal.Signal(name='inbound.VIEWS_FINISHED')
# TODO: should this include information about the view processed?
'''
Emitted when the inbound views processing is finished.
'''

VIEWS_ERROR = signal.Signal(args=['msg'], name='inbound.VIEWS_ERROR')
'''
Emitted when there's an error while processing the inbound view.

:kwarg str msg: A descriptive error message for the log file.
'''
