#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/__init__.py
# Purpose:                Initialize Lychee.
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
Initialize Lychee.
'''

import time


# we'll keep PyPI metadata here so they can be used by Sphinx in the API too
__metadata__ = {
    'author': 'Christopher Antila',
    'author_email': 'christopher.antila@ncodamusic.org',
    'copyright': u'2016 nCoda and others',  # only used in the API
    'description': 'An engine for MEI document management and converion.',
    'license': 'GPLv3+',
    'name': 'Lychee',
    'url': 'https://lychee.ncodamusic.org/',
    'version': '0.5.0',
}

__version__ = __metadata__['version']
__all__ = ['converters', 'document', 'namespaces', 'signals', 'tui', 'workflow', 'vcs', 'views']

DEBUG = False


def log(message, level=None):
    '''
    Log a message according to runtime settings.

    :param str message: The message to log. Context will be prepended (time, module, etc.).
    :param str level: The level of the message in question (i.e., whether this is a "debug" or
        "warning" or "error" message). The default is "debug."

    **Side Effect**

    This method may cause a message to be printed to stdout or stderr or into a file.
    '''

    if level is None:
        level = 'debug'

    level = level.lower()

    if 'debug' == level and not DEBUG:
        return

    message = '[{time}] {name}: {message}'.format(name=__name__,
                                                  time=time.strftime('%H:%M:%S'),
                                                  message=message)

    print(message)


# many other modules will want to import :mod:`exceptions`, so it should be imported first
try:
    from lychee import exceptions
    from lychee import *
except ImportError as exc:
    log(str(exc), level='ERROR')
else:
    InteractiveSession = workflow.session.InteractiveSession
