#!/usr/bin/env python3

'''
Note that you must import the :mod:`lychee.signals.workflow` separately because it isn't imported
by ``from lychee import *`` by default, because it caused too much trouble.
'''

__all__ = ['inbound']

import signalslot
from lychee.signals import *


ACTION_START = signalslot.Signal(args=['inbound_format'])
'''
Emit this signal to start an "action" through Lychee.
'''


def action_starter(**kwargs):
    '''
    Default connection for the ACTION_START signal.
    '''
    # NB: workflow imported here because, in the main module, it would cause circular import probs
    from . import workflow
    workm = workflow.WorkflowManager(kwargs)
    workm.run()
    del workm

ACTION_START.connect(action_starter)
