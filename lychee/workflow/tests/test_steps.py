#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/workflow/tests/test_steps.py
# Purpose:                Tests for the lychee.workflow.steps module.
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
Tests for the :mod:`lychee.workflow.steps` module.
'''

import os.path
import shutil
import tempfile

try:
    from unittest import mock
except ImportError:
    import mock

from lxml import etree
import pytest
import signalslot

from lychee import converters
from lychee import document
from lychee import exceptions
from lychee.namespaces import mei, xml
from lychee import signals
from lychee.vcs import hg as vcs_hg_module
from lychee.views import inbound as views_in
from lychee.workflow import session, steps

from test_session import TestInteractiveSession


def make_slot_mock():
    slot = mock.MagicMock(spec=signalslot.slot.BaseSlot)
    slot.is_alive = True
    return slot


@pytest.fixture()
def temp_doc(request):
    '''
    This PyTest fixture provides and cleans up an empty LMEI document in a temporary directory.

    :returns: Pathname to the LMEI document directory.
    '''
    temp_dir = tempfile.mkdtemp()
    document.Document(temp_dir).save_everything()
    def clean_up_temp_dir():
        "Delete the temporary directory."
        shutil.rmtree(temp_dir)
    request.addfinalizer(clean_up_temp_dir)
    return temp_dir


@pytest.fixture()
def temp_doc_sec(request, temp_doc):
    "Same as 'temp_doc' fixture, plus an empty <section> in the active score."
    score = etree.Element(mei.SCORE)
    etree.SubElement(score, mei.SECTION)
    doc = document.Document(temp_doc)
    doc.put_score(score)
    doc.save_everything()
    return temp_doc


class TestDocumentStep(TestInteractiveSession):
    '''
    Tests for the "document" step.
    '''

    def test_document_1(self):
        '''
        That do_document() works.
        '''
        xmlid = 'Sme-s-m-l-e1111111'
        section_pathname = os.path.join(self.session.get_repo_dir(), '{}.mei'.format(xmlid))
        converted = etree.Element(mei.SECTION, attrib={xml.ID: xmlid})
        pathnames = steps.do_document(self.session, converted, 'views info')

        assert section_pathname in pathnames
        doc = self.session.document
        assert [xmlid] == doc.get_section_ids()
        assert [xmlid] == doc.get_section_ids(all_sections=True)
        assert os.path.exists(section_pathname)


class TestVCSStep(TestInteractiveSession):
    '''
    Tests for the "VCS" step.
    '''

    def setUp(self):
        "Make an InteractiveSession."
        self.session = session.InteractiveSession(vcs='mercurial')
        # disconnect any pre-existing slots
        def disconnect_everything(signal):
            for slot in signal.slots:
                signal.disconnect(slot)

        disconnect_everything(signals.vcs.START)
        disconnect_everything(signals.vcs.VCS_DISABLED)
        disconnect_everything(signals.vcs.FINISHED)
        disconnect_everything(signals.vcs.INIT)
        disconnect_everything(signals.vcs.ADD)
        disconnect_everything(signals.vcs.COMMIT)

    def test_do_vcs_1(self):
        '''
        That do_vcs() works when the VCS is enabled.
        '''
        start_slot = make_slot_mock()
        finished_slot = make_slot_mock()
        signals.vcs.START.connect(start_slot)
        signals.vcs.FINISHED.connect(finished_slot)

        try:
            steps.do_vcs(self.session, ['pathnames'])
        finally:
            signals.vcs.START.disconnect(start_slot)
            signals.vcs.FINISHED.disconnect(finished_slot)

        start_slot.assert_called_with(session=self.session, pathnames=['pathnames'])
        finished_slot.assert_called_with()

    def test_do_vcs_2(self):
        '''
        That do_vcs() works when the VCS is disabled.
        '''
        # pre setup
        self.session.unset_repo_dir()
        self.session = session.InteractiveSession(vcs=None)
        # end pre setup
        start_slot = make_slot_mock()
        disabled_slot = make_slot_mock()
        finished_slot = make_slot_mock()
        signals.vcs.START.connect(start_slot)
        signals.vcs.VCS_DISABLED.connect(disabled_slot)
        signals.vcs.FINISHED.connect(finished_slot)

        try:
            steps.do_vcs(self.session, ['pathnames'])
        finally:
            signals.vcs.START.disconnect(start_slot)
            signals.vcs.VCS_DISABLED.disconnect(disabled_slot)
            signals.vcs.FINISHED.disconnect(finished_slot)

        assert start_slot.call_count == 0
        disabled_slot.assert_called_with()
        finished_slot.assert_called_with()

    def test_vcs_driver_1(self):
        '''
        That _vcs_driver() works.
        '''
        init_slot = make_slot_mock()
        add_slot = make_slot_mock()
        commit_slot = make_slot_mock()
        signals.vcs.INIT.connect(init_slot)
        signals.vcs.ADD.connect(add_slot)
        signals.vcs.COMMIT.connect(commit_slot)

        try:
            steps._vcs_driver(session='sess', pathnames='names')
        finally:
            signals.vcs.INIT.disconnect(init_slot)
            signals.vcs.ADD.disconnect(add_slot)
            signals.vcs.COMMIT.disconnect(commit_slot)

        init_slot.assert_called_with(session='sess')
        add_slot.assert_called_with(pathnames='names', session='sess')
        commit_slot.assert_called_with(message=None, session='sess')


class TestInboundConversionStep(TestInteractiveSession):
    '''
    Tests for the inbound conversion step.
    '''

    def test_choose_converter_1(self):
        '''
        When the converter connects.
        '''
        dtype = 'lilypond'
        assert 0 == len(signals.inbound.CONVERSION_START.slots)
        steps._choose_inbound_converter(dtype)
        assert signals.inbound.CONVERSION_START.is_connected(converters.INBOUND_CONVERTERS[dtype])
        signals.inbound.CONVERSION_START.disconnect(converters.INBOUND_CONVERTERS[dtype])

    def test_choose_converter_2(self):
        '''
        When the "dtype" is invalid.
        '''
        dtype = 'red-black tree'
        assert 0 == len(signals.inbound.CONVERSION_START.slots)
        with pytest.raises(exceptions.InvalidDataTypeError) as exc:
            steps._choose_inbound_converter(dtype)
        assert steps._INVALID_INBOUND_DTYPE.format(dtype) == exc.value.args[0]
        assert 0 == len(signals.inbound.CONVERSION_START.slots)

    def test_flush_inbound_converters_1(self):
        '''
        It works when all the converters are connected.
        '''
        for each_converter in converters.INBOUND_CONVERTERS.values():
            signals.inbound.CONVERSION_START.connect(each_converter)
        assert len(converters.INBOUND_CONVERTERS) == len(signals.inbound.CONVERSION_START.slots)
        steps.flush_inbound_converters()
        assert 0 == len(signals.inbound.CONVERSION_START.slots)

    def test_flush_inbound_converters_2(self):
        '''
        It works when none of the converters are connected.
        '''
        assert 0 == len(signals.inbound.CONVERSION_START.slots)
        steps.flush_inbound_converters()
        assert 0 == len(signals.inbound.CONVERSION_START.slots)

    @mock.patch('lychee.workflow.steps.flush_inbound_converters')
    @mock.patch('lychee.workflow.steps._choose_inbound_converter')
    def test_do_inbound_conversion_1(self, mock_choose, mock_flush):
        '''
        When it works.

        Also make sure the "dtype" is automatically lowercased.
        '''
        dtype = 'dTypE'
        document = 'document'
        start_slot = make_slot_mock()
        signals.inbound.CONVERSION_START.connect(start_slot)

        try:
            steps.do_inbound_conversion(self.session, dtype, document)
            mock_choose.assert_called_once_with('dtype')
            start_slot.assert_called_once_with(document=document)
            mock_flush.assert_called_once_with()
        finally:
            signals.inbound.CONVERSION_START.disconnect(start_slot)

    @mock.patch('lychee.workflow.steps.flush_inbound_converters')
    @mock.patch('lychee.workflow.steps._choose_inbound_converter')
    def test_do_inbound_conversion_2(self, mock_choose, mock_flush):
        '''
        When it fails with a InvalidDataTypeError.
        '''
        dtype = 'dtype'
        document = 'document'
        mock_choose.side_effect = exceptions.InvalidDataTypeError('rawr')
        finish_slot = make_slot_mock()
        signals.inbound.CONVERSION_FINISH.connect(finish_slot)
        error_slot = make_slot_mock()
        signals.inbound.CONVERSION_ERROR.connect(error_slot)

        try:
            steps.do_inbound_conversion(self.session, dtype, document)
            finish_slot.assert_called_once_with(converted=None)
            error_slot.assert_called_once_with(msg='rawr')
            mock_flush.assert_called_once_with()
        finally:
            signals.inbound.CONVERSION_FINISH.disconnect(finish_slot)
            signals.inbound.CONVERSION_ERROR.disconnect(error_slot)

    @mock.patch('lychee.workflow.steps.flush_inbound_converters')
    @mock.patch('lychee.workflow.steps._choose_inbound_converter')
    def test_do_inbound_conversion_3(self, mock_choose, mock_flush):
        '''
        When it fails with another exception.
        '''
        dtype = 'dtype'
        document = 'document'
        mock_choose.side_effect = TypeError
        finish_slot = make_slot_mock()
        signals.inbound.CONVERSION_FINISH.connect(finish_slot)
        error_slot = make_slot_mock()
        signals.inbound.CONVERSION_ERROR.connect(error_slot)

        try:
            steps.do_inbound_conversion(self.session, dtype, document)
            finish_slot.assert_called_once_with(converted=None)
            error_slot.assert_called_once_with(msg=steps._UNEXP_ERR_INBOUND_CONVERSION)
            mock_flush.assert_called_once_with()
        finally:
            signals.inbound.CONVERSION_FINISH.disconnect(finish_slot)
            signals.inbound.CONVERSION_ERROR.disconnect(error_slot)


class TestInboundViewsStep(TestInteractiveSession):
    '''
    Tests for the inbound views step.
    '''

    @mock.patch('lychee.workflow.steps.flush_inbound_views')
    @mock.patch('lychee.workflow.steps._choose_inbound_views')
    def test_do_inbound_views_1(self, mock_choose, mock_flush):
        '''
        When it works.
        '''
        dtype = 'dtype'
        document = 'document'
        converted = 'converted'
        views_info = 'Section XMLID'
        start_slot = make_slot_mock()
        assert 0 == len(signals.inbound.VIEWS_START.slots)
        signals.inbound.VIEWS_START.connect(start_slot)

        try:
            steps.do_inbound_views(self.session, dtype, document, converted, views_info)
        finally:
            signals.inbound.VIEWS_START.disconnect(start_slot)

        mock_choose.assert_called_once_with(dtype)
        start_slot.assert_called_with(
            document=document, converted=converted, session=self.session, views_info=views_info)
        mock_flush.assert_called_with()

    @mock.patch('lychee.workflow.steps.flush_inbound_views')
    @mock.patch('lychee.workflow.steps._choose_inbound_views')
    def test_do_inbound_views_2(self, mock_choose, mock_flush):
        '''
        When it fails with a InvalidDataTypeError.
        '''
        dtype = 'dtype'
        document = 'document'
        converted = 'converted'
        views_info = 'Section XMLID'
        mock_choose.side_effect = exceptions.InvalidDataTypeError('rawr')
        finish_slot = make_slot_mock()
        signals.inbound.VIEWS_FINISH.connect(finish_slot)
        error_slot = make_slot_mock()
        signals.inbound.VIEWS_ERROR.connect(error_slot)

        try:
            steps.do_inbound_views(self.session, dtype, document, converted, views_info)
        finally:
            signals.inbound.VIEWS_FINISH.disconnect(finish_slot)
            signals.inbound.VIEWS_ERROR.disconnect(error_slot)

        finish_slot.assert_called_once_with(views_info=None)
        error_slot.assert_called_once_with(msg='rawr')
        mock_flush.assert_called_once_with()

    @mock.patch('lychee.workflow.steps.flush_inbound_views')
    @mock.patch('lychee.workflow.steps._choose_inbound_views')
    def test_do_inbound_views_3(self, mock_choose, mock_flush):
        '''
        When it fails with another exception.
        '''
        dtype = 'dtype'
        document = 'document'
        converted = 'converted'
        views_info = 'Section XMLID'
        mock_choose.side_effect = TypeError
        finish_slot = make_slot_mock()
        signals.inbound.VIEWS_FINISH.connect(finish_slot)
        error_slot = make_slot_mock()
        signals.inbound.VIEWS_ERROR.connect(error_slot)

        try:
            steps.do_inbound_views(self.session, dtype, document, converted, views_info)
        finally:
            signals.inbound.VIEWS_FINISH.disconnect(finish_slot)
            signals.inbound.VIEWS_ERROR.disconnect(error_slot)

        finish_slot.assert_called_once_with(views_info=None)
        error_slot.assert_called_once_with(msg=steps._UNEXP_ERR_INBOUND_VIEWS)
        mock_flush.assert_called_once_with()

    def test_choose_views_1(self):
        '''
        _choose_inbound_views() with a valid dtype
        '''
        dtype = 'LilyPond'
        steps._choose_inbound_views(dtype)
        assert signals.inbound.VIEWS_START.is_connected(views_in.lilypond.place_view)
        signals.inbound.VIEWS_START.disconnect(views_in.lilypond.place_view)

    def test_choose_views_2(self):
        '''
        _choose_inbound_views() with an invalid dtype
        '''
        dtype = 'Water Depot: Franchises still available!'
        with pytest.raises(exceptions.InvalidDataTypeError) as exc:
            steps._choose_inbound_views(dtype)

        assert len(signals.inbound.VIEWS_START.slots) == 0
        assert exc.value.args[0] == steps._NO_INBOUND_VIEWS.format(dtype.lower())

    def test_flush_views_1(self):
        '''
        flush_inbound_views() when nothing was connected to begin with.
        '''
        assert len(signals.inbound.VIEWS_START.slots) == 0  # pre-condition
        steps.flush_inbound_views()
        assert len(signals.inbound.VIEWS_START.slots) == 0

    def test_flush_views_2(self):
        '''
        flush_inbound_views() when nothing was connected to begin with.
        '''
        assert len(signals.inbound.VIEWS_START.slots) == 0  # pre-condition
        # connect two slots
        signals.inbound.VIEWS_START.connect(views_in.abjad.place_view)
        signals.inbound.VIEWS_START.connect(views_in.lilypond.place_view)
        assert len(signals.inbound.VIEWS_START.slots) == 2  # pre-condition

        steps.flush_inbound_views()

        assert len(signals.inbound.VIEWS_START.slots) == 0


class TestOutboundSteps(object):
    '''
    Tests for the outbound steps.
    '''

    def test_noviews_converters(self):
        '''
        Some outbound converters don't need "views" information, so we don't process it for them.
        '''
        dtype = 'vcs'
        views_info = 'views'
        repo_dir = 'dirrrrr!'
        vcs_mock = mock.MagicMock()
        vcs_mock.return_value = 'vcs4u.com'
        expected = {'dtype': dtype, 'document': vcs_mock.return_value, 'placement': None}

        orig_vcs = converters.OUTBOUND_CONVERTERS[dtype]
        converters.OUTBOUND_CONVERTERS[dtype] = vcs_mock
        try:
            actual = steps.do_outbound_steps(repo_dir, views_info, dtype)
        finally:
            converters.OUTBOUND_CONVERTERS[dtype] = orig_vcs

        vcs_mock.assert_called_once_with(repo_dir)
        assert expected == actual

    @mock.patch('lychee.workflow.steps._do_outbound_views')
    def test_views_converters(self, mock_views, temp_doc_sec):
        '''
        Most outbound converters do need "views" information.
        '''
        dtype = 'mei'
        views_info = 'views'
        repo_dir = temp_doc_sec
        mei_mock = mock.MagicMock()
        mei_mock.return_value = 'mei4u.net'
        mock_views.return_value = {'convert': 'vc', 'placement': 'vp'}
        expected = {'dtype': dtype, 'document': mei_mock.return_value, 'placement': 'vp'}

        orig_mei = converters.OUTBOUND_CONVERTERS[dtype]
        converters.OUTBOUND_CONVERTERS[dtype] = mei_mock
        try:
            actual = steps.do_outbound_steps(repo_dir, views_info, dtype)
        finally:
            converters.OUTBOUND_CONVERTERS[dtype] = orig_mei

        mei_mock.assert_called_once_with(mock_views.return_value['convert'])
        assert expected == actual

    def test_empty_document(self, temp_doc):
        '''
        With an outbound dtype that does require views processing, but there are no sections in the
        score. Expect a SectionNotFoundError.
        '''
        dtype = 'mei'
        views_info = 'views'
        repo_dir = temp_doc

        with pytest.raises(exceptions.SectionNotFoundError) as exc:
            actual = steps.do_outbound_steps(repo_dir, views_info, dtype)

        assert exc.value.args[0] == steps._SCORE_IS_EMPTY

    def test_invalid_dtype(self):
        '''
        When the "dtype" is invalid, we expect an InvalidDataTypeError.
        '''
        dtype = 'butterfly'
        views_info = 'views'
        repo_dir = 'dirrrrr!'

        with pytest.raises(exceptions.InvalidDataTypeError) as exc:
            steps.do_outbound_steps(repo_dir, views_info, dtype)

        assert steps._INVALID_OUTBOUND_DTYPE.format(dtype) == exc.value.args[0]

    @mock.patch('lychee.workflow.steps.views_out.mei.get_view')
    def test_views_works(self, mock_get_view):
        '''
        For steps._do_outbound_views() when it finds a views processor for the "dtype."
        '''
        repo_dir = 'here'
        views_info = 'shmiews shminfo'
        dtype = 'mei'
        mock_get_view.return_value = ('p', 'c')
        expected = {'placement': 'p', 'convert': 'c'}

        actual = steps._do_outbound_views(repo_dir, views_info, dtype)

        assert expected == actual
        mock_get_view.assert_called_with(repo_dir, views_info, dtype)

    def test_views_doesnt_work(self):
        '''
        For steps._do_outbound_views() when it doesn't find a views processor for the "dtype."
        '''
        repo_dir = 'here'
        views_info = 'shmiews shminfo'
        dtype = 'ffffffffffffff, just like fifty Fs, ffffffffffffffffffffffff-'

        with pytest.raises(exceptions.ViewsError) as exc:
            steps._do_outbound_views(repo_dir, views_info, dtype)

        assert exc.value.args[0] == steps._NO_OUTBOUND_VIEWS.format(dtype)
