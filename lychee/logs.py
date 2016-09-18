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

from lithoxyl import logger, SensibleFilter, SensibleFormatter, StreamEmitter, SensibleSink


INBOUND_LOG = None


def logging_init():
    """
    Initialize Lychee's logging stuff.
    """
    global INBOUND_LOG

    # NOTE: it's just copy-and-pasted from the Lithoxyl docs
    log_filter = SensibleFilter(success='debug', failure='debug', exception='debug')
    formatter = SensibleFormatter('{import_delta_s} {level_name_upper} {logger_name}: {end_message}')
    emitter = StreamEmitter('stdout')
    sink = SensibleSink(filters=[log_filter], formatter=formatter, emitter=emitter)

    INBOUND_LOG = logger.Logger('inbound', sinks=[sink])
