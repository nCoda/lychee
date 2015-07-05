#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/__init__.py
# Purpose:                Initialize the "signals" module.
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
Initialize the :mod:`signals` module.
'''

# NOTE that you must import the :mod:`lychee.signals.workflow` separately because it isn't imported
# by ``from lychee import *`` by default, because it caused too much trouble.

__all__ = ['inbound', 'document', 'vcs', 'outbound']

import signalslot
from lychee.signals import *


ACTION_START = signalslot.Signal(args=['dtype', 'doc'])
'''
Emit this signal to start an "action" through Lychee.

:kwarg str dtype: The format (data type) of the inbound musical document. LilyPond, Abjad, etc.
:kwarg object doc: The inbound musical document. The required type is determined by each converter
    module individually.
'''


def action_starter(dtype, doc, **kwargs):
    '''
    Default connection for the ACTION_START signal.
    '''
    # NB: workflow imported here because, in the main module, it would cause circular import probs
    from . import workflow
    workm = workflow.WorkflowManager(dtype, doc)
    workm.run()
    del workm

ACTION_START.connect(action_starter)
