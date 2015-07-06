#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/document.py
# Purpose:                Signals for the "document step."
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
Signals for the "document step."
'''

import signalslot


START = signalslot.Signal()
'''
Emitted by the :class:`WorkflowManager` to begin processing during the "document" stage.
'''

STARTED = signalslot.Signal()
'''
Emitted by the ``lychee.vcs`` module, once it gains control flow and begins to determine how to
manage changes proposed to the musical document.
'''

FINISH = signalslot.Signal()
'''
Emitted by the ``lychee.document`` module, once its actions are complete, to return relevant
information to the :class:`WorkflowManager`.
'''

FINISHED = signalslot.Signal()
'''
This signal is emitted by the :class:`WorkflowManager` once it gains control flow after the
"document" step has finished.
'''

ERROR = signalslot.Signal()
'''
Emit this signal when an error occurs during the "document" stage.
'''