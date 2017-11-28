#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/workflow/tests/test_session.py
# Purpose:                Tests for the lychee.workflow.session module.
#
# Copyright (C) 2016, 2017 Christopher Antila
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

# pylint: disable=protected-access

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
# from mercurial import error as hg_error
import pytest
import signalslot

from lychee import exceptions
from lychee import signals
from lychee.workflow import registrar, session, steps


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
        assert actual._registrar is actual.registrar
        assert signals.outbound.REGISTER_FORMAT.is_connected(actual._registrar.register)
        assert signals.outbound.UNREGISTER_FORMAT.is_connected(actual._registrar.unregister)
        assert signals.vcs.START.is_connected(steps._vcs_driver)
        assert signals.inbound.CONVERSION_FINISH.is_connected(actual._inbound_conversion_finish)
        assert signals.inbound.VIEWS_FINISH.is_connected(actual._inbound_views_finish)

        # things cleaned up for every action
        assert actual._inbound_converted is None
        assert actual._inbound_views_info is None

        assert actual._vcs is None

    @pytest.mark.xfail
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

    @pytest.mark.xfail
    def test_vcs_property_1(self):
        '''
        When the VCS is enabled, the "vcs_enabled" property should be True.
        '''
        actual = session.InteractiveSession(vcs='mercurial')
        assert actual.vcs_enabled is True

    def test_vcs_property_2(self):
        '''
        When the VCS is disabled, the "vcs_enabled" property should be False.
        '''
        actual = session.InteractiveSession(vcs=None)
        assert actual.vcs_enabled is False


class TestCleanupForNewAction(TestInteractiveSession):
    """
    Tests for cleanup_for_new_action().
    """

    @mock.patch('lychee.workflow.session.steps.flush_inbound_converters')
    @mock.patch('lychee.workflow.session.steps.flush_inbound_views')
    def test_without_section_id(self, mock_flush_views, mock_flush_conv):
        """
        When there is no @xml:id of an incoming <section>, everything works.
        """
        self.session._inbound_converted = 'five'
        self.session._cleanup_for_new_action()
        assert self.session._inbound_converted is None
        assert self.session._inbound_views_info is None
        mock_flush_conv.assert_called_once_with()
        mock_flush_views.assert_called_once_with()

    def test_deletes_existing_section(self):
        """
        When given an @xml:id and there are files to delete, they are deleted.
        """
        sect_id = 'asdfasdf'
        dtype = 'qwerqwer'
        self.session.set_repo_dir('')
        save_dir = os.path.join(self.session._repo_dir, session.SAVE_DIR, sect_id)
        self.session.save_text_editor(sect_id, dtype, 'This is a test.')
        self.session._cleanup_for_new_action(sect_id=sect_id)
        assert not os.path.exists(save_dir)

    def test_repo_not_set(self):
        """
        When given an @xml:id but no repository is set, no exception is raised.
        """
        self.session._cleanup_for_new_action(sect_id='asdfasdf')

    def test_nothing_to_delete(self):
        """
        When given an @xml:id but there are no files to delete, no exception is raised.
        """
        self.session.set_repo_dir('')
        self.session._cleanup_for_new_action(sect_id='asdfasdf')

    def test_sect_id_is_a_number(self):
        """
        When given an @xml:id but it is a number, no exception is raised.
        """
        sect_id = '42'
        dtype = 'qwerqwer'
        self.session.set_repo_dir('')
        save_dir = os.path.join(self.session._repo_dir, session.SAVE_DIR, sect_id)
        self.session.save_text_editor(sect_id, dtype, 'This is a test.')
        self.session._cleanup_for_new_action(sect_id=int(sect_id))
        assert not os.path.exists(save_dir)


