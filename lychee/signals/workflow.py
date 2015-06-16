#!/usr/bin/env python3

from lychee import converters
from lychee.signals import inbound


class WorkflowManager(object):
    '''
    It manages the workflow.
    '''

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

    # the following members must be present in "kwargs" to __init__() or it will fail.
    _REQD_KWARGS = ('dtype', 'doc')

    def __init__(self, kwargs):
        self._status = WorkflowManager._PRESTART
        # check the required kwargs
        for kwarg in WorkflowManager._REQD_KWARGS:
            if kwarg not in kwargs:
                raise KeyError('Missing required kwarg to WorkflowManager: {}'.format(kwarg))

        # set instance settings
        # inbound data type
        self._i_dtype = kwargs['dtype'].lower()
        # inbound document
        self._i_doc = kwargs['doc'].lower()

        for signal, slot in WorkflowManager._CONNECTIONS:
            signal.connect(getattr(self, slot))

    def end(self):
        '''
        Disconnect all signals from this :class:`WorkflowManager` so it can be deleted. Does not
        attempt to ensure running processes are allowed to finish.
        '''
        for signal, slot in WorkflowManager._CONNECTIONS:
            signal.disconnect(getattr(self, slot))
        for slot in [converters.ly_to_mei.convert, converters.abjad_to_mei.convert, converters.mei_to_lmei.convert]:
            inbound.CONVERSION_START.disconnect(slot)

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
        inbound.CONVERSION_START.emit(dtype=self._i_dtype, doc=self._i_doc)

        if self._status is not WorkflowManager._INBOUND_CONVERSION_FINISHED:
            if self._status is not WorkflowManager._INBOUND_CONVERSION_ERROR:
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
        Choose an inbound converter based on self._i_dtype.
        '''
        if self._i_dtype:
            if self._i_dtype in converters.INBOUND_CONVERTERS:
                inbound.CONVERSION_START.connect(converters.INBOUND_CONVERTERS[self._i_dtype])
            else:
                inbound.CONVERSION_ERROR.emit(msg='Invalid "dtype"')
        else:
            inbound.CONVERSION_ERROR.emit(msg='Missing "dtype"')

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
        self._status = WorkflowManager._INBOUND_CONVERSION_ERROR
        if 'msg' in kwargs:
            print(kwargs['msg'])
        else:
            print('ERROR during inbound conversion')

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
        self._status = WorkflowManager._INBOUND_VIEWS_ERROR
        if 'msg' in kwargs:
            print(kwargs['msg'])
        else:
            print('ERROR during inbound views processing')


#--------------------------------------------------------------------------------------------------#
# Set up the "inbound" step's workflow.                                                            #
#--------------------------------------------------------------------------------------------------#

def mock_views(**kwargs):
    inbound.VIEWS_STARTED.emit()
    print('mock_views({})'.format(kwargs))
    #inbound.VIEWS_ERROR.emit()
    inbound.VIEWS_FINISH.emit()
    print('mock_views() after finish signal')
