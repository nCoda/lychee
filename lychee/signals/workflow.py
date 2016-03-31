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
.. warning:: This module is deprecated.
'''


import lychee
from lychee.signals import inbound, outbound
from lychee.workflow import steps


class WorkflowManager(object):
    '''
    If you use this class, I will find you, and I will take you out.
    '''

    def __init__(self, dtype=None, doc=None, session=None, **kwargs):
        if session is None:
            raise NotImplementedError('WorkflowManager requires a "session" argument!')
        else:
            self._session = session

        # set instance settings
        # whether to do the "inbound" conversion step
        self._do_inbound = False

        if dtype is not None and doc is not None:  # just in case we can lxml.Element
            lychee.log('WorkflowManager will do a full conversion', 'debug')
            self._do_inbound = True
            self._i_dtype = dtype.lower()
            self._i_doc = doc
        else:
            lychee.log('WorkflowManager will only do the outbound step', 'debug')

    def end(self):
        '''
        Disconnect all signals from this :class:`WorkflowManager` so it can be deleted. Does not
        attempt to ensure running processes are allowed to finish.
        '''
        steps.flush_inbound_converters()
        steps.flush_inbound_views()

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

        # I know it only seems to tell us whether to do the "inbound" step, but the Document and VCS
        # steps only make sense when there was an inbound change!
        if self._do_inbound:
            # Inbound -------------------------------------------------------------
            steps.do_inbound_conversion(
                session=self._session,
                dtype=self._i_dtype,
                document=self._i_doc)

            steps.do_inbound_views(
                session=self._session,
                dtype=self._i_dtype,
                document=self._i_doc,
                converted=self._session._inbound_converted)

            # Document ------------------------------------------------------------
            self._modified_pathnames = steps.do_document(
                converted=self._session._inbound_converted,
                session=self._session,
                views_info='placeholder views info')

            # VCS -----------------------------------------------------------------
            steps.do_vcs(session=self._session, pathnames=self._modified_pathnames)

        # Outbound ------------------------------------------------------------
        # determine which formats are required
        outbound.STARTED.emit()
        for dtype in self._session.registrar.get_registered_formats():
            post = steps.do_outbound_steps(
                self._session.get_repo_dir(),
                self._session._inbound_views_info,
                dtype)
            outbound.CONVERSION_FINISHED.emit(
                dtype=dtype,
                placement=post['placement'],
                document=post['document'])