class TestSaveTextEditor(TestInteractiveSession):
    """
    Tests for save_text_editor().
    """

    def setUp(self, *args, **kwargs):
        TestInteractiveSession.setUp(self, *args, **kwargs)
        self.session.set_repo_dir('')

    def test_save_path(self):
        """
        determines the right path to save the data
        """
        sect_id = 'm2-21aa'
        dtype = '**kern'
        doc = 'this is fake kern data'
        expected_save_path = os.path.join(
            self.session._repo_dir, session.SAVE_DIR, sect_id, dtype
        )

        save_path = self.session.save_text_editor(sect_id, dtype, doc)

        assert expected_save_path == save_path

    def test_correct_contents(self):
        """
        puts the "doc" string into the file
        """
        sect_id = 'm2-21aa'
        dtype = '**kern'
        doc = 'this is fake kern data'

        save_path = self.session.save_text_editor(sect_id, dtype, doc)

        with open(save_path) as saved_file:
            assert doc == saved_file.read()

    def test_save_unicode(self):
        """
        Saves Unicode file contents.

        (Unicode pathnames aren't a problem, for some reason).
        """
        sect_id = u'文件'
        dtype = u'中文'
        doc = u'我是斯念安'

        save_path = self.session.save_text_editor(sect_id, dtype, doc)

        with open(save_path) as saved_file:
            assert doc.encode('utf-8') == saved_file.read()

    def test_make_dir(self):
        """
        makes the directory if required
        """
        sect_id = 'm2-21aa'
        dtype = '**kern'
        doc = 'this is fake kern data'
        expected_dir = os.path.join(
            self.session._repo_dir, session.SAVE_DIR, sect_id
        )

        self.session.save_text_editor(sect_id, dtype, doc)

        assert os.path.exists(expected_dir)

    def test_used_existing_dir(self):
        """
        uses existing directory if possible
        """
        sect_id = 'm2-21aa'
        dtype = '**kern'
        doc = 'this is fake kern data'
        expected_dir = os.path.join(
            self.session._repo_dir, session.SAVE_DIR, sect_id
        )
        os.makedirs(expected_dir)

        save_path = self.session.save_text_editor(sect_id, dtype, doc)

        assert save_path.startswith(expected_dir)
        assert os.path.exists(save_path)

    def test_overwrite(self):
        """
        overwrites existing file
        """
        sect_id = 'm2-21aa'
        dtype = '**kern'
        first_doc = 'this is fake kern data'
        second_doc = 'this is real kern data'

        save_path = self.session.save_text_editor(sect_id, dtype, first_doc)
        with open(save_path) as saved_file:
            assert first_doc == saved_file.read()

        self.session.save_text_editor(sect_id, dtype, second_doc)
        with open(save_path) as saved_file:
            assert second_doc == saved_file.read()

    def test_args_wrong_type(self):
        """
        raises TypeError if args are the wrong type
        """
        sect_id = 212
        dtype = '**kern'
        doc = 'this is fake kern data'

        with pytest.raises(TypeError) as exc:
            self.session.save_text_editor(sect_id, dtype, doc)
        assert exc.match(session._SAVE_ERR_BAD_DATA)

    def test_args_are_empty(self):
        """
        raises ValueError if args are empty string
        """
        sect_id = ''
        dtype = '**kern'
        doc = 'this is fake kern data'

        with pytest.raises(ValueError) as exc:
            self.session.save_text_editor(sect_id, dtype, doc)
        assert exc.match(session._SAVE_ERR_BAD_DATA)

    def test_args_invalid_chars(self):
        """
        raises ValueError if args contain invalid path characters
        """
        sect_id = 'what..ever'
        dtype = 'buy/some.cheese'
        doc = 'this is fake kern data'

        with pytest.raises(ValueError) as exc:
            self.session.save_text_editor(sect_id, dtype, doc)
        assert exc.match(session._SAVE_ERR_BAD_DATA)


