#!/usr/bin/env python3

import signalslot

from lychee.signals import inbound


ACTION_START = signalslot.Signal(args=['inbound_format'])
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
    _INBOUND_PRECONVERSION = 1
    _INBOUND_CONVERSION_STARTED = 2
    _INBOUND_CONVERSION_FINISHED = 3
    _INBOUND_CONVERSION_ERROR = 4
    _INBOUND_PREVIEWS = 5
    _INBOUND_VIEWS_STARTED = 6
    _INBOUND_VIEWS_FINISHED = 7
    _INBOUND_VIEWS_ERROR = 8

    # connections
    # NB: they'll be connected as SIGNAL.connect(self.whatever)
    _CONNECTIONS = ((inbound.CONVERSION_STARTED, '_inbound_conversion_started'),
                    (inbound.CONVERSION_FINISH, '_inbound_conversion_finish'),
                    (inbound.CONVERSION_FINISHED, '_inbound_conversion_finished'),
                    (inbound.CONVERSION_ERROR, '_inbound_conversion_error'),
                    (inbound.VIEWS_STARTED, '_inbound_views_started'),
                    (inbound.VIEWS_FINISH, '_inbound_views_finish'),
                    (inbound.VIEWS_FINISHED, '_inbound_views_finished'),
                    (inbound.VIEWS_ERROR, '_inbound_views_error'),
                   )

    def __init__(self, kwargs):
        self._status = WorkflowManager._PRESTART
        self._inbound_format = kwargs['inbound_format'].lower() if 'inbound_format' in kwargs else None

        for signal, slot in WorkflowManager._CONNECTIONS:
            signal.connect(getattr(self, slot))

    def end(self):
        '''
        Disconnect all signals from this :class:`WorkflowManager` so it can be deleted. Does not
        attempt to ensure running processes are allowed to finish.
        '''
        for signal, slot in WorkflowManager._CONNECTIONS:
            signal.disconnect(getattr(self, slot))

    def run(self):
        '''
        Runs the "action" as required.
        '''
        try:
            self._run()
        finally:
            self.end()

    def _run(self):
        '''
        Actually does what :meth:`run` says it does. The other method is intended as a wrapper for
        this method, to ensure that :meth:`end` is always run, regardless of how this method exits.
        '''
        next_step = '(WorkflowManager continues to the next step)\n'

        # Inbound -------------------------------------------------------------
        if self._status is not WorkflowManager._PRESTART:
            print('ERROR starting the action')
            return

        self._status = WorkflowManager._INBOUND_PRECONVERSION
        self._choose_inbound_converter()
        inbound.CONVERSION_START.emit(inbound_format=self._inbound_format)

        if self._status is not WorkflowManager._INBOUND_CONVERSION_FINISHED:
            print('ERROR during inbound conversion')
            return
        print(next_step)

        self._status = WorkflowManager._INBOUND_PREVIEWS
        self._choose_inbound_views()
        inbound.VIEWS_START.emit()

        if self._status is not WorkflowManager._INBOUND_VIEWS_FINISHED:
            print('ERROR during inbound views processing')
            return
        print(next_step)

        # Document ------------------------------------------------------------

        # Outbound ------------------------------------------------------------

    # ----

    def _choose_inbound_converter(self):
        '''
        Choose an inbound converter based on self._inbound_format.
        '''
        # TODO: can I move this import to the top of the file without causing cyclic import errors?
        from lychee import converters
        conv_dict = {'lilypond': converters.ly_to_mei.convert}

        if self._inbound_format:
            if self._inbound_format in conv_dict:
                inbound.CONVERSION_START.connect(conv_dict[self._inbound_format])
            else:
                inbound.CONVERSION_START.connect(mock_converter)
        else:
            self._status = WorkflowManager._INBOUND_CONVERSION_ERROR

    def _choose_inbound_views(self):
        '''
        Choose an inbound views function based on ??? and the conversion result.
        '''
        inbound.VIEWS_START.connect(mock_views)

    # ----

    def _inbound_conversion_started(self, **kwargs):
        print('inbound conversion started')
        self._status = WorkflowManager._INBOUND_CONVERSION_STARTED

    def _inbound_conversion_finish(self, **kwargs):
        print('inbound conversion finishing')
        if self._status is WorkflowManager._INBOUND_CONVERSION_STARTED:
            self._status = WorkflowManager._INBOUND_CONVERSION_FINISHED
        else:
            print('ERROR during inbound conversion')
        inbound.CONVERSION_FINISHED.emit()

    def _inbound_conversion_finished(self, **kwargs):
        '''
        Called when inbound.CONVERSION_FINISHED is emitted, for logging and debugging.
        '''
        print('inbound conversion finished')

    def _inbound_conversion_error(self, **kwargs):
        print('ERROR during inbound conversion')
        self._status = WorkflowManager._INBOUND_CONVERSION_ERROR

    def _inbound_views_started(self, **kwargs):
        print('inbound views started')
        self._status = WorkflowManager._INBOUND_VIEWS_STARTED

    def _inbound_views_finish(self, **kwargs):
        print('inbound views finishing'.format(kwargs))
        if self._status is WorkflowManager._INBOUND_VIEWS_STARTED:
            self._status = WorkflowManager._INBOUND_VIEWS_FINISHED
        else:
            print('ERROR during inbound views processing')
        inbound.VIEWS_FINISHED.emit()

    def _inbound_views_finished(self, **kwargs):
        '''
        Called when inbound.VIEWS_FINISHED is emitted, for logging and debugging.
        '''
        print('inbound views finished')

    def _inbound_views_error(self, **kwargs):
        print('ERROR during inbound views processing')
        self._status = WorkflowManager._INBOUND_VIEWS_ERROR


#--------------------------------------------------------------------------------------------------#
# Set up the "inbound" step's workflow.                                                            #
#--------------------------------------------------------------------------------------------------#

# mocks of other modules
def mock_converter(**kwargs):
    inbound.CONVERSION_STARTED.emit()
    print('mock_converter({})'.format(kwargs))
    #inbound.CONVERSION_ERROR.emit()
    inbound.CONVERSION_FINISH.emit()
    print('mock_converter() after finish signal')

def mock_views(**kwargs):
    inbound.VIEWS_STARTED.emit()
    print('mock_views({})'.format(kwargs))
    #inbound.VIEWS_ERROR.emit()
    inbound.VIEWS_FINISH.emit()
    print('mock_views() after finish signal')

# actual signal connections
def thing(**kwargs):
    workm = WorkflowManager(kwargs)
    workm.run()
    del workm

ACTION_START.connect(thing)
