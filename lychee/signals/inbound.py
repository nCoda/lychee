#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/inbound.py
# Purpose:                Signals for the "inbound" step.
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
'''
Emitted when the inbound conversion is finished, before any "views" information is processed.
'''

CONVERSION_ERROR = signal.Signal(args=['msg'], name='inbound.CONVERSION_ERROR')
'''
Emitted when there's an error during the in bound conversion step.

:kwarg str msg: A descriptive error message for the log file.
'''

VIEWS_START = signal.Signal(args=['converted', 'document', 'session'], name='inbound.VIEWS_START')
'''
Emit this signal to start the inbound views processing step.

:param converted: The incoming (partial) document, already converted.
:type converted: :class:`lxml.etree.Element` or :class:`lxml.etree.ElementTree`
:param document: The incoming (partial) document for conversion, as supplied to
    :func:`do_inbound_conversion`.
:type document: As required by the converter.
:param session: A session instance for the ongoing notation session.
:type session: :class:`lychee.workflow.session.InteractiveSession`

By default, this signal is not connected to a views-processing module so you must connect it to the
proper function before you emit this signal. This is provided as a signal so that additional modules
can be notified of the workflow progress.

For information on writing a views processing module, refer to the :mod:`lychee.views` module
documentation.
'''

VIEWS_STARTED = signal.Signal(name='inbound.VIEWS_STARTED')
'''
Emitted by the inbound views processing module as soon as it gains control, thereby confirming that
an inbound views processor was correctly chosen.
'''

VIEWS_FINISH = signal.Signal(args=['views_info'], name='inbound.VIEWS_FINISH')
'''
Emitted by the inbound views processing module to return views information to its caller.
'''

VIEWS_FINISHED = signal.Signal(name='inbound.VIEWS_FINISHED')
'''
Emitted after inbound views processing by the module running the workflow.
'''

VIEWS_ERROR = signal.Signal(args=['msg'], name='inbound.VIEWS_ERROR')
'''
Emitted by the inbound views processing module, or the module running the workflow, to indicate that
an error has occurred while generating views information. The error may be recoverable, or may cause
the entire views step to fail, but *Lychee* may be able to continue the workflow.

:kwarg str msg: A descriptive error message for the log file.
'''
