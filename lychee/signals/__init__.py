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
'''
Initialize the :mod:`signals` module.
'''

import six
from lxml import etree

from lychee import log

# NOTE that you must import the :mod:`lychee.signals.workflow` separately because it isn't imported
# by ``from lychee import *`` by default, because it caused too much trouble.

__all__ = ['document', 'inbound', 'vcs', 'outbound']
from . import *

from . import signal


def set_fujian(to_this):
    '''
    Call this with a :class:`fujian.FujianWebSocketHandler` instance. :class:`Signal` instances will
    use it to emit themselves over the WebSocket connection.
    '''
    from . import signal
    signal.set_fujian(to_this)


ACTION_START = signal.Signal(args=['dtype', 'doc'], name='ACTION_START')
'''
Emit this signal to start an "action" through Lychee.

:kwarg str dtype: The format (data type) of the inbound musical document. LilyPond, Abjad, etc.
:kwarg object doc: The inbound musical document. The required type is determined by each converter
    module individually.
'''


def action_starter(**kwargs):
    '''
    Default connection for the ACTION_START signal.
    '''
    # NB: workflow imported here because, in the main module, it would cause a circular import
    from . import workflow
    if 'dtype' in kwargs and 'doc' in kwargs:
        workm = workflow.WorkflowManager(kwargs['dtype'], kwargs['doc'])
    else:
        workm = workflow.WorkflowManager()
    workm.run()
    del workm

ACTION_START.connect(action_starter)
