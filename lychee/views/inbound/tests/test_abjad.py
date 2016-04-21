#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/views/inbound/tests/abjad.py
# Purpose:                Tests for inbound views processing for Abjad.
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
Tests for inbound views processing for Abjad.
'''

import pytest
import signalslot

try:
    from unittest import mock
except ImportError:
    import mock

import lychee
from lychee import exceptions
from lychee import signals
from lychee.views.inbound import abjad


@pytest.fixture()
def mock_signals(request):
    '''
    This PyTest fixture puts mock slots on the VIEWS_STARTED, VIEWS_FINISH, and VIEWS_ERROR signals.

    :returns: A dictionary with keys "started", "finish", and "error", and values being the mock
        slot for the corresponding signal.
    '''
    post = {
        'started': mock.MagicMock(spec=signalslot.slot.BaseSlot),
        'finish': mock.MagicMock(spec=signalslot.slot.BaseSlot),
        'error': mock.MagicMock(spec=signalslot.slot.BaseSlot),
    }
    post['started'].is_alive = True
    post['finish'].is_alive = True
    post['error'].is_alive = True

    signals.inbound.VIEWS_STARTED.connect(post['started'])
    signals.inbound.VIEWS_FINISH.connect(post['finish'])
    signals.inbound.VIEWS_ERROR.connect(post['error'])

    def disconnect_slots():
        "Disconnect the mock slots."
        signals.inbound.VIEWS_STARTED.disconnect(post['started'])
        signals.inbound.VIEWS_FINISH.disconnect(post['finish'])
        signals.inbound.VIEWS_ERROR.disconnect(post['error'])
    request.addfinalizer(disconnect_slots)

    return post


class TestPlaceView(object):
    '''
    Tests for the place_view() function.
    '''

    @mock.patch('lychee.views.inbound.abjad._place_view')
    def test_success(self, mock__place, mock_signals):
        '''
        The conversion is successful.
        '''
        expected = 'fourteen'
        mock__place.return_value = expected
        converted = 'ddd'
        document = 'eee'
        session = 'fff'

        assert abjad.place_view(converted, document, session) is None

        mock__place.assert_called_with(converted, document, session)
        mock_signals['started'].assert_called_with()
        mock_signals['finish'].assert_called_with(views_info=expected)
        assert mock_signals['error'].call_count == 0

    @mock.patch('lychee.views.inbound.abjad._place_view')
    def test_fail_debug(self, mock__place, mock_signals):
        '''
        The conversion fails and DEBUG is True.
        '''
        mock__place.side_effect = RuntimeError()
        converted = 'ddd'
        document = 'eee'
        session = 'fff'

        orig_DEBUG = lychee.DEBUG
        try:
            lychee.DEBUG = True
            with pytest.raises(RuntimeError):
                abjad.place_view(converted, document, session)
        finally:
            lychee.DEBUG = orig_DEBUG

        mock_signals['started'].assert_called_with()
        assert mock_signals['error'].call_count == 0
        assert mock_signals['finish'].call_count == 0

    @mock.patch('lychee.views.inbound.abjad._place_view')
    def test_fail_nodebug(self, mock__place, mock_signals):
        '''
        The conversion fails and DEBUG is False.
        '''
        mock__place.side_effect = RuntimeError()
        converted = 'ddd'
        document = 'eee'
        session = 'fff'

        orig_DEBUG = lychee.DEBUG
        try:
            lychee.DEBUG = False
            assert abjad.place_view(converted, document, session) is None
        finally:
            lychee.DEBUG = orig_DEBUG

        mock__place.assert_called_with(converted, document, session)
        mock_signals['started'].assert_called_with()
        mock_signals['error'].assert_called_with(msg=abjad._GENERIC_ERROR.format('RuntimeError()'))
        assert mock_signals['finish'].call_count == 0

def test__seven_digits():
    '''
    _seven_digits()

    Copied from lychee.document.
    '''
    # Statistically, ten percent of the initial strings should begin with a zero. Given that,
    # calling _seven_digits() 100 times gives us a pretty good chance of hitting that case at
    # least once.
    for _ in range(100):
        actual = abjad._seven_digits()
        assert 7 == len(actual)
        assert not actual.startswith('0')
        assert int(actual)
