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
"""
Initialize Lychee.
"""


# we'll keep PyPI metadata here so they can be used by Sphinx in the API too
__metadata__ = {
    'author': 'Christopher Antila',
    'author_email': 'christopher.antila@ncodamusic.org',
    'copyright': u'2016 nCoda and others',  # only used in the API
    'description': 'An engine for MEI document management and converion.',
    'license': 'GPLv3+',
    'name': 'Lychee',
    'url': 'https://lychee.ncodamusic.org/',
    'version': '0.5.3',
}

__version__ = __metadata__['version']
__all__ = ['converters', 'document', 'exceptions', 'logs', 'namespaces', 'signals', 'tui',
    'workflow', 'vcs', 'views']
