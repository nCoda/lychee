#!/usr/bin/env python3

import signalslot

import inbound  #TODO: from lychee.signals import inbound


ACTION_START = signalslot.Signal()
'''
Emit this signal to start an "action" through Lychee.
'''


class WorkflowManager(object):
    '''
    It manages the workflow.
    '''
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
    _CONNECTIONS = ((inbound.CONVERSION_STARTED, '_inbound_conversion_started'),
                    (inbound.CONVERSION_FINISH, '_inbound_conversion_finish'),
                    (inbound.CONVERSION_FINISHED, '_inbound_conversion_finished'),
                    (inbound.VIEWS_STARTED, '_inbound_views_started'),
                    (inbound.VIEWS_FINISH, '_inbound_views_finish'),
                    (inbound.VIEWS_FINISHED, '_inbound_views_finished'),
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
        inbound.CONVERSION_START.emit()

        if self._status is not WorkflowManager._INBOUND_CONVERT_FINISH:
            print('failure during inbound conversion')
            return

        self._status = WorkflowManager._INBOUND_PREVIEWS
        self._choose_inbound_views()
        inbound.VIEWS_START.emit()

    def _choose_inbound_converter(self):
        '''
        Choose an inbound converter based on self._kwargs.
        '''
        inbound.CONVERSION_START.connect(mock_converter)

    def _choose_inbound_views(self):
        '''
        Choose an inbound views function based on self._kwargs and the conversion result.
        '''
        inbound.VIEWS_START.connect(mock_views)

    def _inbound_conversion_started(self, **kwargs):
        print('inbound conversion started')
        self._status = WorkflowManager._INBOUND_CONVERT

    def _inbound_conversion_finish(self, **kwargs):
        print('inbound conversion finishing')
        self._status = WorkflowManager._INBOUND_CONVERT_FINISH
        inbound.CONVERSION_FINISHED.emit()

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
        inbound.VIEWS_FINISHED.emit()

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
    inbound.CONVERSION_STARTED.emit()
    print('mock_converter({})'.format(kwargs))
    inbound.CONVERSION_FINISH.emit()
    print('mock_converter() after finish signal')

def mock_views(**kwargs):
    inbound.VIEWS_STARTED.emit()
    print('mock_views({})'.format(kwargs))
    inbound.VIEWS_FINISH.emit()
    print('mock_views() after finish signal')

# actual signal connections
def thing(**kwargs):
    workm = WorkflowManager(kwargs)
    workm.run()

ACTION_START.connect(thing)

# this is what starts a test "action"
ACTION_START.emit()
