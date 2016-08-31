#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/workflow/tests/test_session.py
# Purpose:                Tests for the lychee.workflow.session module.
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
Tests for the :mod:`lychee.workflow.session` module.
'''

import os.path
import shutil
import sys
import tempfile
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from lxml import etree
from mercurial import error as hg_error
import pytest
import signalslot

from lychee.converters import registrar
from lychee import exceptions
from lychee import signals
from lychee.workflow import session
from lychee.workflow import steps


def make_slot_mock():
    slot = mock.MagicMock(spec=signalslot.slot.BaseSlot)
    slot.is_alive = True
    return slot


class TestInteractiveSession(unittest.TestCase):
    '''
    Makes sure to clean up the session before and after every test.
    '''

    def setUp(self):
        "Make an InteractiveSession."
        self.session = session.InteractiveSession()

    def tearDown(self):
        "Clean up the InteractiveSession."
        self.session.unset_repo_dir()


class TestGeneral(TestInteractiveSession):
    '''
    Tests general functionality.
    '''

    def test_init_1(self):
        '''
        Everything works as intended.
        '''
        actual = self.session
        assert actual._doc is None
        assert actual._hug is None
        assert actual._temp_dir is False
        assert actual._repo_dir is None
        assert isinstance(actual._registrar, registrar.Registrar)
        assert signals.outbound.REGISTER_FORMAT.is_connected(actual._registrar.register)
        assert signals.outbound.UNREGISTER_FORMAT.is_connected(actual._registrar.unregister)
        assert signals.vcs.START.is_connected(steps._vcs_driver)
        assert signals.inbound.CONVERSION_FINISH.is_connected(actual.inbound_conversion_finish)
        assert signals.inbound.VIEWS_FINISH.is_connected(actual.inbound_views_finish)

        # things cleaned up for every action
        assert actual._inbound_converted is None
        assert actual._inbound_views_info is None

        assert actual._vcs is None

    def test_init_with_vcs_1(self):
        '''
        The __init__() method sets the "vcs" appropriately.
        '''
        actual = session.InteractiveSession(vcs='mercurial')
        assert actual._vcs == 'mercurial'

    def test_init_with_vcs_2(self):
        '''
        The __init__() method complains when the "vcs" is an invalid type.
        '''
        with pytest.raises(exceptions.RepositoryError) as err:
            session.InteractiveSession(vcs='git')
        # TODO: check the err

    @mock.patch('lychee.workflow.session.steps.flush_inbound_converters')
    @mock.patch('lychee.workflow.session.steps.flush_inbound_views')
    def test_cleanup_for_new_action(self, mock_flush_views, mock_flush_conv):
        '''
        Make sure cleanup_for_new_action() actually cleans up!
        '''
        self.session._inbound_converted = 'five'
        self.session._cleanup_for_new_action()
        assert self.session._inbound_converted is None
        assert self.session._inbound_views_info is None
        mock_flush_conv.assert_called_once_with()
        mock_flush_views.assert_called_once_with()


class TestRepository(TestInteractiveSession):
    '''
    Test functionality related to the repository.
    '''

    def setUp(self):
        "Make an InteractiveSession."
        self.session = session.InteractiveSession(vcs='mercurial')

    def test_get_repo_dir_1(self):
        '''
        When a repository directory is set, return it.
        '''
        actual = self.session
        actual._repo_dir = 'five'
        assert 'five' == actual.get_repo_dir()

    def test_get_repo_dir_2(self):
        '''
        When the repository directory isn't set, ask set_repo_dir() to set a new one.
        '''
        actual = self.session
        actual._repo_dir = None
        actual.set_repo_dir = mock.MagicMock(return_value='six')
        assert 'six' == actual.get_repo_dir()
        actual.set_repo_dir.assert_called_with('', run_outbound=False)

    def test_unset_repo_dir_1(self):
        '''
        When we have to remove a temporary directory.
        '''
        path = tempfile.mkdtemp()
        assert os.path.exists(path)
        actual = self.session
        actual._repo_dir = path
        actual._temp_dir = True
        actual._hug = 'hug'

        actual.unset_repo_dir()

        assert not os.path.exists(path)
        assert actual._repo_dir is None
        assert actual._temp_dir is False
        assert actual._hug is None
        assert actual._doc is None

    def test_unset_repo_dir_2(self):
        '''
        When the repository isn't in a temporary directory (as far as InteractiveSession knows).
        '''
        path = tempfile.mkdtemp()
        assert os.path.exists(path)
        actual = self.session
        actual._repo_dir = path
        actual._temp_dir = False
        actual._hug = 'hug'

        actual.unset_repo_dir()

        assert os.path.exists(path)
        shutil.rmtree(path)  # if the other tests fail, this won't happen, so...
        assert actual._repo_dir is None
        assert actual._temp_dir is False
        assert actual._hug is None
        assert actual._doc is None

    def test_unset_repo_dir_3(self):
        '''
        When the _temp_dir is True but the repository is already missing.
        '''
        actual = self.session
        actual._repo_dir = None
        actual._temp_dir = True

        actual.unset_repo_dir()

        assert actual._repo_dir is None
        assert actual._temp_dir is False

    def test_set_repo_dir_1a(self):
        '''
        When "path" is '', it makes a temp dir and initializes a new Hg repo.
        '''
        sess = self.session
        sess._run_outbound = mock.Mock()
        actual = sess.set_repo_dir('', run_outbound=True)
        if sys.platform == 'linux2':
            assert actual.startswith('/tmp/')
        elif sys.platform == 'darwin':
            assert actual.startswith('/var/')
        else:
            raise NotImplementedError("This test isn't yet implemented on this platform.")
        assert os.path.exists(os.path.join(actual, '.hg'))
        assert sess._run_outbound.call_count == 1

    def test_set_repo_dir_1b(self):
        '''
        Same as 1a, but with run_outbound=False.
        '''
        # only test what's different from 1b
        sess = self.session
        sess._run_outbound = mock.Mock()
        actual = sess.set_repo_dir('', run_outbound=False)
        assert sess._run_outbound.call_count == 0

    @mock.patch('lychee.workflow.session.hug')
    def test_set_repo_dir_2(self, mock_hug):
        '''
        When it makes a temp dir but can't initialize a new Hg repo.
        '''
        sess = self.session
        sess._run_outbound = mock.Mock()
        mock_hug.Hug.side_effect = hg_error.RepoError
        with pytest.raises(exceptions.RepositoryError) as exc:
            sess.set_repo_dir('', run_outbound=True)
        assert session._CANNOT_SAFELY_HG_INIT == exc.value.args[0]
        # the _repo_dir still must have been set, so unset_repo_dir() can delete it on __del__()
        assert sess._repo_dir is not None
        assert sess._run_outbound.call_count == 0

    @mock.patch('lychee.workflow.session.hug')
    def test_set_repo_dir_3(self, mock_hug):
        '''
        When the path exists, and it initializes fine.
        '''
        sess = self.session
        sess._run_outbound = mock.Mock()
        actual = sess.set_repo_dir('../tests', run_outbound=True)
        assert actual.endswith('tests')
        assert sess._hug is not None
        assert sess._temp_dir is False
        assert sess._repo_dir == actual
        assert sess._run_outbound.call_count == 1

    @mock.patch('lychee.workflow.session.hug')
    def test_set_repo_dir_4(self, mock_hug):
        '''
        When the path must be created, and it initializes fine.
        '''
        assert not os.path.exists('zests')  # for the test to work, this dir must not already exist
        sess = self.session
        sess._run_outbound = mock.Mock()
        try:
            actual = sess.set_repo_dir('zests', run_outbound=True)
        finally:
            assert actual.endswith('zests')
            assert os.path.exists(actual)
            shutil.rmtree(actual)
        assert sess._run_outbound.call_count == 1

    def test_set_repo_dir_5(self):
        '''
        When the path must be created, but it can't be.
        '''
        sess = self.session
        sess._run_outbound = mock.Mock()
        with pytest.raises(exceptions.RepositoryError) as exc:
            sess.set_repo_dir('/bin/delete_me', run_outbound=True)
        assert session._CANNOT_MAKE_HG_DIR == exc.value.args[0]
        assert sess._run_outbound.call_count == 0

    def test_set_repo_dir_6(self):
        '''
        When the VCS is not enabled, the repository is still set, but not initialized with Hug.
        (Based on test 1a).
        '''
        sess = session.InteractiveSession()
        actual = sess.set_repo_dir('', run_outbound=False)
        if sys.platform == 'linux2':
            assert actual.startswith('/tmp/')
        elif sys.platform == 'darwin':
            assert actual.startswith('/var/')
        else:
            raise NotImplementedError("This test isn't yet implemented on this platform.")
        assert not os.path.exists(os.path.join(actual, '.hg'))
        assert sess.hug is None

    def test_hug_property(self):
        '''
        Make sure InteractiveSession.hug returns InteractiveSession._hug.
        '''
        self.session._hug = 'comfy'
        assert self.session.hug == self.session._hug


class TestDocument(TestInteractiveSession):
    '''
    Tests for InteractiveSession's management of Document instances.
    '''

    def test_get_document_1(self):
        '''
        When self._doc is already set.
        '''
        self.session._doc = 5
        assert 5 == self.session.get_document()

    def test_get_document_2(self):
        '''
        When self._doc is not set but repo_dir is.
        '''
        repo_dir = self.session.set_repo_dir('')
        actual = self.session.get_document()
        assert repo_dir == actual._repo_path

    def test_get_document_3(self):
        '''
        When self._doc and repo_dir are both unset.
        '''
        actual = self.session.get_document()
        assert self.session._repo_dir == actual._repo_path

    def test_unset_repo_dir(self):
        '''
        Cross-check that the document instance is deleted when the repo_dir is changed.
        '''
        self.session.get_document()
        self.session.set_repo_dir('')
        assert self.session._doc is None


class TestInbound(TestInteractiveSession):
    '''
    Tests for the inbound stage.
    '''

    def test_conversion_finished(self):
        "It works."
        finished_slot = make_slot_mock()
        signals.inbound.CONVERSION_FINISHED.connect(finished_slot)
        try:
            self.session.inbound_conversion_finish(converted='lol')
            assert 'lol' == self.session._inbound_converted
            finished_slot.assert_called_once_with()
        finally:
            signals.inbound.CONVERSION_FINISHED.disconnect(finished_slot)

    def test_views_finished(self):
        "It works."
        finished_slot = make_slot_mock()
        signals.inbound.VIEWS_FINISHED.connect(finished_slot)
        try:
            self.session.inbound_views_finish(views_info='lol')
            assert 'lol' == self.session._inbound_views_info
            finished_slot.assert_called_once_with()
        finally:
            signals.inbound.VIEWS_FINISHED.disconnect(finished_slot)


class TestActionStart(TestInteractiveSession):
    '''
    Tests for InteractiveSession._action_start(), the slot for the ACTION_START signal.
    '''

    def test_everything_works_unit(self):
        '''
        A unit test (fully mocked) for when everything works and all code paths are executed.
        '''
        dtype = 'silly format'
        doc = '<silly/>'
        views_info = 'Section XMLID'  # given to ACTION_START
        self.session._cleanup_for_new_action = mock.Mock()
        self.session._run_inbound_doc_vcs = mock.Mock()
        self.session._run_outbound = mock.Mock()

        self.session._action_start(dtype=dtype, doc=doc, views_info=views_info)

        self.session._run_outbound.assert_called_once_with()
        self.session._run_inbound_doc_vcs.assert_called_once_with(dtype, doc, views_info)
        assert 2 == self.session._cleanup_for_new_action.call_count

    def test_set_views_unit(self):
        '''
        A unit test (fully mocked) for when ACTION_START receives views_info and not dtype or doc.
        '''
        self.session._cleanup_for_new_action = mock.Mock()
        self.session._run_inbound_doc_vcs = mock.Mock()
        views_info = 'IBV'
        self.session._run_outbound = mock.Mock()

        self.session._action_start(views_info=views_info)

        assert self.session._inbound_views_info == 'IBV'
        assert not self.session._run_inbound_doc_vcs.called
        self.session._run_outbound.assert_called_once_with()
        assert self.session._cleanup_for_new_action.callled

    def test_when_inbound_fails(self):
        '''
        A unit test (fully mocked) for when the inbound step fails.

        The "views_info" kwarg is omitted.

        We need to assert that the later steps do not happen. Not only would running the later
        steps be unnecessary and take extra time, but it may also cause new errors.
        '''
        dtype = 'silly format'
        doc = '<silly/>'
        self.session._cleanup_for_new_action = mock.Mock()
        self.session._run_inbound_doc_vcs = mock.Mock()
        self.session._run_inbound_doc_vcs.side_effect = exceptions.InboundConversionError
        self.session._run_outbound = mock.Mock()

        self.session._action_start(dtype=dtype, doc=doc)

        self.session._run_inbound_doc_vcs.assert_called_once_with(dtype, doc, None)
        assert self.session._cleanup_for_new_action.call_count == 2
        assert self.session._run_outbound.call_count == 0

    def test_when_hg_update_works(self):
        '''
        A unit test (fully mocked) for when running Hug.update() works.
        Initial revision is on a tag.
        '''
        self.session = session.InteractiveSession(vcs='mercurial')
        parent_revision = '99:801774903828 tip'
        target_revision = '40:964b28acc4ee'
        self.session._cleanup_for_new_action = mock.Mock()
        self.session._run_outbound = mock.Mock()
        self.session._hug = mock.Mock()
        self.session._hug.summary = mock.Mock(return_value={'parent': parent_revision})
        self.session._hug.update = mock.Mock()

        self.session._action_start(revision=target_revision)

        self.session._run_outbound.assert_called_with()
        assert self.session._cleanup_for_new_action.call_count == 2
        assert self.session._hug.update.call_count == 2
        self.session._hug.update.assert_any_call(target_revision)
        # the tag name (the "tip" part) should be removed
        self.session._hug.update.assert_called_with(parent_revision[:-4])  # final call

    def test_when_hg_update_fails(self):
        '''
        A unit test (fully mocked) for when running Hug.update() fails.
        Initial revision is not on a tag.
        '''
        self.session = session.InteractiveSession(vcs='mercurial')
        parent_revision = '99:801774903828'
        target_revision = '44444444444444444'
        self.session._cleanup_for_new_action = mock.Mock()
        self.session._run_outbound = mock.Mock()
        self.session._hug = mock.Mock()
        self.session._hug.summary = mock.Mock(return_value={'parent': parent_revision})
        # we need a complicated mock here so one call to update() fails, but the 2nd, in the finally
        # suite, won't fail
        def update_effect(revision):
            "side-effect for Hug.update()"
            if revision != parent_revision:
                    raise RuntimeError('=^.^=  meow')
        self.session._hug.update = mock.Mock(side_effect=update_effect)

        self.session._action_start(revision=target_revision)

        assert self.session._run_outbound.call_count == 0
        assert self.session._cleanup_for_new_action.call_count == 2
        assert self.session._hug.update.call_count == 2
        self.session._hug.update.assert_any_call(target_revision)
        self.session._hug.update.assert_called_with(parent_revision)  # final call

    def test_revision_ignored(self):
        '''
        A unit test (fully mocked) to check the "revision" argument is ignored if VCS is disabled.
        NB: there would be an AttributeError if the VCS isn't enabled
        '''
        target_revision = '40:964b28acc4ee'
        self.session._cleanup_for_new_action = mock.Mock()
        self.session._run_outbound = mock.Mock()

        self.session._action_start(revision=target_revision)

        self.session._run_outbound.assert_called_with()
        assert self.session._cleanup_for_new_action.call_count == 2

    def test_everything_works_unmocked(self):
        '''
        An integration test (no mocks) for when everything works and all code paths are excuted.
        '''
        self.session = session.InteractiveSession(vcs='mercurial')
        input_ly = """\\clef "treble" a''4 b'16 c''2  | \\clef "bass" d?2 e!2  | f,,2 fis,2  |"""
        assert not os.path.exists(os.path.join(self.session.get_repo_dir(), 'all_files.mei'))  # pre-condition
        # unfortunately we need a mock for this, so we can be sure it was called
        finish_mock = make_slot_mock()
        def finish_side_effect(dtype, placement, document, **kwargs):
            called = True
            assert 'mei' == dtype
            assert isinstance(document, etree._Element)
        finish_mock.side_effect = finish_side_effect

        signals.outbound.REGISTER_FORMAT.emit(dtype='mei', who='test_everything_works_unmocked')
        signals.outbound.CONVERSION_FINISHED.connect(finish_mock)
        try:
            self.session._action_start(dtype='LilyPond', doc=input_ly)
        finally:
            signals.outbound.UNREGISTER_FORMAT.emit(dtype='mei', who='test_everything_works_unmocked')
            signals.outbound.CONVERSION_FINISHED.disconnect(finish_mock)

        assert os.path.exists(os.path.join(self.session.get_repo_dir(), 'all_files.mei'))


class TestRunOutbound(TestInteractiveSession):
    '''
    Tests for InteractiveSession._run_outbound().
    '''

    @mock.patch('lychee.signals.outbound.CONVERSION_FINISHED')
    @mock.patch('lychee.signals.outbound.STARTED')
    def test_no_formats(self, mock_out_started, mock_out_finished):
        '''
        No formats are registered for outbound conversion.
        '''
        self.session.set_repo_dir('')  # tempdir
        self.session._run_outbound()
        mock_out_started.emit.assert_called_once_with()
        assert mock_out_finished.emit.call_count == 0

    @mock.patch('lychee.workflow.steps.do_outbound_steps')
    @mock.patch('lychee.signals.outbound.CONVERSION_FINISHED')
    @mock.patch('lychee.signals.outbound.STARTED')
    def test_single_format(self, mock_out_started, mock_out_finished, mock_do_out):
        '''
        A single format is registered for outbound conversion. Repo is at a tag.
        '''
        self.session = session.InteractiveSession(vcs='mercurial')
        outbound_dtype = 'mei'
        views_info = 'IBV'
        self.session._inbound_views_info = views_info
        self.session._hug = mock.Mock()
        self.session._hug.summary = mock.Mock(return_value={'tag': 'tip'})
        mock_do_out.return_value = {'placement': None, 'document': None}

        signals.outbound.REGISTER_FORMAT.emit(dtype=outbound_dtype, who='test_single_format')
        try:
            self.session._run_outbound()
        finally:
            signals.outbound.UNREGISTER_FORMAT.emit(dtype=outbound_dtype, who='test_single_format')

        mock_out_started.emit.assert_called_once_with()
        mock_do_out.assert_called_once_with(
            self.session.get_repo_dir(),
            views_info,
            outbound_dtype)
        mock_out_finished.emit.assert_called_once_with(
            dtype=outbound_dtype,
            placement=mock_do_out.return_value['placement'],
            document=mock_do_out.return_value['document'],
            changeset='tip')

    @mock.patch('lychee.workflow.steps.do_outbound_steps')
    @mock.patch('lychee.signals.outbound.CONVERSION_FINISHED')
    @mock.patch('lychee.signals.outbound.STARTED')
    def test_three_formats(self, mock_out_started, mock_out_finished, mock_do_out):
        '''
        Three formats are registered for outbound conversion. Repo is not at a tag.
        '''
        self.session = session.InteractiveSession(vcs='mercurial')
        outbound_dtypes = ['document', 'mei', 'vcs']
        views_info = 'IBV'
        self.session._inbound_views_info = views_info
        self.session._hug = mock.Mock()
        self.session._hug.summary = mock.Mock(return_value={'parent': '16:96eb6fba2374'})
        mock_do_out.return_value = {'placement': None, 'document': None}

        for dtype in outbound_dtypes:
            signals.outbound.REGISTER_FORMAT.emit(dtype=dtype, who='test_single_format')
        try:
            self.session._run_outbound()
        finally:
            for dtype in outbound_dtypes:
                signals.outbound.UNREGISTER_FORMAT.emit(dtype=dtype, who='test_single_format')

        mock_out_started.emit.assert_called_once_with()
        assert mock_do_out.call_count == 3
        assert mock_out_finished.emit.call_count == 3
        mock_out_finished.emit.assert_any_call(
            dtype=outbound_dtypes[0],
            placement=mock_do_out.return_value['placement'],
            document=mock_do_out.return_value['document'],
            changeset='16:96eb6fba2374')

    @mock.patch('lychee.workflow.steps.do_outbound_steps')
    @mock.patch('lychee.signals.outbound.CONVERSION_FINISHED')
    @mock.patch('lychee.signals.outbound.STARTED')
    def test_vcs_disabled(self, mock_out_started, mock_out_finished, mock_do_out):
        '''
        A single format is registered for outbound conversion. VCS is disabled.
        '''
        outbound_dtype = 'mei'
        views_info = 'IBV'
        self.session._inbound_views_info = views_info
        mock_do_out.return_value = {'placement': None, 'document': None}

        signals.outbound.REGISTER_FORMAT.emit(dtype=outbound_dtype, who='test_single_format')
        try:
            self.session._run_outbound()
        finally:
            signals.outbound.UNREGISTER_FORMAT.emit(dtype=outbound_dtype, who='test_single_format')

        mock_out_started.emit.assert_called_once_with()
        mock_do_out.assert_called_once_with(
            self.session.get_repo_dir(),
            views_info,
            outbound_dtype)
        mock_out_finished.emit.assert_called_once_with(
            dtype=outbound_dtype,
            placement=mock_do_out.return_value['placement'],
            document=mock_do_out.return_value['document'],
            changeset='')


class TestRunInboundDocVcs(TestInteractiveSession):
    '''
    Tests for _run_inbound_doc_vcs(), a helper method for _action_start().
    '''

    @mock.patch('lychee.workflow.steps.do_inbound_conversion')
    @mock.patch('lychee.workflow.steps.do_inbound_views')
    @mock.patch('lychee.workflow.steps.do_document')
    @mock.patch('lychee.workflow.steps.do_vcs')
    def test_run_inbound_unit_1a(self, mock_vcs, mock_doc, mock_views, mock_conv):
        '''
        Unit test for _run_inbound_doc_vcs().

        - do_inbound_conversion() is called correctly
        - do_inbound_conversion() fails so there's an early return
        - the following functions aren't called
        '''
        dtype = 'meh'
        doc = 'document'
        views_info = 'Section XMLID'

        with pytest.raises(exceptions.InboundConversionError) as exc:
            self.session._run_inbound_doc_vcs(dtype, doc, views_info)

        mock_conv.assert_called_once_with(
            session=self.session,
            dtype=dtype,
            document=doc)
        assert 0 == mock_views.call_count
        assert 0 == mock_doc.call_count
        assert 0 == mock_vcs.call_count

    @mock.patch('lychee.workflow.steps.do_inbound_conversion')
    def test_run_inbound_unit_1b(self, mock_conv):
        '''
        Unit test for _run_inbound_doc_vcs().

        - do_inbound_conversion() is called correctly
        - do_inbound_conversion() returns an incorrect value so there's an early return
        '''
        dtype = 'meh'
        doc = 'document'
        views_info = 'Section XMLID'
        self.session._inbound_converted = 'this is not an LMEI document'

        with pytest.raises(exceptions.InboundConversionError) as exc:
            self.session._run_inbound_doc_vcs(dtype, doc, views_info)

        mock_conv.assert_called_once_with(
            session=self.session,
            dtype=dtype,
            document=doc)

    @mock.patch('lychee.workflow.steps.do_inbound_conversion')
    @mock.patch('lychee.workflow.steps.do_inbound_views')
    @mock.patch('lychee.workflow.steps.do_document')
    @mock.patch('lychee.workflow.steps.do_vcs')
    def test_run_inbound_unit_2a(self, mock_vcs, mock_doc, mock_views, mock_conv):
        '''
        Unit test for _run_inbound_doc_vcs().

        - do_inbound_views() is called correctly
        - do_inbound_views() fails so there's an early return
        - the following functions aren't called
        '''
        dtype = 'meh'
        doc = 'document'
        views_info = 'Section XMLID'
        self.session._inbound_converted = etree.Element('whatever')

        with pytest.raises(exceptions.InboundConversionError) as exc:
            self.session._run_inbound_doc_vcs(dtype, doc, views_info)

        assert 1 == mock_conv.call_count
        mock_views.assert_called_once_with(
            session=self.session,
            dtype=dtype,
            document=doc,
            converted=self.session._inbound_converted,
            views_info=views_info)
        assert 0 == mock_doc.call_count
        assert 0 == mock_vcs.call_count

    @mock.patch('lychee.workflow.steps.do_inbound_conversion')
    @mock.patch('lychee.workflow.steps.do_inbound_views')
    def test_run_inbound_unit_2b(self, mock_views, mock_conv):
        '''
        Unit test for _run_inbound_doc_vcs().

        - do_inbound_views() is called correctly
        - do_inbound_views() returns an incorrect value so there's an early return
        '''
        dtype = 'meh'
        doc = 'document'
        views_info = 'Section XMLID'
        self.session._inbound_converted = etree.Element('whatever')
        self.session._inbound_views_info = 4  # expecting str

        with pytest.raises(exceptions.InboundConversionError) as exc:
            self.session._run_inbound_doc_vcs(dtype, doc, views_info)

        assert 1 == mock_conv.call_count
        mock_views.assert_called_once_with(
            session=self.session,
            dtype=dtype,
            document=doc,
            converted=self.session._inbound_converted,
            views_info=views_info)

    @mock.patch('lychee.workflow.steps.do_inbound_conversion')
    @mock.patch('lychee.workflow.steps.do_inbound_views')
    @mock.patch('lychee.workflow.steps.do_document')
    @mock.patch('lychee.workflow.steps.do_vcs')
    def test_run_inbound_unit_3(self, mock_vcs, mock_doc, mock_views, mock_conv):
        '''
        Unit test for _run_inbound_doc_vcs().

        - do_document() is called correctly
        - do_vcs() is called correctly
        '''
        dtype = 'meh'
        doc = 'document'
        views_info = 'Section XMLID'
        self.session._inbound_converted = etree.Element('whatever')
        self.session._inbound_views_info = 'something'
        mock_doc.return_value = ['pathnames!']

        self.session._run_inbound_doc_vcs(dtype, doc, views_info)

        assert 1 == mock_conv.call_count
        assert 1 == mock_views.call_count
        mock_doc.assert_called_once_with(
            converted=self.session._inbound_converted,
            session=self.session,
            views_info=self.session._inbound_views_info)
        mock_vcs.assert_called_once_with(session=self.session, pathnames=mock_doc.return_value)
