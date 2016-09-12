#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/outbound.py
# Purpose:                Signals for the "outbound" step.
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
Signals for the "outbound" step.

The structure of the :class:`~lychee.workflow.steps` module, which contains functions that run the
workflow steps, is such that the outbound steps use many fewer signals than the inbound steps. This
is a compromise taken to allow the parallel processing in the outbound steps (i.e., more than one
outbound data format can be processed at once).
'''

from . import signal


REGISTER_FORMAT = signal.Signal(args=['dtype', 'who', 'outbound'], name='outbound.REGISTER_FORMAT')
'''
To request that Lychee produce output data in a given format, call this signal before calling
:const:`ACTION_START`.

:kwarg str dtype: The data type to produce ('abjad', 'lilypond', 'mei', 'verovio').
:kwarg str who: (Optional). A unique identifier for the component requesting a format.
:kwarg bool outbound: (Optional). Whether to run an "outbound" step immediately.

The "outbound" argument causes the outbound step to run immediately, producing data for the whole
MEI document. Use this if you do not want to wait for data until an action has been run.

The "who" argument helps Lychee determine how manu user interface components are expecting data in
a given format. If three UI components call :const:`REGISTER_FORMAT` with the same "dtype" argument,
then one component sends the :const:`UNREGISTER_FORMAT` signal for that "dtype," the other two
components will not receive new data. However, if each component registers with a unique "who"
argument, Lychee will produce output for that "dtype" until all three components unregister.

Therefore, while it is not required to pass the "who" argument, and while there are some use cases
where Lychee may not benefit from such disambiguation (namely "one-shot" mode) we do recommend that
long-running applications use a "who" argument.
'''


UNREGISTER_FORMAT = signal.Signal(args=['dtype', 'who'], name='outbound.UNREGISTER_FORMAT')
'''
Tell Lychee that an interface component is no longer expecting output for a specific "dtype".

:kwarg str dtype: The data type to produce ('abjad', 'lilypond', 'mei', 'verovio').
:kwarg str who: (Optional). A unique identifier for the component requesting a format.

Refer to the discussion above for :const:`REGISTER_FORMAT`.
'''


STARTED = signal.Signal(name='outbound.STARTED')
'''
Emitted when outbound steps begin, before any of the views processing or conversion modules have
begun processing, and only once for all registered outbound formats.
'''


CONVERSION_FINISHED = signal.Signal(args=['dtype', 'placement', 'document', 'changeset'],
                                    name='outbound.CONVERSION_FINISHED')
'''
Emitted when one of the registered data types has finished outbound processing.

Depending on the environmental factors, the function that emits this signals
(:func:`lychee.workflow.steps.do_outbound_steps`) may either wait for all conversions to finish
before emitting the :const:`CONVERSION_FINISHED` signal, or may emit the signal at different times,
as the conversions finish.

:param str dtype: The data type of the "document" argument ("abjad", "lilypond", or "mei"). Always
    in lowercase.
:param object placement: Information for the slot about which part of the document is being updated.
    Offered in a different format depending on the "dtype" of this call.
:param object document: The update (partial) document. The type depends on the value of "dtype."
:param str changeset: If the VCS is disabled, this is an empty string. If the VCS is enabled, this
    is either the tag or the revision number and hash of the most recent changeset.
    If :const:`ACTION_START` was emitted with an inbound change, this will always be ``'tip'``
    because this tag always points to the most recent changeset. Otherwise it will be the same as
    "parent" field in ``hg summary`` (like ``'8:713cbfbaffcc'`` for example).

**Type of "Document" Parameter**

- If ``dtype`` is ``'mei'`` then ``document`` should be an :class:`lxml.etree.Element`.
'''


ERROR = signal.Signal(args=['msg'], name='outbound.ERROR')
'''
Emitted when there's an error during the outbound step.

:kwarg str msg: A descriptive error message for the log file.
'''
