#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/logs.py
# Purpose:                Configure Lithoxyl logs for Lychee.
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
"""
Configure Lithoxyl logs for Lychee.
"""

from __future__ import unicode_literals
from lithoxyl import logger, SensibleFilter, SensibleSink


INBOUND_LOG = None
DOCUMENT_LOG = None
VCS_LOG = None
OUTBOUND_LOG = None
SESSION_LOG = None


class LycheeEmitter(object):
    """
    An "emitter" for the Lithoxyl :class:`SensibleSink` that sends log messages through the
    :const:`lychee.signals.LOG_MESSAGE` signal.
    """

    def emit_entry(self, action, entry):
        import lychee.signals
        lychee.signals.LOG_MESSAGE.emit(**entry)

    on_begin = on_warn = on_end = on_comment = emit_entry


class LycheeFormatter(object):
    """
    A "formatter" for the Lithoxyl :class:`SensibleSink` that formats log messages as a dictionary
    with the following fields:

    - level
    - logger
    - message
    - status
    - time
    """

    def do_format(self, event):
        return {
            'level': event.level_name.upper(),
            'logger': event.logger.name,
            'message': event.end_event.message,
            'status': event.status,
            'time': str(event.etime),
        }

    on_begin = on_warn = on_end = on_comment = do_format


def logging_init():
    """
    Initialize Lychee's logging stuff.

    This function is called automatically when the :mod:`logs` module is imported. All the ``*_LOG``
    :class:`~lithoxyl.logger.Logger` instances are created always and only when
    ``INBOUND_LOG is None``.
    """
    global INBOUND_LOG
    global DOCUMENT_LOG
    global VCS_LOG
    global OUTBOUND_LOG
    global SESSION_LOG

    if INBOUND_LOG is None:
        log_filter = SensibleFilter(success='critical', failure='info', exception='debug')
        emitter = LycheeEmitter()
        sink = SensibleSink(filters=[log_filter], formatter=LycheeFormatter(), emitter=emitter)

        INBOUND_LOG = logger.Logger('inbound', sinks=[sink])
        DOCUMENT_LOG = logger.Logger('document', sinks=[sink])
        VCS_LOG = logger.Logger('vcs', sinks=[sink])
        OUTBOUND_LOG = logger.Logger('outbound', sinks=[sink])
        SESSION_LOG = logger.Logger('session', sinks=[sink])


logging_init()
