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

import six
from lxml import etree

from lychee import log

# NOTE that you must import the :mod:`lychee.signals.workflow` separately because it isn't imported
# by ``from lychee import *`` by default, because it caused too much trouble.

__all__ = ['inbound', 'document', 'vcs', 'outbound']

import signalslot


# This is a module-level FujianWebSocketHandler instance. The Signal class uses it to emit signals
# to the GUI over the WebSocket connection.
_module_fujian = None


def set_fujian(to_this):
    '''
    Call this with a :class:`fujian.FujianWebSocketHandler` instance. :class:`Signal` instances will
    use it to emit themselves over the WebSocket connection.
    '''

    global _module_fujian
    _module_fujian = to_this


class Signal(signalslot.Signal):
    '''
    A Lychee-specific extension of the :class:`signalslot.Signal` class that emits signals through
    the "Fujian" WebSocket server, if it's available.
    '''

    def __init__(self, args=None, name=None, threadsafe=False):
        '''
        Determine whether Fujian is available then call the superclass constructor.
        '''
        global _module_fujian
        try:
            _module_fujian
            self._ws = True
        except NameError:
            self._ws = False
        signalslot.Signal.__init__(self, args, name, threadsafe)

    def emit(self, **kwargs):
        '''
        Emit the signal via Fujian if possible, then call the superclass :meth:`emit`.
        '''
        global _module_fujian
        if self._ws:
            payload = {'signal': self.name}
            for arg in self.args:
                if arg in kwargs:
                    if isinstance(kwargs[arg], etree._Element):
                        payload[arg] = etree.tostring(kwargs[arg])
                    else:
                        payload[arg] = six.text_type(kwargs[arg])
                else:
                    log('Missing "{}" arg for "{}" signal'.format(arg, self.name))

            try:
                _module_fujian.write_message(payload)
            except NameError:
                self._ws = False

        signalslot.Signal.emit(self, **kwargs)


ACTION_START = Signal(args=['dtype', 'doc'], name='ACTION_START')
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