class TestRepository(TestInteractiveSession):
    '''
    Test functionality related to the repository.
    '''

    def test_get_repo_dir_1(self):
        '''
        When a repository directory is set, return it.
        '''
        actual = session.InteractiveSession()
        actual._repo_dir = 'five'
        assert actual.get_repo_dir() == 'five'

    def test_get_repo_dir_2(self):
        '''
        When the repository directory isn't set, ask set_repo_dir() to set a new one.
        '''
        actual = session.InteractiveSession()
        actual._repo_dir = None
        actual.set_repo_dir = mock.MagicMock(return_value='six')
        assert actual.get_repo_dir() == 'six'
        actual.set_repo_dir.assert_called_with('', run_outbound=False)

    def test_unset_repo_dir_1(self):
        '''
        When we have to remove a temporary directory.
        '''
        path = tempfile.mkdtemp()
        assert os.path.exists(path)
        actual = session.InteractiveSession()
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
        actual = session.InteractiveSession()
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
        actual = session.InteractiveSession()
        actual._repo_dir = None
        actual._temp_dir = True

        actual.unset_repo_dir()

        assert actual._repo_dir is None
        assert actual._temp_dir is False

    @pytest.mark.xfail
    def test_set_repo_dir_1a(self):
        '''
        When "path" is '', it makes a temp dir and initializes a new Hg repo.
        '''
        sess = session.InteractiveSession(vcs='mercurial')
        sess.run_outbound = mock.Mock()
        actual = sess.set_repo_dir('', run_outbound=True)
        if sys.platform == 'linux2':
            assert actual.startswith('/tmp/')
        elif sys.platform == 'darwin':
            assert actual.startswith('/var/')
        else:
            raise NotImplementedError("This test isn't yet implemented on this platform.")
        assert os.path.exists(os.path.join(actual, '.hg'))
        assert sess.run_outbound.call_count == 1

    @pytest.mark.xfail
    def test_set_repo_dir_1b(self):
        '''
        Same as 1a, but with run_outbound=False.
        '''
        # only test what's different from 1b
        sess = session.InteractiveSession(vcs='mercurial')
        sess.run_outbound = mock.Mock()
        actual = sess.set_repo_dir('', run_outbound=False)
        assert sess.run_outbound.call_count == 0

    @pytest.mark.xfail
    @mock.patch('lychee.workflow.session.hug')
    def test_set_repo_dir_2(self, mock_hug):
        '''
        When it makes a temp dir but can't initialize a new Hg repo.
        '''
        sess = session.InteractiveSession(vcs='mercurial')
        sess.run_outbound = mock.Mock()
        mock_hug.Hug.side_effect = hg_error.RepoError
        with pytest.raises(exceptions.RepositoryError) as exc:
            sess.set_repo_dir('', run_outbound=True)
        assert session._CANNOT_SAFELY_HG_INIT == exc.value.args[0]
        # the _repo_dir still must have been set, so unset_repo_dir() can delete it on __del__()
        assert sess._repo_dir is not None
        assert sess.run_outbound.call_count == 0

    @pytest.mark.xfail
    @mock.patch('lychee.workflow.session.hug')
    def test_set_repo_dir_3(self, mock_hug):
        '''
        When the path exists, and it initializes fine.
        '''
        sess = session.InteractiveSession(vcs='mercurial')
        sess.run_outbound = mock.Mock()
        actual = sess.set_repo_dir('../tests', run_outbound=True)
        assert actual.endswith('tests')
        assert sess._hug is not None
        assert sess._temp_dir is False
        assert sess._repo_dir == actual
        assert sess.run_outbound.call_count == 1

    @pytest.mark.xfail
    @mock.patch('lychee.workflow.session.hug')
    def test_set_repo_dir_4(self, mock_hug):
        '''
        When the path must be created, and it initializes fine.
        '''
        assert not os.path.exists('zests')  # for the test to work, this dir must not already exist
        sess = session.InteractiveSession(vcs='mercurial')
        sess.run_outbound = mock.Mock()
        try:
            actual = sess.set_repo_dir('zests', run_outbound=True)
        finally:
            assert actual.endswith('zests')
            assert os.path.exists(actual)
            shutil.rmtree(actual)
        assert sess.run_outbound.call_count == 1

    def test_set_repo_dir_5(self):
        '''
        When the path must be created, but it can't be.
        '''
        sess = session.InteractiveSession()
        sess.run_outbound = mock.Mock()
        with pytest.raises(exceptions.RepositoryError) as exc:
            sess.set_repo_dir('/bin/delete_me', run_outbound=True)
        assert session._CANNOT_MAKE_HG_DIR == exc.value.args[0]
        assert sess.run_outbound.call_count == 0

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
        sess = session.InteractiveSession()
        sess._hug = 'comfy'
        assert sess.hug == sess._hug


