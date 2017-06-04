#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/signal.py
# Purpose:                Lychee-specific Signal class.
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
Lychee-specific Signal class.
'''

import signalslot

from lychee.logs import SESSION_LOG as log


# These are the signals that Fujian wants to know about, if we're being run by Fujian.
FUJIAN_INTERESTED_SIGNALS = ('outbound.CONVERSION_FINISHED', 'outbound.ERROR', 'LOG_MESSAGE')


# This is a module-level FujianWebSocketHandler instance. The Signal class uses it to emit signals
# to the GUI over the WebSocket connection.
_module_fujian = None


def have_fujian():
    '''
    Return ``True`` if a :class:`~fujian.Fujian` instance is configured.
    '''
    return _module_fujian is not None


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

    def emit(self, **kwargs):
        '''
        Emit the signal via Fujian if possible, then call the superclass :meth:`emit`.
        '''
        global _module_fujian
        if _module_fujian is not None:
            with log.debug('emitting {signal} signal', signal=self.name):
                if self.name in FUJIAN_INTERESTED_SIGNALS:
                    _module_fujian.signal(self.name, **kwargs)

        # NOTE: the "stringified" args are only sent through Fujian; here we keep Python objects
        signalslot.Signal.emit(self, **kwargs)
