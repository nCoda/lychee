#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/vcs.py
# Purpose:                Signals for the "vcs" step.
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
Signals for the "vcs" step.
'''

import signalslot


START = signalslot.Signal()
'''
Emitted by the :class:`WorkflowManager` to begin processing during the "vcs" stage.
'''

STARTED = signalslot.Signal()
'''
Emitted by the ``lychee.vcs`` module, once it gains control flow and begins to determine how to
manage changes proposed to the musical document.
'''

BYPASSING_VCS = signalslot.Signal()
'''
This signal is emitted by the ``lychee.vcs`` module when the VCS system will be bypassed because of
configuration. A failure will be emitted through the ERROR signal.
'''

USING_VCS = signalslot.Signal()
'''
This signal is emitted by the ``lychee.vcs`` module when the VCS system will be used according to
the configuration system.
'''

PREINIT = signalslot.Signal()
'''
This signal is emitted before initializing a new repository.
'''

INIT = signalslot.Signal()
'''
This signal is emitted to cause a repository initialization. Such initialization may consist either
of creating a new, empty local repository, or of cloning a remote repository.
'''

POSTINIT = signalslot.Signal()
'''
This signal is emitted after a repository is initialized.
'''

PREADD = signalslot.Signal()
'''
This signal is emitted before new files are added to the VCS.
'''

ADD = signalslot.Signal()
'''
This signal is emitted to cause files to be added to the VCS.
'''

POSTADD = signalslot.Signal()
'''
This signal is emitted after files are added to the VCS, before committing.
'''

PRECOMMIT = signalslot.Signal()
'''
This signal is emitted by the ``lychee.vcs`` module just before making a new commit.
'''

COMMIT = signalslot.Signal()
'''
This signal is emitted to cause a new commit.
'''

POSTCOMMIT = signalslot.Signal()
'''
Emitted after the commit finishes, before the FINISH signal. This signal is for other modules that
want to do something after the commit, since only the :class:`WorkflowManager` should connect to
the FINISH signal.
'''

PREUPDATE_PERMANENT = signalslot.Signal()
'''
Emitted before UPDATE_PERMANENT.
'''

UPDATE_PERMANENT = signalslot.Signal()
'''
When a user chooses to "save" their progress, a "permanent" bookmark or branch will be moved
to the relevant revision.
'''

POSTUPDATE_PERMANENT = signalslot.Signal()
'''
Emitted after UPDATE_PERMANENT.
'''

PREEND_SESSION = signalslot.Signal()
'''
Emitted before END_SESSION.
'''

END_SESSION = signalslot.Signal()
'''
Emitted to end a session, which causes the revisions between the "permanent" and "session_permanent"
markers (branches or bookmarks) to be collapsed into a single revision, and (if relevant) the
repository's changes to be pushed to a remote server.
'''

POSTEND_SESSION = signalslot.Signal()
'''
Emitted after END_SESSION.
'''

PREHOP_TO_REVISION = signalslot.Signal()
'''
Emitted before HOP_TO_REVISION.
'''

HOP_TO_REVISION = signalslot.Signal()
'''
This signal is emitted to cause the repository to checkout a particular revision (changeset/commit)
and update all the views with the contents in that commit. In this situation, each outbound
converter is likely to receive the complete document, which eliminates the complexity of determining
which portions of the document to update.
'''

POSTHOP_TO_REVISION = signalslot.Signal()
'''
Emitted after HOP_TO_REVISION.
'''

FINISH = signalslot.Signal()
'''
Emitted by the ``lychee.vcs`` module, once its actions are complete, to return relevant information
to the :class:`WorkflowManager`.
'''

FINISHED = signalslot.Signal()
'''
This signal is emitted by the :class:`WorkflowManager` once it gains control flow after the
"vcs" step has finished.
'''

ERROR = signalslot.Signal()
'''
Emit this signal when an error occurs during the "vcs" stage.
'''