class TestDocument(TestInteractiveSession):
    '''
    Tests for InteractiveSession's management of Document instances.
    '''

    def test_document_1(self):
        '''
        When self._doc is already set.
        '''
        self.session._doc = 5
        assert 5 == self.session.document

    def test_document_2(self):
        '''
        When self._doc is not set but repo_dir is.
        '''
        repo_dir = self.session.set_repo_dir('')
        actual = self.session.document
        assert repo_dir == actual._repo_path

    def test_document_3(self):
        '''
        When self._doc and repo_dir are both unset.
        '''
        actual = self.session.document
        assert self.session._repo_dir == actual._repo_path

    def test_unset_repo_dir(self):
        '''
        Cross-check that the document instance is deleted when the repo_dir is changed.
        '''
        self.session.document
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
            self.session._inbound_conversion_finish(converted='lol')
            assert 'lol' == self.session._inbound_converted
            finished_slot.assert_called_once_with()
        finally:
            signals.inbound.CONVERSION_FINISHED.disconnect(finished_slot)

    def test_views_finished(self):
        "It works."
        finished_slot = make_slot_mock()
        signals.inbound.VIEWS_FINISHED.connect(finished_slot)
        try:
            self.session._inbound_views_finish(views_info='lol')
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
        self.session._inbound_views_info = 'IBV'
        self.session.run_inbound = mock.Mock()
        self.session.run_outbound = mock.Mock()

        self.session._action_start(dtype=dtype, doc=doc, views_info=views_info)

        self.session.run_outbound.assert_called_once_with(views_info='IBV')
        self.session.run_inbound.assert_called_once_with(dtype, doc, views_info)
        assert 2 == self.session._cleanup_for_new_action.call_count

    def test_set_views_unit(self):
        '''
        A unit test (fully mocked) for when ACTION_START receives views_info and not dtype or doc.
        '''
        self.session._cleanup_for_new_action = mock.Mock()
        self.session.run_inbound = mock.Mock()
        views_info = 'IBV'
        self.session.run_outbound = mock.Mock()

        self.session._action_start(views_info=views_info)

        assert self.session._inbound_views_info == 'IBV'
        assert not self.session.run_inbound.called
        self.session.run_outbound.assert_called_once_with(views_info=views_info)
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
        self.session.run_inbound = mock.Mock()
        self.session.run_inbound.side_effect = exceptions.InboundConversionError
        self.session.run_outbound = mock.Mock()

        self.session._action_start(dtype=dtype, doc=doc)

        self.session.run_inbound.assert_called_once_with(dtype, doc, None)
        assert self.session._cleanup_for_new_action.call_count == 2
        assert self.session.run_outbound.call_count == 0

    @pytest.mark.xfail
    def test_when_hg_update_works(self):
        '''
        A unit test (fully mocked) for when running Hug.update() works.
        Initial revision is on a tag.
        '''
        self.session = session.InteractiveSession(vcs='mercurial')
        parent_revision = '99:801774903828 tip'
        target_revision = '40:964b28acc4ee'
        self.session._cleanup_for_new_action = mock.Mock()
        self.session.run_outbound = mock.Mock()
        self.session._hug = mock.Mock()
        self.session._hug.summary = mock.Mock(return_value={'parent': parent_revision})
        self.session._hug.update = mock.Mock()
        self.session._inbound_views_info = 'IBV'

        self.session._action_start(revision=target_revision)

        self.session.run_outbound.assert_called_with(views_info='IBV')
        assert self.session._cleanup_for_new_action.call_count == 2
        assert self.session._hug.update.call_count == 2
        self.session._hug.update.assert_any_call(target_revision)
        # the tag name (the "tip" part) should be removed
        self.session._hug.update.assert_called_with(parent_revision[:-4])  # final call

    @pytest.mark.xfail
    def test_when_hg_update_fails(self):
        '''
        A unit test (fully mocked) for when running Hug.update() fails.
        Initial revision is not on a tag.
        '''
        self.session = session.InteractiveSession(vcs='mercurial')
        parent_revision = '99:801774903828'
        target_revision = '44444444444444444'
        self.session._cleanup_for_new_action = mock.Mock()
        self.session.run_outbound = mock.Mock()
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

        assert self.session.run_outbound.call_count == 0
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
        self.session.run_outbound = mock.Mock()
        self.session._inbound_views_info = 'IBV'

        self.session._action_start(revision=target_revision)

        self.session.run_outbound.assert_called_with(views_info='IBV')
        assert self.session._cleanup_for_new_action.call_count == 2

    def test_everything_works_unmocked(self):
        '''
        An integration test (no mocks) for when everything works and all code paths are excuted.
        '''
        self.session = session.InteractiveSession()
        input_ly = r"""\new Staff { \clef "treble" a''4 b'16 c''2  | \clef "bass" d?2 e!2  | f,,2 fis,2  | }"""
        # pre-condition
        assert not os.path.exists(os.path.join(self.session.get_repo_dir(), 'all_files.mei'))
        # unfortunately we need a mock for this, so we can be sure it was called
        finish_mock = make_slot_mock()
        def finish_side_effect(dtype, placement, document, **kwargs):
            assert 'mei' == dtype
            assert isinstance(document, etree._Element)
            assert os.path.exists(
                os.path.join(self.session.get_repo_dir(), '{}.mei'.format(placement))
                )
        finish_mock.side_effect = finish_side_effect

        signals.outbound.REGISTER_FORMAT.emit(dtype='mei', who='test_everything_works_unmocked')
        signals.outbound.CONVERSION_FINISHED.connect(finish_mock)
        try:
            self.session._action_start(dtype='LilyPond', doc=input_ly)
        finally:
            signals.outbound.UNREGISTER_FORMAT.emit(dtype='mei', who='test_everything_works_unmocked')
            signals.outbound.CONVERSION_FINISHED.disconnect(finish_mock)

        assert os.path.exists(os.path.join(self.session.get_repo_dir(), 'all_files.mei'))
        assert finish_mock.called


