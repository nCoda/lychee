#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/document/__init__.py
# Purpose:                Initializes the "document" module.
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
Initializes the :mod:`document` module.
'''

from lxml import etree as ETree

from lychee.signals import document as document_signals
from lychee.document.document import Document


_MEINS = '{http://www.music-encoding.org/ns/mei}'


def _document_processor(converted, **kwargs):
    document_signals.STARTED.emit()
    print('{}.document_processor(converted={})'.format(__name__, converted))

    score = ETree.Element('{}score'.format(_MEINS))
    score.append(converted)

    doc = Document()
    doc.put_score(score)
    output_filenames = doc.save_everything()

    document_signals.FINISH.emit(pathnames=output_filenames)
    print('{}.document_processor() after finish signal'.format(__name__))


document_signals.START.connect(_document_processor)
