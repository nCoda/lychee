#!/usr/bin/env python3

import signalslot


CONVERSION_START = signalslot.Signal(args=['inbound_format'])
'''
Emitted when the inbound conversion will start (i.e., this signal is emitted to cause a converter
module to start the conversion).
'''

CONVERSION_STARTED = signalslot.Signal()
'''
Emitted as soon as the inbound conversion has started (i.e., as soon as the converter module has
begun to process data).
'''

CONVERSION_FINISH = signalslot.Signal()
'''
Emitted just before the inbound conversion finishes (i.e., emitting this signal is the last action
of an inbound conversion module).
'''

CONVERSION_FINISHED = signalslot.Signal()
'''
Emitted when the inbound conversion is finished, before any "views" information is processed.
'''

CONVERSION_ERROR = signalslot.Signal()
'''
Emitted when there's an error during the in bound conversion step.
'''

VIEWS_START = signalslot.Signal()
'''
Emitted when the inbound view processing will start (i.e., this signal is emitted to cause the views
module to start its bit).
'''

VIEWS_STARTED = signalslot.Signal()
'''
Emitted as soon as the views module begins its inbound processing (i.e., as soon as the views module
has begun to process data).
'''

VIEWS_FINISH = signalslot.Signal()
'''
Emitted just before the views module finishes its inbound processing (i.e., just before the views
module returns).
'''

VIEWS_FINISHED = signalslot.Signal()
'''
Emitted when the inbound views processing is finished.
'''

VIEWS_ERROR = signalslot.Signal()
'''
Emitted when there's an error while processing the inbound view.
'''
