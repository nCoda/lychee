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

from lxml import etree

from lychee.namespaces import mei, xml
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