class TestRunWorkflow(TestInteractiveSession):
    '''
    Tests for InteractiveSession.run_workflow().
    '''

    def test_new_section_unit(self):
        '''
        A unit test (fully mocked) where everything works and a new section is created.
        '''
        dtype = 'silly format'
        doc = '<silly/>'
        self.session._cleanup_for_new_action = mock.Mock()
        self.session._inbound_views_info = 'IBV'
        self.session.run_inbound = mock.Mock()
        self.session.run_outbound = mock.Mock()

        self.session.run_workflow(dtype=dtype, doc=doc)

        self.session.run_inbound.assert_called_once_with(dtype, doc, None)
        self.session.run_outbound.assert_called_once_with(views_info='IBV')
        assert self.session._cleanup_for_new_action.called

    def test_existing_section_unit(self):
        '''
        A unit test (fully mocked) where everything works and an existing section is modified.
        '''
        dtype = 'silly format'
        doc = '<silly/>'
        sect_id = 'Section XMLID'
        self.session._cleanup_for_new_action = mock.Mock()
        self.session._inbound_views_info = 'IBV'
        self.session.run_inbound = mock.Mock()
        self.session.run_outbound = mock.Mock()

        self.session.run_workflow(dtype=dtype, doc=doc, sect_id=sect_id)

        self.session.run_outbound.assert_called_once_with(views_info='IBV')
        self.session.run_inbound.assert_called_once_with(dtype, doc, sect_id)
        assert self.session._cleanup_for_new_action.called

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
        self.session.run_inbound = mock.Mock()
        self.session.run_inbound.side_effect = exceptions.InboundConversionError
        self.session.run_outbound = mock.Mock()

        self.session.run_workflow(dtype=dtype, doc=doc)

        self.session.run_inbound.assert_called_once_with(dtype, doc, None)
        assert self.session._cleanup_for_new_action.called
        assert self.session.run_outbound.call_count == 0

    def test_new_section(self):
        '''
        An integration test (no mocks) for when everything works and a new <section> is created.
        '''
        self.session = session.InteractiveSession()
        input_ly = r"""\new Staff { \clef "treble" a''4 b'16 c''2  | \clef "bass" d?2 e!2  | f,,2 fis,2  | }"""
        # pre-condition
        assert not os.path.exists(os.path.join(self.session.get_repo_dir(), 'all_files.mei'))
        # unfortunately we need a mock for this, so we can be sure it was called
        finish_mock = make_slot_mock()
        def finish_side_effect(dtype, placement, document, **kwargs):
            assert dtype == 'mei'
            assert isinstance(document, etree._Element)
            assert os.path.exists(
                os.path.join(self.session.get_repo_dir(), '{}.mei'.format(placement))
                )
        finish_mock.side_effect = finish_side_effect

        signals.outbound.REGISTER_FORMAT.emit(dtype='mei', who='test_everything_works_unmocked')
        signals.outbound.CONVERSION_FINISHED.connect(finish_mock)
        try:
            self.session.run_workflow(dtype='LilyPond', doc=input_ly)
        finally:
            signals.outbound.UNREGISTER_FORMAT.emit(dtype='mei', who='test_everything_works_unmocked')
            signals.outbound.CONVERSION_FINISHED.disconnect(finish_mock)

        assert os.path.exists(os.path.join(self.session.get_repo_dir(), 'all_files.mei'))
        assert finish_mock.called


