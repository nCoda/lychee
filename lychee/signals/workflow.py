#!/usr/bin/env python3

from lychee import converters, vcs
from lychee.signals import inbound, document


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
    _DOCUMENT_PRESTART = 100
    _DOCUMENT_STARTED = 101
    _DOCUMENT_FINISHED = 102
    _DOCUMENT_ERROR = 103

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
                    (document.STARTED, '_document_started'),
                    (document.FINISH, '_document_finish'),
                    (document.FINISHED, '_document_finished'),
                    (document.ERROR, '_document_error'),
                   )

    def __init__(self, dtype, doc, **kwargs):
        self._status = WorkflowManager._PRESTART

        # set instance settings
        # inbound data type
        self._i_dtype = dtype.lower()
        # inbound document
        self._i_doc = doc.lower()
        # inbound document after conversion
        self._converted = None
        # inbound information from the "views" module
        self._i_views = None

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
        inbound.CONVERSION_START.emit(document=self._i_doc)

        if self._status is not WorkflowManager._INBOUND_CONVERSION_FINISHED:
            if self._status is not WorkflowManager._INBOUND_CONVERSION_ERROR:
                print('ERROR during inbound conversion')
            return
        print(next_step)

        self._status = WorkflowManager._INBOUND_PREVIEWS
        self._choose_inbound_views()
        inbound.VIEWS_START.emit(dtype=self._i_dtype, doc=self._i_doc, converted=self._converted)

        if self._status is not WorkflowManager._INBOUND_VIEWS_FINISHED:
            print('ERROR during inbound views processing')
            return
        print(next_step)

        # Document ------------------------------------------------------------
        self._status = WorkflowManager._DOCUMENT_PRESTART
        document.START.emit()

        if self._status is not WorkflowManager._DOCUMENT_FINISHED:
            if self._status is not WorkflowManager._DOCUMENT_ERROR:
                print('ERROR during "document" step')
            return
        print(next_step)

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
        # TODO: do we need this method?
        pass

    # ----

    def _inbound_conversion_started(self, **kwargs):
        print('inbound conversion started')
        self._status = WorkflowManager._INBOUND_CONVERSION_STARTED

    def _inbound_conversion_finish(self, converted, **kwargs):
        print('inbound conversion finishing')
        if self._status is WorkflowManager._INBOUND_CONVERSION_STARTED:
            if converted is None:
                inbound.CONVERSION_ERROR.emit(msg='Inbound converter did not return L-MEI document')
            else:
                print('\t(we got "{}")'.format(converted))
                self._converted = converted
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

    def _inbound_views_finish(self, views_info, **kwargs):
        print('inbound views finishing'.format(kwargs))
        if self._status is WorkflowManager._INBOUND_VIEWS_STARTED:
            if views_info is None:
                inbound.VIEWS_ERROR.emit(msg='Inbound views processing did not return views_info')
            else:
                print('\t(we got "{}")'.format(views_info))
                self._i_views = views_info
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

    def _document_started(self, **kwargs):
        print('document started')
        self._status = WorkflowManager._DOCUMENT_STARTED

    def _document_finish(self, **kwargs):
        print('document finishing'.format(kwargs))
        if self._status is WorkflowManager._DOCUMENT_STARTED:
            if 5 is None:  # TODO: put in the appropriate arg here
                document.ERROR.emit(msg='Document processing did not return views_info')
            else:
                self._status = WorkflowManager._DOCUMENT_FINISHED
        else:
            print('ERROR during document processing')
        document.FINISHED.emit()

    def _document_finished(self, **kwargs):
        '''
        Called when document.FINISHED is emitted, for logging and debugging.
        '''
        print('document processing finished')

    def _document_error(self, **kwargs):
        self._status = WorkflowManager._DOCUMENT_ERROR
        if 'msg' in kwargs:
            print(kwargs['msg'])
        else:
            print('ERROR during document processing')
