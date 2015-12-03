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

from . import signal


START = signal.Signal(args=['pathnames'], name='vcs.START')
'''
Emitted by the :class:`WorkflowManager` to begin processing during the "vcs" stage.

:kwarg pathnames: A list of pathnames that were modified in the most recent write-to-disk.
:type pathnames: list of str
'''

STARTED = signal.Signal(name='vcs.STARTED')
'''
Emitted by the ``lychee.vcs`` module, once it gains control flow and begins to determine how to
manage changes proposed to the musical document.
'''

BYPASSING_VCS = signal.Signal(name='vcs.BYPASSING_VCS')
'''
This signal is emitted by the ``lychee.vcs`` module when the VCS system will be bypassed because of
configuration. A failure will be emitted through the ERROR signal.
'''

USING_VCS = signal.Signal(name='vcs.USING_VCS')
'''
This signal is emitted by the ``lychee.vcs`` module when the VCS system will be used according to
the configuration system.
'''

PREINIT = signal.Signal(name='vcs.PREINIT')
'''
This signal is emitted before initializing a new repository.
'''

INIT = signal.Signal(name='vcs.INIT')
'''
This signal is emitted to cause a repository initialization. Such initialization may consist either
of creating a new, empty local repository, or of cloning a remote repository.
'''

POSTINIT = signal.Signal(name='vcs.POSTINIT')
'''
This signal is emitted after a repository is initialized.
'''

PREADD = signal.Signal(name='vcs.PREADD')
'''
This signal is emitted before new files are added to the VCS.
'''

ADD = signal.Signal(name='vcs.ADD')
'''
This signal is emitted to cause files to be added to the VCS.
'''

POSTADD = signal.Signal(name='vcs.POSTADD')
'''
This signal is emitted after files are added to the VCS, before committing.
'''

PRECOMMIT = signal.Signal(name='vcs.PRECOMMIT')
'''
This signal is emitted by the ``lychee.vcs`` module just before making a new commit.
'''

COMMIT = signal.Signal(name='vcs.COMMIT')
'''
This signal is emitted to cause a new commit.
'''

POSTCOMMIT = signal.Signal(name='vcs.POSTCOMMIT')
'''
Emitted after the commit finishes, before the FINISH signal. This signal is for other modules that
want to do something after the commit, since only the :class:`WorkflowManager` should connect to
the FINISH signal.
'''

PREUPDATE_PERMANENT = signal.Signal(name='vcs.PREUPDATE_PERMANENT')
'''
Emitted before UPDATE_PERMANENT.
'''

UPDATE_PERMANENT = signal.Signal(name='vcs.UPDATE_PERMANENT')
'''
When a user chooses to "save" their progress, a "permanent" bookmark or branch will be moved
to the relevant revision.
'''

POSTUPDATE_PERMANENT = signal.Signal(name='vcs.POSTUPDATE_PERMANENT')
'''
Emitted after UPDATE_PERMANENT.
'''

PREEND_SESSION = signal.Signal(name='vcs.PREEND_SESSION')
'''
Emitted before END_SESSION.
'''

END_SESSION = signal.Signal(name='vcs.END_SESSION')
'''
Emitted to end a session, which causes the revisions between the "permanent" and "session_permanent"
markers (branches or bookmarks) to be collapsed into a single revision, and (if relevant) the
repository's changes to be pushed to a remote server.
'''

POSTEND_SESSION = signal.Signal(name='vcs.POSTEND_SESSION')
'''
Emitted after END_SESSION.
'''

PREHOP_TO_REVISION = signal.Signal(name='vcs.PREHOP_TO_REVISION')
'''
Emitted before HOP_TO_REVISION.
'''

HOP_TO_REVISION = signal.Signal(name='vcs.HOP_TO_REVISION')
'''
This signal is emitted to cause the repository to checkout a particular revision (changeset/commit)
and update all the views with the contents in that commit. In this situation, each outbound
converter is likely to receive the complete document, which eliminates the complexity of determining
which portions of the document to update.
'''

POSTHOP_TO_REVISION = signal.Signal(name='vcs.POSTHOP_TO_REVISION')
'''
Emitted after HOP_TO_REVISION.
'''

FINISH = signal.Signal(name='vcs.FINISH')
'''
Emitted by the ``lychee.vcs`` module, once its actions are complete, to return relevant information
to the :class:`WorkflowManager`.
'''

FINISHED = signal.Signal(name='vcs.FINISHED')
'''
This signal is emitted by the :class:`WorkflowManager` once it gains control flow after the
"vcs" step has finished.
'''

ERROR = signal.Signal(name='vcs.ERROR')
'''
Emit this signal when an error occurs during the "vcs" stage.
'''