class TestRunOutbound(TestInteractiveSession):
    '''
    Tests for InteractiveSession.run_outbound().
    '''

    @mock.patch('lychee.signals.outbound.CONVERSION_FINISHED')
    @mock.patch('lychee.signals.outbound.STARTED')
    def test_no_formats(self, mock_out_started, mock_out_finished):
        '''
        No formats are registered for outbound conversion.
        '''
        self.session.set_repo_dir('')  # tempdir
        self.session.run_outbound()
        mock_out_started.emit.assert_called_once_with()
        assert mock_out_finished.emit.call_count == 0

    @pytest.mark.xfail
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
        self.session._hug = mock.Mock()
        self.session._hug.summary = mock.Mock(return_value={'tag': 'tip'})
        mock_do_out.return_value = {'placement': None, 'document': None}

        signals.outbound.REGISTER_FORMAT.emit(dtype=outbound_dtype, who='test_single_format')
        try:
            self.session.run_outbound(views_info)
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

    @pytest.mark.xfail
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
        self.session._hug = mock.Mock()
        self.session._hug.summary = mock.Mock(return_value={'parent': '16:96eb6fba2374'})
        mock_do_out.return_value = {'placement': None, 'document': None}

        for dtype in outbound_dtypes:
            signals.outbound.REGISTER_FORMAT.emit(dtype=dtype, who='test_single_format')
        try:
            self.session.run_outbound(views_info)
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
        mock_do_out.return_value = {'placement': None, 'document': None}

        signals.outbound.REGISTER_FORMAT.emit(dtype=outbound_dtype, who='test_single_format')
        try:
            self.session.run_outbound(views_info)
        finally:
            signals.outbound.UNREGISTER_FORMAT.emit(dtype=outbound_dtype, who='test_single_format')

        mock_out_started.emit.assert_called_once_with()
        mock_do_out.assert_called_once_with(
            self.session.get_repo_dir(),
            views_info,
            outbound_dtype,
            mock.ANY)
        mock_out_finished.emit.assert_called_once_with(
            dtype=outbound_dtype,
            placement=mock_do_out.return_value['placement'],
            document=mock_do_out.return_value['document'],
            changeset='')

    @pytest.mark.xfail
    @mock.patch('lychee.workflow.steps.do_outbound_steps')
    def test_when_hg_update_works(self, mock_do_out):
        '''
        A unit test (fully mocked) for when running Hug.update() works.
        Initial revision is on a tag.
        '''
        self.session = session.InteractiveSession(vcs='mercurial')
        parent_revision = '99:801774903828 tip'
        target_revision = '40:964b28acc4ee'
        self.session._registrar.register('mei')
        self.session._cleanup_for_new_action = mock.Mock()
        self.session._hug = mock.Mock()
        self.session._hug.summary = mock.Mock(return_value={'parent': parent_revision})
        self.session._hug.update = mock.Mock()
        self.session._repo_dir = '/path/to/repo'
        views_info = 'IBV'

        self.session.run_outbound(views_info=views_info, revision=target_revision)

        mock_do_out.assert_called_with('/path/to/repo', views_info, 'mei')
        assert self.session._cleanup_for_new_action.called
        assert self.session._hug.update.call_count == 2
        self.session._hug.update.assert_any_call(target_revision)
        # the tag name (the "tip" part) should be removed
        self.session._hug.update.assert_called_with(parent_revision[:-4])  # final call

    @pytest.mark.xfail
    @mock.patch('lychee.workflow.steps.do_outbound_steps')
    def test_when_hg_update_fails(self, mock_do_out):
        '''
        A unit test (fully mocked) for when running Hug.update() fails.
        Initial revision is not on a tag.
        '''
        self.session = session.InteractiveSession(vcs='mercurial')
        parent_revision = '99:801774903828'
        target_revision = '44444444444444444'
        self.session._cleanup_for_new_action = mock.Mock()
        self.session._hug = mock.Mock()
        self.session._hug.summary = mock.Mock(return_value={'parent': parent_revision})
        # we need a complicated mock here so one call to update() fails, but the 2nd, in the finally
        # suite, won't fail
        def update_effect(revision):
            "side-effect for Hug.update()"
            if revision != parent_revision:
                raise RuntimeError('=^.^=  meow')
        self.session._hug.update = mock.Mock(side_effect=update_effect)
        self.session._repo_dir = '/path/to/repo'

        self.session.run_outbound(revision=target_revision)

        assert not mock_do_out.called
        assert self.session._cleanup_for_new_action.called
        assert self.session._hug.update.call_count == 2
        self.session._hug.update.assert_any_call(target_revision)
        self.session._hug.update.assert_called_with(parent_revision)  # final call

    @mock.patch('lychee.workflow.steps.do_outbound_steps')
    def test_revision_ignored(self, mock_do_out):
        '''
        A unit test (fully mocked) to check the "revision" argument is ignored if VCS is disabled.
        NB: there would be an AttributeError if the VCS isn't enabled
        '''
        target_revision = '40:964b28acc4ee'
        self.session._registrar.register('mei')
        self.session._cleanup_for_new_action = mock.Mock()
        views_info = 'IBV'

        self.session.run_outbound(views_info=views_info, revision=target_revision)

        mock_do_out.assert_called_with(self.session.get_repo_dir(), views_info, 'mei', mock.ANY)
        assert self.session._cleanup_for_new_action.called


