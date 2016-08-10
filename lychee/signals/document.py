#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/document.py
# Purpose:                Signals for operations on Lychee's current Document instance.
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
Signals for operations on Lychee's current :class:`Document` instance.
'''


from lychee.document import document
from . import signal
from . import vcs


MOVE_SECTION_TO = signal.Signal(args=['xmlid', 'position'], name='document.MOVE_SECTION_TO')
'''
.. warning::
    This signal is deprecated.
    Refer to `T108 <https://goldman.ncodamusic.org/T108>`_ for more information.

Emit this signal to move a ``<section>`` to a specific position in the currently active score.

:kwarg string xmlid: The @xml:id attribute of the ``<section>`` to move. The section may or may
    not already be in the active score, but it must already be part of the document.
:kwarg int position: The requested new index of the section in the active score.

Do note that the ``<section>`` may not end up with the requested index because "position" is used
to determine the *new order* of the active score. For example, if you specify a "position" of `3`,
the section will always be placed between the sections currently at indices `2` and `3` (after `2`,
before `3`). However, if the section is already in the active score and the "position" is higher
than the current index, the actual new index will be one less than "position." In addition, any
"position" equal or greater to the current length of the active score will simply put the section
at the end.
'''

def _move_section_to(xmlid, position, **kwargs):
    '''
    Slot for the "MOVE_SECTION_TO" signal.

    The steps:
    1.) call lychee.document.document._move_section_to()
    2.) make a commit
    3.) run the outbound workflow
    '''
    # if we import these at module level it doesn't work because IDK
    import lychee
    from . import workflow

    with document.Document(lychee.get_repo_dir()) as doc:
        doc.move_section_to(xmlid, position)

    workm = workflow.WorkflowManager()
    workm._vcs_driver(pathnames=['score.mei'])  # if it just changes the order, that's just score.mei
    workm.run()
    workm.end()


MOVE_SECTION_TO.connect(_move_section_to)
