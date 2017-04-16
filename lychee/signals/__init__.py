#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/__init__.py
# Purpose:                Initialize the "signals" module.
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

# NOTE that you must import the :mod:`lychee.signals.workflow` separately because it isn't imported
# by ``from lychee import *`` by default, because it caused too much trouble.

__all__ = ['document', 'inbound', 'vcs', 'outbound']
from . import *

from . import signal


def set_fujian(to_this):
    """
    Call this with a :class:`fujian.FujianWebSocketHandler` instance. :class:`Signal` instances will
    use it to emit themselves over the WebSocket connection.
    """
    from . import signal
    signal.set_fujian(to_this)


def simple_log_outputter(level, logger, message, time, **kwargs):
    """
    Output log messages to "stdout" if Fujian is not running.
    """
    if not signal.have_fujian():
        print('{} {} {}: {}'.format(time, level, logger, message))


ACTION_START = signal.Signal(args=['dtype', 'doc', 'views_info', 'revision'], name='ACTION_START')
"""
.. danger::
    .. deprecated:: 0.5.4
        Use :class:`lychee.workflow.session.InteractiveSession.run_workflow`,
        :class:`~lychee.workflow.session.InteractiveSession.run_inbound`, and
        :class:`~lychee.workflow.session.InteractiveSession.run_outbound` instead.

Emit this signal to start an "action" through Lychee.

:kwarg str dtype: As per :class:`~lychee.workflow.session.InteractiveSession.run_workflow` and
    :class:`~lychee.workflow.session.InteractiveSession.run_inbound`.
:kwarg object doc: As per :class:`~lychee.workflow.session.InteractiveSession.run_workflow` and
    :class:`~lychee.workflow.session.InteractiveSession.run_inbound`.
:kwarg str views_info: As per :class:`~lychee.workflow.session.InteractiveSession.run_workflow`,
    :class:`~lychee.workflow.session.InteractiveSession.run_inbound`, or
    :class:`~lychee.workflow.session.InteractiveSession.run_outbound`.
:kwarg str revision: As per :class:`~lychee.workflow.session.InteractiveSession.run_outbound`.
"""


LOG_MESSAGE = signal.Signal(args=['level', 'logger', 'message', 'status', 'time'], name='LOG_MESSAGE')
"""
.. note::
    This signal will *not* be removed.

Connect to this signal to receive log messages from Lychee. DO NOT use this signal to emit log
messages; instead, use one of the loggers in :mod:`lychee.logs`.

:kwarg str level: The log level of the message (one of "debug", "info", or "critical").
:kwarg str logger: Name of the :mod:`lychee.logs` logger sending the message.
:kwarg str message: The log message.
:kwarg str status: Status of the logged event (one of "begin", "comment", "exception", "end", "warning").
:kwarg str time: Running time of the logged event as measured by Lychee's loggers.
"""


LOG_MESSAGE.connect(simple_log_outputter)
