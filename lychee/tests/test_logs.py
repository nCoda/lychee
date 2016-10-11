#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/tests/test_logs.py
# Purpose:                Tests for Lithoxyl log helpers.
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
"""
Tests for Lithoxyl log helpers.
"""

try:
    from unittest import mock
except ImportError:
    import mock

import pytest
import signalslot

import lychee.logs
import lychee.signals


@pytest.fixture
def event_mock():
    event = mock.Mock()
    event.level_name = 'warning'
    event.logger = mock.Mock()
    event.logger.name = 'outbound'
    event.end_event = mock.Mock()
    event.end_event.message = 'did it!'
    event.status = 'exception'
    event.etime = 400.28910
    return event


class TestLycheeFormatter(object):
    """
    For :class:`LycheeFormatter`.
    """

    def run_test(self, this_method, event):
        """
        Run a test on one of the :class:`LycheeFormatter` methods, each of which behaves identically.

        :param this_method: A method on a :class:`LycheeFormatter` instance.
        :param event: An "event" mock from the :func:`event_mock` fixture.
        """
        actual = this_method(event)
        assert actual == {
            'level': event.level_name.upper(),
            'logger': event.logger.name,
            'message': event.end_event.message,
            'status': event.status,
            'time': str(event.etime),
        }

    def test_begin(self, event_mock):
        formatter = lychee.logs.LycheeFormatter()
        self.run_test(formatter.on_begin, event_mock)

    def test_warn(self, event_mock):
        formatter = lychee.logs.LycheeFormatter()
        self.run_test(formatter.on_warn, event_mock)

    def test_end(self, event_mock):
        formatter = lychee.logs.LycheeFormatter()
        self.run_test(formatter.on_end, event_mock)

    def test_comment(self, event_mock):
        formatter = lychee.logs.LycheeFormatter()
        self.run_test(formatter.on_comment, event_mock)


class TestLycheeEmitter(object):
    """
    For :class:`LycheeEmitter`.
    """

    def run_test(self, this_method):
        """
        Run a test on one of the :class:`LycheeEmitter` methods, each of which behaves identically.

        :param this_method: A method on a :class:`LycheeFormatter` instance.
        """
        slot = mock.MagicMock(spec=signalslot.slot.BaseSlot)
        slot.is_alive = True
        try:
            lychee.signals.LOG_MESSAGE.connect(slot)
            this_method('action', {'level': 'level', 'logger': 'logger',  'message': 'message', 'status': 'status', 'time': 'time'})
        finally:
            lychee.signals.LOG_MESSAGE.disconnect(slot)
        slot.assert_called_with(
            level='level',
            logger='logger',
            message='message',
            status='status',
            time='time'
        )

    def test_begin(self):
        emitter = lychee.logs.LycheeEmitter()
        self.run_test(emitter.on_begin)

    def test_warn(self):
        emitter = lychee.logs.LycheeEmitter()
        self.run_test(emitter.on_warn)

    def test_end(self):
        emitter = lychee.logs.LycheeEmitter()
        self.run_test(emitter.on_end)

    def test_comment(self):
        emitter = lychee.logs.LycheeEmitter()
        self.run_test(emitter.on_comment)
