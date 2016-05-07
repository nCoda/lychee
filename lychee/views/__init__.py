#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/views/__init__.py
# Purpose:                Initialize the "views" module.
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
The :mod:`~lychee.views` modules allow *Lychee* to keep track of several discrete musical fragments
at once, and to determine the most efficient way to provide updates for all registered outbound
formats. An action with views processing looks approximately like this:

#. Inbound conversion.
#. Inbound views ("What part of the music was updated?")
#. Document assembly.
#. VCS (optional).
#. Outbound views ("Send out this part of the music.")
#. Outbound conversion.

The views processing steps determine which part of the internal Lychee-MEI score to update during an
inbound change, and which part of the external format's data to update as a result. Knowing which
part of the score is modified, *Lychee* will only send updates for external formats if the portion
of the document *currently in view* has been modified. This ability to understand *views on a
document* allows *Lychee* to work effectively in situations where full-document conversion would be
too time-consuming.

Regardless, *Lychee* is also capable of working with complete documents.


Sample Uses
-----------

Example 1:
    A user creates a new note with a score-based point-and-click interface. The LilyPond
    representation of that moment, also visible, should be updated with only the single new
    note---the whole MEI document will not be converted from scratch. This requires sending a
    single MEI ``<note>`` element to the outbound LilyPond converter, along with instructions on
    where to place the note (row and column in the text file).

Example 2:
    A user selects a two-measure musical passage, then requests the Abjad representation of those
    measures. Even though the inbound stage is skipped, the outbound Abjad converter should only
    receive two measures.

Example 3:
    A user opens a score from the MEI sample encodings. *Lychee* converts the score to Lychee-MEI
    and caches the views information required to ensure the first two examples are possible immediately.


Inbound Views
-------------

During the inbound stage, the views processing modules fit a view into the complete score. During an
interactive notation editing session, the inbound views modules determine how much of the score is
affected by an edit, and provide this information to the outbound views modules.

Modules for the :mod:`inbound` direction must provide a function
``place_view(converted, document, session)``, with the parameters are the same as specified for
:const:`lychee.signals.inbound.VIEWS_START` (being the converted music, the external-format music,
and the current :class:`~lychee.workflow.session.InteractiveSession` instance). In order to allow
proper operation of the workflow signals, :func:`place_view` **must** return ``None`` and use the
following three signals as described:

- :const:`~lychee.signals.inbound.VIEWS_STARTED` immediately after receiving control, to confirm
  that a views processing module was selected correctly.
- :const:`~lychee.signals.inbound.VIEWS_ERROR` for errors during processing, with a description of
  the error. Note that this signal should be used for recoverable errors; if execution must stop
  because of an error, we recommend raising an exception as per standard Python practice.
- :const:`~lychee.signals.inbound.VIEWS_FINISH` with results when views processing completes
  successfully. Because the function must return ``None``, this signal is the only way to provide
  views data back to the caller. It is possible to complete processing and emit :const:`VIEWS_FINISH`
  after reporting a recoverable error with :const:`VIEWS_ERROR`.


Outbound Views
--------------

During the outbound stage, the views processing modules produce a view with the required music.
During an interactive notation editing session, the oubound views modules ensure that changing a
single note in the score doesn't result in re-converting the entire score from scratch for all
registered outbound formats.

Modules for the :mod:`outbound` direction must provide a function ``get_view(repo_dir, views_info)``
where the parameters are the same as specified for :func:`lychee.workflow.steps.do_outbound_steps`
(being a string to the directory of the repository, and a string with the @xml:id of the element
for export). The function must return a two-tuple: the first element is the "views" information
required by the :const:`CONVERSION_FINISHED` signal; the second is the :class:`~lxml.etree.Element`
indicated by the ``views_info`` argument, along with any required changes to @xml:id attributes.


Example
-------

This example converts from an Abjad/LilyPond/music21-like data format that doesn't exist. The
inbound converter receives three Note objects:

    >>> inbound = [Note('c4'), Note('d4'), Note('e4')]
    >>> inbound_mei = convert(inbound)

The inbound converter produces Lychee-MEI *but* with non-conformant @xml:id attributes. The @xml:id
attributes provided by the converter are designed to be unique in the score, for example by computing
a cryptographic hash involving all of the element's attributes. (Note that inbound converters must
produce IDs that are consistent across user sessions and Python interpreters, so using the built-in
:func:`id` function is clever but not acceptable).

    >>> inbound_mei[0].get('xml:id')
    'z1de512a9c446cd'
    >>> inbound_mei[1].get('xml:id')
    'a66d9902885d427'
    >>> inbound_mei[2].get('xml:id')
    'accb45e81aeee72'

The :mod:`views` module replaces the @xml:id attributes with proper Lychee-MEI values. (And the
values of any attribute that refers to that @xml:id). Aong the way, :mod:`views` also generates
mappings between the converter-supplied and corresponding Lychee-MEI @xml:id.

    >>> extern_to_mei_ids = {}
    >>> mei_to_extern_ids = {}
    >>> for element in every_element_in_the_score:
    ...     this_id = make_new_xml_id(element)
    ...     extern_to_mei_ids[element.get('xml:id')] = this_id
    ...     mei_to_extern_ids[this_id] = element.get('xml:id')
    ...     element.set('xml:id', this_id)
    ...
    >>>

If we create a new document that's *mostly* the same, the :mod:`views` modules has the context it
needs to determine what part of the document has changed.

    >>> inbound = [Note('c4'), Note('d-4'), Note('e4')]
    >>> inbound_mei = convert(inbound)
    >>> inbound_mei[0].get('xml:id')
    'z1de512a9c446cd'
    >>> inbound_mei[1].get('xml:id')
    '8efa7afeab8a29b'
    >>> inbound_mei[2].get('xml:id')
    'accb45e81aeee72'

You can see how only the second note is different from the first example, which is reflected in the
ID values provided by the inbound converter. Even though all three Python objects are different from
the first example, the :mod:`views` module is able to determine that only the second object is
*meaningfully* different. This allows the document preparation, version control, and outbound stages
to continue with the smallest possible data to process.
'''

from . import inbound
from . import outbound