class TestRunInboundDocVcs(TestInteractiveSession):
    '''
    Tests for run_inbound(), a helper method for _action_start().
    '''

    @mock.patch('lychee.workflow.steps.do_inbound_conversion')
    @mock.patch('lychee.workflow.steps.do_inbound_views')
    @mock.patch('lychee.workflow.steps.do_document')
    @mock.patch('lychee.workflow.steps.do_vcs')
    def test_run_inbound_unit_1a(self, mock_vcs, mock_doc, mock_views, mock_conv):
        '''
        Unit test for run_inbound().

        - do_inbound_conversion() is called correctly
        - do_inbound_conversion() fails so there's an early return
        - the following functions aren't called
        '''
        dtype = 'meh'
        doc = 'document'
        views_info = 'Section XMLID'

        with pytest.raises(exceptions.InboundConversionError):
            self.session.run_inbound(dtype, doc, views_info)

        mock_conv.assert_called_once_with(
            session=self.session,
            dtype=dtype,
            document=doc,
            user_settings={})
        assert not mock_views.called
        assert not mock_doc.called
        assert not mock_vcs.called

    @mock.patch('lychee.workflow.steps.do_inbound_conversion')
    def test_run_inbound_unit_1b(self, mock_conv):
        '''
        Unit test for run_inbound().

        - do_inbound_conversion() is called correctly
        - do_inbound_conversion() returns an incorrect value so there's an early return
        '''
        dtype = 'meh'
        doc = 'document'
        views_info = 'Section XMLID'
        self.session._inbound_converted = 'this is not an LMEI document'

        with pytest.raises(exceptions.InboundConversionError):
            self.session.run_inbound(dtype, doc, views_info)

        mock_conv.assert_called_once_with(
            session=self.session,
            dtype=dtype,
            document=doc,
            user_settings={})

    @mock.patch('lychee.workflow.steps.do_inbound_conversion')
    @mock.patch('lychee.workflow.steps.do_inbound_views')
    @mock.patch('lychee.workflow.steps.do_document')
    @mock.patch('lychee.workflow.steps.do_vcs')
    def test_run_inbound_unit_2a(self, mock_vcs, mock_doc, mock_views, mock_conv):
        '''
        Unit test for run_inbound().

        - do_inbound_views() is called correctly
        - do_inbound_views() fails so there's an early return
        - the following functions aren't called
        '''
        dtype = 'meh'
        doc = 'document'
        views_info = 'Section XMLID'
        def mock_conv_side_effect(**kwargs):
            """Assign the conversion result."""
            kwargs['session']._inbound_converted = etree.Element('whatever')
        mock_conv.side_effect = mock_conv_side_effect

        with pytest.raises(exceptions.InboundConversionError):
            self.session.run_inbound(dtype, doc, views_info)

        assert mock_conv.called
        mock_views.assert_called_once_with(
            session=self.session,
            dtype=dtype,
            document=doc,
            converted=self.session._inbound_converted,
            views_info=views_info)
        assert not mock_doc.called
        assert not mock_vcs.called

    @mock.patch('lychee.workflow.steps.do_inbound_conversion')
    @mock.patch('lychee.workflow.steps.do_inbound_views')
    def test_run_inbound_unit_2b(self, mock_views, mock_conv):
        '''
        Unit test for run_inbound().

        - do_inbound_views() is called correctly
        - do_inbound_views() returns an incorrect value so there's an early return
        '''
        dtype = 'meh'
        doc = 'document'
        views_info = 'Section XMLID'
        def mock_conv_side_effect(**kwargs):
            """Assign the conversion result."""
            kwargs['session']._inbound_converted = etree.Element('whatever')
        mock_conv.side_effect = mock_conv_side_effect
        def mock_views_side_effect(**kwargs):
            """Assign the views result."""
            kwargs['session']._inbound_views_info = 4  # expecting str
        mock_views.side_effect = mock_views_side_effect

        with pytest.raises(exceptions.InboundConversionError):
            self.session.run_inbound(dtype, doc, views_info)

        assert mock_conv.called
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
        Unit test for run_inbound().

        - do_document() is called correctly
        - do_vcs() is called correctly
        '''
        dtype = 'meh'
        doc = 'document'
        views_info = 'Section XMLID'
        def mock_conv_side_effect(**kwargs):
            """Assign the conversion result."""
            kwargs['session']._inbound_converted = etree.Element('whatever')
        mock_conv.side_effect = mock_conv_side_effect
        def mock_views_side_effect(**kwargs):
            """Assign the views result."""
            kwargs['session']._inbound_views_info = 'something'
        mock_views.side_effect = mock_views_side_effect
        mock_doc.return_value = ['pathnames!']

        self.session.run_inbound(dtype, doc, views_info)

        assert mock_conv.called
        assert mock_views.called
        mock_doc.assert_called_once_with(
            converted=self.session._inbound_converted,
            session=self.session,
            views_info=self.session._inbound_views_info)
        mock_vcs.assert_called_once_with(session=self.session, pathnames=mock_doc.return_value)


class TestUserSettings(TestInteractiveSession):
    '''
    Test the helper methods write_user_settings and read_user_settings.
    '''

    def test_write_read_user_settings(self):
        '''A dictionary written to and read from user settings is preserved.'''
        # Necessary to initialize the temporary directory.
        self.session.set_repo_dir('')

        user_settings = {
            'heWasA': 'sk8er boi',
            'sheSaid': 'see you l8er boi',
            }
        self.session.write_user_settings(user_settings)

        repo_dir = self.session.get_repo_dir()
        print(repo_dir)
        assert os.path.exists(os.path.join(repo_dir, session.USER_SETTINGS_FILE))

        actual_user_settings = self.session.read_user_settings()
        assert actual_user_settings == user_settings

    def test_inbound_lilypond_language_creates_user_settings(self):
        '''Integration test of inbound LilyPond language.'''
        input_ly = r"""\language "deutsch" \new Staff { h'4 }"""
        self.session.run_inbound(dtype='LilyPond', doc=input_ly)

        user_settings = self.session.read_user_settings()
        assert user_settings == {'lilyPondLanguage': 'deutsch'}

    def test_lilypond_language(self):
        '''Integration test of inbound + outbound LilyPond language.'''
        input_ly = r"""\language "deutsch" \new Staff { h'4 }"""
        self.session.run_inbound(dtype='LilyPond', doc=input_ly)

        def action(document, **kwargs):
            assert r'\language "deutsch"' in document

        signals.outbound.REGISTER_FORMAT.emit(dtype="lilypond")
        signals.outbound.CONVERSION_FINISHED.connect(action)
        self.session.run_workflow(dtype="LilyPond", doc=input_ly)
