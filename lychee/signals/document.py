#!/usr/bin/env python3

import signalslot


DOCUMENT_START = signalslot.Signal()
'''
Emitted by the :class:`WorkflowManager` to begin processing during the "document" stage.
'''

DOCUMENT_STARTED = signalslot.Signal()
'''
Emitted by the ``lychee.vcs`` module, once it gains control flow and begins to determine how to
manage changes proposed to the musical document.
'''

DOCUMENT_BYPASS_VCS = signalslot.Signal()
'''
This signal is emitted by the ``lychee.vcs`` module when the VCS system will be bypassed because of
configuration. A failure will be emitted through the DOCUMENT_ERROR signal.
'''

DOCUMENT_USING_VCS = signalslot.Signal()
'''
This signal is emitted by the ``lychee.vcs`` module when the VCS system will be used according to
the configuration system.
'''

DOCUMENT_HG_INIT = signalslot.Signal()
'''
This signal is emitted by the ``lychee.vcs`` module just before initializing a new Mercurial
repository.
'''

DOCUMENT_HG_ADD = signalslot.Signal()
'''
This signal is emitted by the ``lychee.vcs`` module just before a newly-created file is added to
the repository.
'''

DOCUMENT_HG_COMMIT = signalslot.Signal()
'''
This signals is emitted by the ``lychee.vcs`` module just before running the ``hg commit`` command.
'''

DOCUMENT_POSTCOMMIT = signalslot.Signal()
'''
Emitted after the commit finishes, before the DOCUMENT_FINISH signal. This signal is for other
modules that want to do something after the commit, since only the :class:`WorkflowManager` should
do something after the DOCUMENT_FINISH signal is emitted.
'''

DOCUMENT_FINISH = signalslot.Signal()
'''
Emitted by the ``lychee.vcs`` module, once its actions are complete, to return relevant information
to the :class:`WorkflowManager`.
'''

DOCUMENT_FINISHED = signalslot.Signal()
'''
This signal is emitted by the :class:`WorkflowManager` once it gains control flow after the
"document" step has finished.
'''

DOCUMENT_ERROR = signalslot.Signal()
'''
Emit this signal when an error occurs during the "document" stage.
'''
