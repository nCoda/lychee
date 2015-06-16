#!/usr/bin/env python3

import signalslot


CONVERSION_START = signalslot.Signal(args=['document'])
'''
Emitted when the inbound conversion will start (i.e., this signal is emitted to cause a converter
module to start the conversion).

:kwarg object document: The inbound musical document. The required type is determined by each
    converter module individually.
'''

CONVERSION_STARTED = signalslot.Signal()
'''
Emitted as soon as the inbound conversion has started (i.e., as soon as the converter module has
begun to process data).
'''

CONVERSION_FINISH = signalslot.Signal(args=['converted'])
'''
Emitted just before the inbound conversion finishes (i.e., emitting this signal is the last action
of an inbound conversion module).

:kwarg converted: The inbound musical document, converted to Lychee-MEI format.
:type converted: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
'''

CONVERSION_FINISHED = signalslot.Signal()
'''
Emitted when the inbound conversion is finished, before any "views" information is processed.
'''

CONVERSION_ERROR = signalslot.Signal(args=['msg'])
'''
Emitted when there's an error during the in bound conversion step.

:kwarg str msg: A descriptive error message for the log file.
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

VIEWS_ERROR = signalslot.Signal(args=['msg'])
'''
Emitted when there's an error while processing the inbound view.

:kwarg str msg: A descriptive error message for the log file.
'''
