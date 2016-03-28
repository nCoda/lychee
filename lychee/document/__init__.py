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
Initializes the :mod:`document` module.
'''

from lxml import etree

import lychee
from lychee.document.document import Document


_MEINS = '{http://www.music-encoding.org/ns/mei}'


def _document_processor(converted, session, **kwargs):
    lychee.log('{}.document_processor(converted={})'.format(__name__, converted))

    score = etree.Element('{}score'.format(_MEINS))
    score.append(converted)

    doc = session.get_document()
    doc.put_score(score)
    output_filenames = doc.save_everything()

    return output_filenames
