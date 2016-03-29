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

try:
    from unittest import mock
except ImportError:
    import mock

from lxml import etree
import signalslot

from lychee.namespaces import mei, xml
from lychee import signals
from lychee.vcs import hg as vcs_hg_module
from lychee.workflow import steps

from test_session import TestInteractiveSession


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
        doc = self.session.get_document()
        assert [xmlid] == doc.get_section_ids()
        assert [xmlid] == doc.get_section_ids(all_sections=True)
        assert os.path.exists(section_pathname)


class TestVCSStep(TestInteractiveSession):
    '''
    Tests for the "VCS" step.
    '''

    @staticmethod
    def make_slot_mock():
        slot = mock.MagicMock(spec=signalslot.slot.BaseSlot)
        slot.is_alive = True
        return slot

    def test_do_vcs_1(self):
        '''
        That do_vcs() works.
        '''
        signals.vcs.START.disconnect(steps._vcs_driver)
        assert 0 == len(signals.vcs.START.slots)  # pre-condition
        assert 0 == len(signals.vcs.FINISHED.slots)  # pre-condition
        # create and connect some mock slots for vcs.START and vcs.FINISHED
        start_slot = TestVCSStep.make_slot_mock()
        finished_slot = TestVCSStep.make_slot_mock()
        signals.vcs.START.connect(start_slot)
        signals.vcs.FINISHED.connect(finished_slot)

        steps.do_vcs(self.session, ['pathnames'])

        start_slot.assert_called_with(repo_dir=self.session.get_repo_dir(), pathnames=['pathnames'])
        finished_slot.assert_called_with()
        signals.vcs.START.disconnect(start_slot)
        signals.vcs.FINISHED.disconnect(finished_slot)

    def test_vcs_driver_1(self):
        '''
        That _vcs_driver() works.
        '''
        signals.vcs.INIT.disconnect(vcs_hg_module.init_repo)
        signals.vcs.ADD.disconnect(vcs_hg_module.add)
        signals.vcs.COMMIT.disconnect(vcs_hg_module.commit)
        assert 0 == len(signals.vcs.INIT.slots)  # pre-condition
        assert 0 == len(signals.vcs.ADD.slots)  # pre-condition
        assert 0 == len(signals.vcs.COMMIT.slots)  # pre-condition
        init_slot = TestVCSStep.make_slot_mock()
        add_slot = TestVCSStep.make_slot_mock()
        commit_slot = TestVCSStep.make_slot_mock()
        signals.vcs.INIT.connect(init_slot)
        signals.vcs.ADD.connect(add_slot)
        signals.vcs.COMMIT.connect(commit_slot)

        steps._vcs_driver('dir', 'names')

        init_slot.assert_called_with(repodir='dir')
        add_slot.assert_called_with(pathnames='names')
        commit_slot.assert_called_with(message=None)
        signals.vcs.INIT.disconnect(init_slot)
        signals.vcs.ADD.disconnect(add_slot)
        signals.vcs.COMMIT.disconnect(commit_slot)
