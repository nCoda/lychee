#!/usr/bin/env python3

import signalslot

ACTION_START = signalslot.Signal()
'''
Emit this signal to start an "action" through Lychee.
'''

CONVERSION_START = signalslot.Signal()
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


#--------------------------------------------------------------------------------------------------#
# Set up the "inbound" step's workflow.                                                            #
#--------------------------------------------------------------------------------------------------#
class WorkflowManager(object):
    '''
    It manages the workflow.
    '''
    # TODO: move this into its own module; should it be a submodule of "signals" or not?
    # TODO: add support for the error states

    # statusses
    _PRESTART = 0
    _INBOUND_PRECONVERT = 1
    _INBOUND_CONVERT = 2
    _INBOUND_CONVERT_FAIL = 3
    _INBOUND_CONVERT_FINISH = 4
    _INBOUND_PREVIEWS = 5
    _INBOUND_VIEWS = 6
    _INBOUND_VIEWS_FAIL = 7
    _INBOUND_VIEWS_FINISH = 8

    # connections
    # NB: they'll be connected as SIGNAL.connect(self.whatever)
    _CONNECTIONS = ((CONVERSION_STARTED, '_inbound_conversion_started'),
                    (CONVERSION_FINISH, '_inbound_conversion_finish'),
                    (CONVERSION_FINISHED, '_inbound_conversion_finished'),
                    (VIEWS_STARTED, '_inbound_views_started'),
                    (VIEWS_FINISH, '_inbound_views_finish'),
                    (VIEWS_FINISHED, '_inbound_views_finished'),
                   )

    def __init__(self, kwargs):
        self._status = WorkflowManager._PRESTART
        self._kwargs = kwargs
        for signal, slot in WorkflowManager._CONNECTIONS:
            signal.connect(getattr(self, slot))

    def run(self):
        '''
        Runs the "action" as required.
        '''
        if self._status is not WorkflowManager._PRESTART:
            print('failure starting the action')
            return

        self._status = WorkflowManager._INBOUND_PRECONVERT
        self._choose_inbound_converter()
        CONVERSION_START.emit()

        if self._status is not WorkflowManager._INBOUND_CONVERT_FINISH:
            print('failure during inbound conversion')
            return

        self._status = WorkflowManager._INBOUND_PREVIEWS
        self._choose_inbound_views()
        VIEWS_START.emit()

    def _choose_inbound_converter(self):
        '''
        Choose an inbound converter based on self._kwargs.
        '''
        CONVERSION_START.connect(mock_converter)

    def _choose_inbound_views(self):
        '''
        Choose an inbound views function based on self._kwargs and the conversion result.
        '''
        VIEWS_START.connect(mock_views)

    def _inbound_conversion_started(self, **kwargs):
        print('inbound conversion started')
        self._status = WorkflowManager._INBOUND_CONVERT

    def _inbound_conversion_finish(self, **kwargs):
        print('inbound conversion finishing')
        self._status = WorkflowManager._INBOUND_CONVERT_FINISH
        CONVERSION_FINISHED.emit()

    def _inbound_conversion_finished(self, **kwargs):
        '''
        Called when inbound.CONVERSION_FINISHED is emitted, for logging and debugging.
        '''
        print('inbound conversion finished')

    def _inbound_views_started(self, **kwargs):
        print('inbound views started')
        self._status = WorkflowManager._INBOUND_VIEWS

    def _inbound_views_finish(self, **kwargs):
        print('inbound views finishing'.format(kwargs))
        self._status = WorkflowManager._INBOUND_VIEWS_FINISH
        VIEWS_FINISHED.emit()

    def _inbound_views_finished(self, **kwargs):
        '''
        Called when inbound.VIEWS_FINISHED is emitted, for logging and debugging.
        '''
        print('inbound views finished')


#--------------------------------------------------------------------------------------------------#
# Set up the "inbound" step's workflow.                                                            #
#--------------------------------------------------------------------------------------------------#

# mocks of other modules
def mock_converter(**kwargs):
    CONVERSION_STARTED.emit()
    print('mock_converter({})'.format(kwargs))
    CONVERSION_FINISH.emit()
    print('mock_converter() after finish signal')

def mock_views(**kwargs):
    VIEWS_STARTED.emit()
    print('mock_views({})'.format(kwargs))
    VIEWS_FINISH.emit()
    print('mock_views() after finish signal')

# actual signal connections
def thing(**kwargs):
    workm = WorkflowManager(kwargs)
    workm.run()

ACTION_START.connect(thing)

# this is what starts a test "action"
ACTION_START.emit()
