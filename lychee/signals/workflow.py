#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/workflow.py
# Purpose:                Control the workflow progression through an "action."
#
# Copyright (C) 2016 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
'''
Control the workflow progression through an "action."
'''


import lychee
from lychee import converters
from lychee import document
from lychee.signals import inbound, vcs, outbound


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
    _OUTBOUND_PRESTART = 200
    _OUTBOUND_VIEWS_STARTED = 202
    _OUTBOUND_VIEWS_FINISHED = 203
    _OUTBOUND_VIEWS_ERROR = 204
    _OUTBOUND_CONVERSIONS_STARTED = 205
    _OUTBOUND_CONVERSIONS_FINISHED = 206
    _OUTBOUND_CONVERSIONS_ERROR = 207
    _OUTBOUND_FINISHING = 208

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
                    (vcs.START, '_vcs_driver'),
                    (vcs.FINISHED, '_vcs_finished'),
                    (vcs.ERROR, '_vcs_error'),
                    (outbound.VIEWS_STARTED, '_outbound_views_started'),
                    (outbound.VIEWS_FINISH, '_outbound_views_finish'),
                    (outbound.VIEWS_FINISHED, '_outbound_views_finished'),
                    (outbound.VIEWS_ERROR, '_outbound_views_error'),
                    (outbound.CONVERSION_STARTED, '_outbound_conversion_started'),
                    (outbound.CONVERSION_FINISH, '_outbound_conversion_finish'),
                    (outbound.CONVERSION_FINISHED, '_outbound_conversion_finished'),
                    (outbound.CONVERSION_ERROR, '_outbound_conversion_error'),
                   )

    def __init__(self, dtype=None, doc=None, session=None, **kwargs):
        if session is None:
            raise NotImplementedError('WorkflowManager requires a "session" argument!')
        else:
            self._session = session

        self._status = WorkflowManager._PRESTART

        # set instance settings
        # whether to do the "inbound" conversion step
        self._do_inbound = False

        # inbound data type
        self._i_dtype = None
        # inbound document
        self._i_doc = None
        # inbound document after conversion
        self._converted = None
        # inbound information from the "views" module
        self._i_views = None

        if dtype is not None and doc is not None:  # just in case we can lxml.Element
            lychee.log('WorkflowManager will do a full conversion', 'debug')
            self._do_inbound = True
            self._i_dtype = dtype.lower()
            self._i_doc = doc
        else:
            lychee.log('WorkflowManager will only do the outbound step', 'debug')

        # list of output "dtype" required
        self._o_dtypes = []
        # mapping from dtype to its outbound views_info
        self._o_views_info = {}
        # mapping from dtype to its outbound converted form
        self._o_converted = {}
        # dtype of the currently running outbound converter
        self._o_running_converter = None

        for signal, slot in WorkflowManager._CONNECTIONS:
            signal.connect(getattr(self, slot))

    def end(self):
        '''
        Disconnect all signals from this :class:`WorkflowManager` so it can be deleted. Does not
        attempt to ensure running processes are allowed to finish.
        '''
        for signal, slot in WorkflowManager._CONNECTIONS:
            signal.disconnect(getattr(self, slot))
        self._flush_inbound_converters()
        self._flush_outbound_converters()

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
        next_step = '(WorkflowManager continues to the next step)\n------------------------------------------\n'

        # I know it only seems to tell us whether to do the "inbound" step, but the Document and VCS
        # steps only make sense when there was an inbound change!
        if self._do_inbound:
            # Inbound -------------------------------------------------------------
            if self._status is not WorkflowManager._PRESTART:
                lychee.log('ERROR starting the action')
                return

            self._status = WorkflowManager._INBOUND_PRECONVERSION
            self._choose_inbound_converter()
            inbound.CONVERSION_START.emit(document=self._i_doc)

            if self._status is not WorkflowManager._INBOUND_CONVERSION_FINISHED:
                if self._status is not WorkflowManager._INBOUND_CONVERSION_ERROR:
                    lychee.log('ERROR during inbound conversion')
                return
            lychee.log(next_step)

            self._status = WorkflowManager._INBOUND_PREVIEWS
            self._choose_inbound_views()
            inbound.VIEWS_START.emit(dtype=self._i_dtype, doc=self._i_doc, converted=self._converted)

            if self._status is not WorkflowManager._INBOUND_VIEWS_FINISHED:
                lychee.log('ERROR during inbound views processing')
                return
            lychee.log(next_step)

            # Document ------------------------------------------------------------
            self._modified_pathnames = document._document_processor(
                converted=self._converted,
                session=self._session)
            lychee.log(next_step)

            # VCS -----------------------------------------------------------------
            # NOTE: why bother with the signal at all? Why not just call self._vcs_driver() ? Because
            # this way we can enable/disable the VCS step by changing who's listening to vcs.START.
            vcs.START.emit(pathnames=self._modified_pathnames)
            vcs.FINISHED.emit()
            lychee.log(next_step)

        # Outbound ------------------------------------------------------------
        self._status = WorkflowManager._OUTBOUND_PRESTART

        # determine which formats are required
        self._o_dtypes = self._session.registrar.get_registered_formats()
        lychee.log('Currently registered outbound dtypes: {}'.format(self._o_dtypes))

        self._the_outbound_stuff(self._o_dtypes)


    # ----

    def _flush_inbound_converters(self):
        '''
        Clear any inbound converters that may be connected.
        '''
        for each_converter in converters.INBOUND_CONVERTERS.values():
            inbound.CONVERSION_START.disconnect(each_converter)

    def _flush_outbound_converters(self):
        '''
        Clear any outbound converters that may be connected.
        '''
        for each_converter in converters.OUTBOUND_CONVERTERS.values():
            outbound.CONVERSION_START.disconnect(each_converter)

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
        pass

    def _choose_outbound_converter(self, dtype):
        '''
        Choose an outbound converter based on the "dtype" argument. This should be called once for
        every outbound converter format required.
        '''
        self._flush_outbound_converters()
        if dtype in converters.OUTBOUND_CONVERTERS:
            outbound.CONVERSION_START.connect(converters.OUTBOUND_CONVERTERS[dtype])
        else:
            outbound.CONVERSION_ERROR.emit(msg='Invalid "dtype" ({})'.format(dtype))

    # ----

    def _inbound_conversion_started(self, **kwargs):
        lychee.log('inbound conversion started')
        lychee.log('inbound conversion started')
        self._status = WorkflowManager._INBOUND_CONVERSION_STARTED

    def _inbound_conversion_finish(self, converted, **kwargs):
        lychee.log('inbound conversion finishing')
        if self._status is WorkflowManager._INBOUND_CONVERSION_STARTED:
            if converted is None:
                inbound.CONVERSION_ERROR.emit(msg='Inbound converter did not return L-MEI document')
            else:
                lychee.log('\t(we got "{}")'.format(converted))
                self._converted = converted
                self._status = WorkflowManager._INBOUND_CONVERSION_FINISHED
        else:
            lychee.log('ERROR during inbound conversion')
        inbound.CONVERSION_FINISHED.emit()

    def _inbound_conversion_finished(self, **kwargs):
        '''
        Called when inbound.CONVERSION_FINISHED is emitted, for logging and debugging.
        '''
        lychee.log('inbound conversion finished')

    def _inbound_conversion_error(self, **kwargs):
        self._status = WorkflowManager._INBOUND_CONVERSION_ERROR
        if 'msg' in kwargs:
            lychee.log(kwargs['msg'])
        else:
            lychee.log('ERROR during inbound conversion')

    def _inbound_views_started(self, **kwargs):
        lychee.log('inbound views started')
        self._status = WorkflowManager._INBOUND_VIEWS_STARTED

    def _inbound_views_finish(self, views_info, **kwargs):
        lychee.log('inbound views finishing'.format(kwargs))
        if self._status is WorkflowManager._INBOUND_VIEWS_STARTED:
            if views_info is None:
                inbound.VIEWS_ERROR.emit(msg='Inbound views processing did not return views_info')
            else:
                lychee.log('\t(we got "{}")'.format(views_info))
                self._i_views = views_info
                self._status = WorkflowManager._INBOUND_VIEWS_FINISHED
        else:
            lychee.log('ERROR during inbound views processing')
        inbound.VIEWS_FINISHED.emit()

    def _inbound_views_finished(self, **kwargs):
        '''
        Called when inbound.VIEWS_FINISHED is emitted, for logging and debugging.
        '''
        lychee.log('inbound views finished')

    def _inbound_views_error(self, **kwargs):
        self._status = WorkflowManager._INBOUND_VIEWS_ERROR
        if 'msg' in kwargs:
            lychee.log(kwargs['msg'])
        else:
            lychee.log('ERROR during inbound views processing')

    # ----

    def _vcs_driver(self, pathnames, **kwargs):
        '''
        Slot for vcs.START that runs the "VCS step."
        '''
        # TODO: these must be set properly
        message = None

        vcs.INIT.emit(repodir=self._session.get_repo_dir())
        vcs.ADD.emit(pathnames=pathnames)
        vcs.COMMIT.emit(message=message)

    def _vcs_finished(self, **kwargs):
        '''
        Called when vcs.FINISHED is emitted, for logging and debugging.
        '''
        lychee.log('vcs processing finished')

    def _vcs_error(self, **kwargs):
        self._status = WorkflowManager._VCS_ERROR
        if 'msg' in kwargs:
            lychee.log(kwargs['msg'])
        else:
            lychee.log('ERROR during vcs processing')

    # ----

    def _outbound_views_started(self, **kwargs):
        lychee.log('outbound views started')
        self._status = WorkflowManager._OUTBOUND_VIEWS_STARTED

    def _outbound_views_finish(self, dtype, views_info, **kwargs):
        '''
        Slot for outbound.VIEWS_FINISH
        '''
        lychee.log('outbound views finishing'.format(kwargs))
        if self._status is WorkflowManager._OUTBOUND_VIEWS_STARTED:
            self._o_views_info[dtype] = views_info
            self._status = WorkflowManager._OUTBOUND_VIEWS_FINISHED
        else:
            lychee.log('ERROR during outbound views processing')

    def _outbound_views_finished(self, **kwargs):
        '''
        Called when outbound.VIEWS_FINISHED is emitted, for logging and debugging.
        '''
        lychee.log('outbound views finished')

    def _outbound_views_error(self, **kwargs):
        self._status = WorkflowManager._OUTBOUND_VIEWS_ERROR
        if 'msg' in kwargs:
            lychee.log(kwargs['msg'])
        else:
            lychee.log('ERROR during outbound views processing')

    def _outbound_conversion_started(self, **kwargs):
        lychee.log('outbound conversion started')
        self._status = WorkflowManager._OUTBOUND_CONVERSIONS_STARTED

    def _outbound_conversion_finish(self, converted, **kwargs):
        lychee.log('outbound conversion finishing')
        if self._status is WorkflowManager._OUTBOUND_CONVERSIONS_STARTED:
            if converted is None:
                outbound.CONVERSION_ERROR.emit(msg='Outbound converter did not return a document')
            else:
                lychee.log('\t(we got "{}")'.format(converted))
                self._o_converted[self._o_running_converter] = converted
                self._status = WorkflowManager._OUTBOUND_CONVERSIONS_FINISHED
        else:
            lychee.log('ERROR during outbound conversion')

    def _outbound_conversion_finished(self, dtype, placement, document, **kwargs):
        '''
        Called when outbound.CONVERSION_FINISHED is emitted, for logging and debugging.
        '''
        lychee.log('outbound conversion finished\n\tdtype: {}\n\tplacement: {}\n\tdocument: {}\n'.format(dtype, placement, document))

    def _outbound_conversion_error(self, **kwargs):
        self._status = WorkflowManager._OUTBOUND_CONVERSIONS_ERROR
        if 'msg' in kwargs:
            lychee.log(kwargs['msg'])
        else:
            lychee.log('ERROR during outbound conversion')

    # ----

    def _the_outbound_stuff(self, dtypes):
        '''
        Do an "outbound" step for the given "dtypes."

        :param dtypes: A list of the datatypes in which to produce outbound results.
        :type dtypes: list of str
        :raises: :exc:`RuntimeError` when something went wrong
        '''
        # TODO: use better exceptions when you rewrite the workflow stuff
        next_step = '(WorkflowManager continues to the next step)\n------------------------------------------\n'

        # do the views processing
        successful_dtypes = []
        for each_dtype in self._o_dtypes:
            outbound.VIEWS_START.emit(dtype=each_dtype)
            if self._status is WorkflowManager._OUTBOUND_VIEWS_ERROR:
                self._status = WorkflowManager._OUTBOUND_VIEWS_STARTED
                continue
            elif each_dtype not in self._o_views_info:
                lychee.log('ERROR: {} did not return outbound views info'.format(each_dtype))
                continue
            else:
                successful_dtypes.append(each_dtype)

        # see if everything worked
        if self._status is WorkflowManager._OUTBOUND_VIEWS_ERROR:
            # can't happen?
            pass
        if len(successful_dtypes) != len(self._o_dtypes):
            if 0 == len(successful_dtypes):
                outbound.VIEWS_ERROR.emit(msg='No registered outbound dtypes passed through views processing')
            else:
                lychee.log('ERROR: some registered outbound dtypes failed views processing')
                self._o_dtypes = successful_dtypes
        else:
            outbound.VIEWS_FINISHED.emit()

        # After the "views" stuff, we know what we need to load for the outbound conversion...
        # (for now, we have no "views" module, so that means everything).
        convert_this = self._converted
        if convert_this is None:
            # ask the Document module to prepare a full <score> for us
            doc = self._session.get_document()
            if len(doc.get_section_ids()) > 0:
                # TODO: we shouldn't be using the first <section> by default; we should have a Document cursor that knows which section
                convert_this = doc.get_section(doc.get_section_ids()[0])

        if self._status is WorkflowManager._OUTBOUND_VIEWS_ERROR:
            # TODO: you can't even do this, because you'll ruin it for all the other dtypes that worked!
            raise RuntimeError('Error during outbound views.')
        lychee.log(next_step)

        # do the outbound conversion
        successful_dtypes = []
        expected_conversions = len(self._o_dtypes)  # NB: when there's no musical content, this is
                                                    # decremented with every music-only converter,
                                                    # so that we don't get errors when the score is empty
        if convert_this is None:
            # when there is no musical content, only some of the outbound converters will work
            for each_dtype in self._o_dtypes:
                if each_dtype in ('document', 'vcs'):
                    self._choose_outbound_converter(each_dtype)
                    self._o_running_converter = each_dtype
                    outbound.CONVERSION_START.emit(
                        views_info=self._o_views_info[each_dtype],
                        document=None,
                        session=self._session)
                    if self._status is WorkflowManager._OUTBOUND_CONVERSIONS_ERROR:
                        self._status = WorkflowManager._OUTBOUND_CONVERSIONS_STARTED
                        continue
                    else:
                        successful_dtypes.append(each_dtype)
                else:
                        expected_conversions -= 1

        else:
            for each_dtype in self._o_dtypes:
                self._choose_outbound_converter(each_dtype)
                self._o_running_converter = each_dtype
                outbound.CONVERSION_START.emit(
                    views_info=self._o_views_info[each_dtype],
                    document=convert_this,
                    session=self._session)
                if self._status is WorkflowManager._OUTBOUND_CONVERSIONS_ERROR:
                    self._status = WorkflowManager._OUTBOUND_CONVERSIONS_STARTED
                    continue
                else:
                    successful_dtypes.append(each_dtype)

        # see if everything worked
        if self._status is WorkflowManager._OUTBOUND_CONVERSIONS_ERROR:
            # can't happen?
            pass
        if len(successful_dtypes) < expected_conversions:
            if 0 == len(successful_dtypes):
                outbound.CONVERSION_ERROR.emit(msg='No outbound converters succeeded')
            else:
                lychee.log('ERROR: some registered outbound dtypes failed conversion')
                self._o_dtypes = successful_dtypes

        # emit one signal per things returned
        for each_dtype in successful_dtypes:
            outbound.CONVERSION_FINISHED.emit(dtype=each_dtype,
                                              placement=self._o_views_info[each_dtype],
                                              document=self._o_converted[each_dtype])
