#!/usr/bin/env python3

import signalslot


START = signalslot.Signal()
'''
Emitted by the :class:`WorkflowManager` to begin processing during the "document" stage.
'''

STARTED = signalslot.Signal()
'''
Emitted by the ``lychee.vcs`` module, once it gains control flow and begins to determine how to
manage changes proposed to the musical document.
'''

BYPASS_VCS = signalslot.Signal()
'''
This signal is emitted by the ``lychee.vcs`` module when the VCS system will be bypassed because of
configuration. A failure will be emitted through the ERROR signal.
'''

USING_VCS = signalslot.Signal()
'''
This signal is emitted by the ``lychee.vcs`` module when the VCS system will be used according to
the configuration system.
'''

HG_INIT = signalslot.Signal()
'''
This signal is emitted by the ``lychee.vcs`` module just before initializing a new Mercurial
repository.
'''

HG_ADD = signalslot.Signal()
'''
This signal is emitted by the ``lychee.vcs`` module just before a newly-created file is added to
the repository.
'''

HG_COMMIT = signalslot.Signal()
'''
This signals is emitted by the ``lychee.vcs`` module just before running the ``hg commit`` command.
'''

POSTCOMMIT = signalslot.Signal()
'''
Emitted after the commit finishes, before the FINISH signal. This signal is for other
modules that want to do something after the commit, since only the :class:`WorkflowManager` should
do something after the FINISH signal is emitted.
'''

FINISH = signalslot.Signal()
'''
Emitted by the ``lychee.vcs`` module, once its actions are complete, to return relevant information
to the :class:`WorkflowManager`.
'''

FINISHED = signalslot.Signal()
'''
This signal is emitted by the :class:`WorkflowManager` once it gains control flow after the
"document" step has finished.
'''

ERROR = signalslot.Signal()
'''
Emit this signal when an error occurs during the "document" stage.
'''
