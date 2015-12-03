#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/__init__.py
# Purpose:                Initialize Lychee.
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
Initialize Lychee.
'''

import time


__version__ = '0.0.1'
__all__ = ['converters', 'document', 'namespaces', 'signals', 'tui', 'vcs', 'views']

DEBUG = True


def log(message, level=None):
    '''
    Log a message according to runtime settings.

    :param str message: The message to log. Context will be prepended (time, module, etc.).
    :param str level: The level of the message in question (i.e., whether this is a "debug" or
        "warning" or "error" message). The default is "debug."

    **Side Effect**

    This method may cause a message to be printed to stdout or stderr or into a file.
    '''
    # TODO: use Python's actual logging mechanism

    if level is None:
        level = 'debug'

    if 'debug' == level and not DEBUG:
        return

    message = '[{time}] {name}: {message}'.format(name=__name__,
                                                  time=time.strftime('%H:%M:%S'),
                                                  message=message)

    print(message)


# many other modules will want to import :mod:`exceptions`, so it should be imported first
from lychee import exceptions
from lychee import *


# setup a Registrar instance for outbound format conversion
the_registrar = converters.registrar.Registrar()
signals.outbound.REGISTER_FORMAT.connect(the_registrar.register)
signals.outbound.UNREGISTER_FORMAT.connect(the_registrar.unregister)
