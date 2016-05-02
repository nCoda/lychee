#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/__init__.py
# Purpose:                Initialization for converters module.
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
Each converter module, designed in the way most suitable for the module author's skills, provides a
public interface with a single function, :func:`convert`, that performs conversions as appropriate
for that module. Thus for example :func:`lychee.converters.lmei_to_abjad.convert` accepts a
Lychee-MEI document (fragment) and produces an Abjad document (fragment).

**Inbound converters** produce a Lychee-MEI document as an :class:`lxml.etree.Element` object.
**Outbound converters** consume an :class:`Element` and produce a document in the external format.
Some outbound converters are a serialization for non-musical data, like the :mod:`vcs_outbound` and
:mod:`document_outbound` converters, which produce Mercurial data and MEI document metadata,
respectively.

Converters must be capable of partial document conversion: accepting an incomplete document fragment
and producing corresponding output, even if the inputted document would not by itself be valid. For
example, a LilyPond converter should be able to accept ``des,4`` even though the LilyPond program
would not render output from this.


Work In Progress
^^^^^^^^^^^^^^^^

Do note that the converter modules are currently incomplete in two ways. This means both: the
existing converters do not support everything the external formats can encode; and we intend to
provide additional converters in the future.


XMLID Values
^^^^^^^^^^^^

Depending on how the :mod:`~lychee.views` modules are implemented, we may place restrictions on the
@xml:id values produced and consumed by converters. Inbound converters are not, and will not be,
required to produce Lychee-MEI compliant @xml:id values.

Currently, the inbound Abjad converter uses a hash function based on certain characteristics to
ensure that an element's @xml:id value is unique within a ``<section>``, and that it will change
when the element is moved within the document or its attributes are modified. This allows the
:mod:`views` module to use a shortcut when computing the differences between the current and
incoming Lychee-MEI documents. We may enforce this for all converters, if possible.
'''

# Jeff: "Well, a universal converter is, by definition, a pretty slutty thing."

__all__ = ['mei_to_ly', 'ly_to_mei', 'lmei_to_abjad', 'abjad_to_lmei', 'mei_to_lmei', 'lmei_to_mei',
    'lmei_to_verovio', 'registrar', 'vcs_outbound', 'document_outbound']

from lychee.converters import *


# NOTE: please keep the keys in lowercase
INBOUND_CONVERTERS = {'lilypond': ly_to_mei.convert,
                      'abjad': abjad_to_lmei.convert,
                      'mei': mei_to_lmei.convert
                     }
'''
Mapping from the lowercase name of an inbound converter format to the :func:`convert` function that
converts from that format to Lychee-MEI.
'''

# NOTE: please keep the keys in lowercase
OUTBOUND_CONVERTERS = {'lilypond': mei_to_ly.convert,
                       'abjad': lmei_to_abjad.convert,
                       'mei': lmei_to_mei.convert,
                       'verovio': lmei_to_verovio.convert,
                       'vcs': vcs_outbound.convert,
                       'document': document_outbound.convert,
                      }
'''
Mapping from the lowercase name of an outbound converter format to the :func:`convert` function that
converts from Lychee-MEI into hat format.
'''
