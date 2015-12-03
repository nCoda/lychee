#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/signal.py
# Purpose:                Lychee-specific Signal class.
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
Lychee-specific Signal class.
'''

import signalslot
import six

# from lychee import log


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
    def __init__(self, *args, **kwargs):
        # print('initializing {}'.format(kwargs['name'])) ##############################################
        signalslot.Signal.__init__(self, *args, **kwargs)

    def emit(self, **kwargs):
        '''
        Emit the signal via Fujian if possible, then call the superclass :meth:`emit`.
        '''
        global _module_fujian
        if _module_fujian is not None:
            payload = {'signal': self.name}
            for arg in self.args:
                if arg in kwargs:
                    if isinstance(kwargs[arg], etree._Element):
                        payload[arg] = etree.tostring(kwargs[arg])
                    else:
                        payload[arg] = six.text_type(kwargs[arg])
                else:
                    # log('Missing "{}" arg for "{}" signal'.format(arg, self.name))
                    # TODO
                    pass

            try:
                _module_fujian.write_message(payload)
            except AttributeError:
                # TODO: something useful?
                pass

        signalslot.Signal.emit(self, **kwargs)
