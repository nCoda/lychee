#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/document/__init__.py
# Purpose:                Initializes the "document" module.
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
The :mod:`~lychee.document.document` module contains components to responsible for the files in a
Lychee-MEI document, including a host of helper functions and the :class:`~document.Document` class.
The optional version control repository is managed by the :mod:`lychee.vcs` module.

In order to consolidate file- and document-related functionality, no other *Lychee* module should
read from or write to files. This helps us ensure consistency and correctness of the Lychee-MEI
document, and also avoids duplicating and spreading functionality.

Document manipulation in other *Lychee* modules usually occurs with ``<section>`` elements or lower
in the hierarchy, allowing :class:`~document.Document` to coordinate ``<section>`` elements and
store them in files as required by Lychee-MEI.

:class:`~document.Document` will eventually be able to handl requests for document fragments
according to @xml:id, rather than being restricted to a complete ``<section>`` or ``<score>``.
'''

from lychee.document.document import Document
