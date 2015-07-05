#!/usr/bin/env python3

'''
Note that you must import the :mod:`lychee.signals.workflow` separately because it isn't imported
by ``from lychee import *`` by default, because it caused too much trouble.
'''

__all__ = ['inbound', 'document', 'vcs', 'outbound']

import signalslot
from lychee.signals import *


ACTION_START = signalslot.Signal(args=['dtype', 'doc'])
'''
Emit this signal to start an "action" through Lychee.

:kwarg str dtype: The format (data type) of the inbound musical document. LilyPond, Abjad, etc.
:kwarg object doc: The inbound musical document. The required type is determined by each converter
    module individually.
'''


def action_starter(dtype, doc, **kwargs):
    '''
    Default connection for the ACTION_START signal.
    '''
    # NB: workflow imported here because, in the main module, it would cause circular import probs
    from . import workflow
    workm = workflow.WorkflowManager(dtype, doc)
    workm.run()
    del workm

ACTION_START.connect(action_starter)
