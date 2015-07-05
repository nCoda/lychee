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

FINISH = signalslot.Signal()
'''
Emitted by the ``lychee.document`` module, once its actions are complete, to return relevant
information to the :class:`WorkflowManager`.
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
