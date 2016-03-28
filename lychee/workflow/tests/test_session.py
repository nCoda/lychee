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


from lychee.converters import registrar
from lychee import signals
from lychee.workflow import session


class TestInteractiveSession(object):
    '''
    Tests for the InteractiveSession object.
    '''

    def test_init_1(self):
        '''
        Everything works as intended.
        '''
        actual = session.InteractiveSession()
        assert isinstance(actual._registrar, registrar.Registrar)
        assert signals.outbound.REGISTER_FORMAT.is_connected(actual._registrar.register)
        assert signals.outbound.UNREGISTER_FORMAT.is_connected(actual._registrar.unregister)
