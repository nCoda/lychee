#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/outbound.py
# Purpose:                Signals for the "outbound" step.
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
Signals for the "outbound" step.
'''

from . import signal


WHO_IS_LISTENING = signal.Signal(name='outbound.WHO_IS_LISTENING')
'''
The :class:`WorkflowManager` emits this signal before beginning the outbound processing steps, in
order to determine the outbound formats that are required at the moment. Every UI component that
wants an update should emit the :const:`I_AM_LISTENING` signal with the required data type, to
ensure the proper data type will be prepared.

UI components receive their data from the :const:`CONVERSION_FINISHED` signal, which is emitted
for every data type prepared. Therefore, slots on UI components must double-check they have been
called with the required data type, and not complain if the data is the wrong type, because they
will very often be called with data of the wrong type.

For as long as Lychee runs synchronously (which is likely to be always) the :const:`WHO_IS_LISTENING`
call and :const:`I_AM_LISTENING` response pattern will work just fine because outbound processing
cannot begin until all the :const:`WHO_IS_LISTENING` slots have finished execution.
'''

I_AM_LISTENING = signal.Signal(args=['dtype'], name='outbound.I_AM_LISTENING')
'''
As described above, UI components should emit this signal with the proper data type to ensure they
will receive the data they require. It is safe to emit this signal multiple times with the same
argument---the :class:`WorkflowManager` will still only perform the conversion once per data type.

:kwarg str dtype: The requested data type ('abjad', 'lilypond', 'mei')
'''

VIEWS_START = signal.Signal(args=['dtype'], name='outbound.VIEWS_START')
'''
Emitted to begin outbound views processing. (This is emitted several times---once per data type).

:kwarg str dtypes: The desired outbound format.
'''

VIEWS_STARTED = signal.Signal(name='outbound.VIEWS_STARTED')
'''
Emitted when outbound view processing begins.
'''

VIEWS_FINISH = signal.Signal(args=['dtype', 'views_info'], name='outbound.VIEWS_FINISH')
'''
Emitted with the results of outbound views processing.

:kwarg str dtype: The data type this views information corresponds to.
:kwarg object views_info: The views information required for the "dtype" data format.
'''

VIEWS_FINISHED = signal.Signal(name='outbound.VIEWS_FINISHED')
'''
Emitted after the views processing has completed for *all* data types.
'''

VIEWS_ERROR = signal.Signal(args=['msg'], name='outbound.VIEWS_ERROR')
'''
Emitted when there's an error while processing the outbound view.

:kwarg str msg: A descriptive error message for the log file.
'''

CONVERSION_START = signal.Signal(args=['views_info', 'outbound'], name='outbound.CONVERSION_START')
'''
Emitted to being outbound conversion. (This is emitted several times---once per data type).

:kwarg object views_info: The views information required for the "dtype" data format.
:kwarg outbound: The Lychee-MEI document required to prepare the outbound data.
:type outbound: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
'''

CONVERSION_STARTED = signal.Signal(name='outbound.CONVERSION_STARTED')
'''
Emitted when outbound conversion begins.
'''

CONVERSION_FINISH = signal.Signal(args=['converted'], name='outbound.CONVERSION_FINISH')
'''
Emitted with the results of an outbound conversion.

:kwarg object converted: The converted document, ready for UI components.
'''

CONVERSION_FINISHED = signal.Signal(args=['dtype', 'placement', 'document'], name='outbound.CONVERSION_FINISHED')
'''
Emitted by the :class:`WorkflowManager` after all data types have been prepared, once per data type.
Slots should pay attention to the "dtype" value to know whether they are interested in the document
in the currently-offered format, or they wish to wait for another format.

To help ensure all UI components will be updated at approximately the same time, all outbound
formats are prepared before any :const:`CONVERSION_FINISHED` signal is emitted.

:param str dtype: The data type of the "document" argument ("abjad", "lilypond", or "mei"). Always
    in lowercase.
:param object placement: Information for the slot about which part of the document is being updated.
    Offered in a different format depending on the "dtype" of this call.
:param object document: The update (partial) document. The type depends on the value of "dtype."

**Type of "Document" Parameter**

- If ``dtype`` is ``'mei'`` then ``document`` should be an :class:`lxml.etree.Element`.
'''

CONVERSION_ERROR = signal.Signal(args=['msg'], name='outbound.CONVERSION_ERROR')
'''
Emitted when there's an error during the outbound conversion step.

:kwarg str msg: A descriptive error message for the log file.
'''
