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
import tempfile
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

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

    def test_registrar_property(self):
        '''
        The "registrar" property works.
        '''
        actual = self.session
        assert actual._registrar is actual.registrar

    @mock.patch('lychee.workflow.session.steps.flush_inbound_converters')
    def test_cleanup_for_new_action(self, mock_flush):
        '''
        Make sure cleanup_for_new_action() actually cleans up!
        '''
        self.session._inbound_converted = 'five'
        self.session._cleanup_for_new_action()
        assert self.session._inbound_converted is None
        assert self.session._inbound_views_info is None
        mock_flush.assert_called_once_with()


class TestRepository(TestInteractiveSession):
    '''
    Test functionality related to the repository.
    '''

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
        actual.set_repo_dir.assert_called_with('')

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

    def test_set_repo_dir_1(self):
        '''
        When "path" is '', it makes a temp dir and initializes a new Hg repo.
        '''
        sess = self.session
        actual = sess.set_repo_dir('')
        assert actual.startswith('/tmp/')
        assert os.path.exists(os.path.join(actual, '.hg'))

    @mock.patch('lychee.workflow.session.hug')
    def test_set_repo_dir_2(self, mock_hug):
        '''
        When it makes a temp dir but can't initialize a new Hg repo.
        '''
        sess = self.session
        mock_hug.Hug.side_effect = hg_error.RepoError
        with pytest.raises(exceptions.RepositoryError) as exc:
            sess.set_repo_dir('')
        assert session._CANNOT_SAFELY_HG_INIT == exc.value.args[0]
        # the _repo_dir still must have been set, so unset_repo_dir() can delete it on __del__()
        assert sess._repo_dir is not None

    @mock.patch('lychee.workflow.session.hug')
    def test_set_repo_dir_3(self, mock_hug):
        '''
        When the path exists, and it initializes fine.
        '''
        sess = self.session
        actual = sess.set_repo_dir('../tests')
        assert actual.endswith('tests')
        assert sess._hug is not None
        assert sess._temp_dir is False
        assert sess._repo_dir == actual

    @mock.patch('lychee.workflow.session.hug')
    def test_set_repo_dir_4(self, mock_hug):
        '''
        When the path must be created, and it initializes fine.
        '''
        assert not os.path.exists('zests')  # for the test to work, this dir must not already exist
        sess = self.session
        actual = sess.set_repo_dir('zests')
        assert actual.endswith('zests')
        assert os.path.exists(actual)
        shutil.rmtree(actual)

    def test_set_repo_dir_5(self):
        '''
        When the path must be created, but it can't be.
        '''
        sess = self.session
        with pytest.raises(exceptions.RepositoryError) as exc:
            sess.set_repo_dir('/bin/delete_me')
        assert session._CANNOT_MAKE_HG_DIR == exc.value.args[0]


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
