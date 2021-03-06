#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/test/signal.py
# Purpose:                Tests for Lychee-specific Signal class.
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
Tests for Lychee-specific Signal class.
'''

try:
    from unittest import mock
except ImportError:
    import mock

from lxml import etree

from lychee.signals import signal


def test_have_fujian_1():
    '''When we have Fujian, it returns True.'''
    try:
        signal._module_fujian = 4
        assert signal.have_fujian() is True
    finally:
        signal._module_fujian = None

def test_have_fujian_2():
    '''When we don't have Fujian, it returns False.'''
    assert signal._module_fujian is None  # pre-condition
    assert signal.have_fujian() is False

def test_set_fujian():
    '''signal.set_fujian()'''
    assert signal._module_fujian is None
    to_this = 5
    signal.set_fujian(to_this)
    assert to_this == signal._module_fujian

def test_emit_without_fujian_1():
    '''
    When we don't have Fujian, the Signal should behave like a regular signal (no args).
    '''
    signal._module_fujian = None
    slot_mock = mock.Mock()
    def slot(**kwargs):
        slot_mock(**kwargs)
    sig_name = 'TestSignal'
    sig = signal.Signal(name=sig_name)
    sig.connect(slot)

    sig.emit()

    assert sig_name == sig.name
    slot_mock.assert_called_once_with()

def test_emit_without_fujian_2():
    '''
    When we don't have Fujian, the Signal should behave like a regular signal (with args).
    '''
    signal._module_fujian = None
    slot_mock = mock.Mock()
    def slot(**kwargs):
        slot_mock(**kwargs)
    sig_name = 'TestSignal'
    sig = signal.Signal(name=sig_name, args=['a', 'b'])
    sig.connect(slot)

    sig.emit(a=1, b=2)

    assert sig_name == sig.name
    slot_mock.assert_called_once_with(a=1, b=2)

def test_emit_with_fujian_1():
    '''
    When we have Fujian, the Signal should call signal() and behave like a regular
    signal (no args).
    '''
    mock_fujian = mock.Mock()
    mock_fujian.signal = mock.Mock()
    signal._module_fujian = mock_fujian
    slot_mock = mock.Mock()
    def slot(**kwargs):
        slot_mock(**kwargs)
    sig_name = signal.FUJIAN_INTERESTED_SIGNALS[0]
    sig = signal.Signal(name=sig_name)
    sig.connect(slot)

    sig.emit()

    assert sig_name == sig.name
    mock_fujian.signal.assert_called_once_with(sig_name)
    slot_mock.assert_called_once_with()

def test_emit_with_fujian_2():
    '''
    When we have Fujian with signal() isn't there, the Signal should not explod when it tries
    calling signal(), and then should behave like a regular signal (no args).
    '''
    mock_fujian = 5  # doesn't have a signal() method
    slot_mock = mock.Mock()
    def slot(**kwargs):
        slot_mock(**kwargs)
    sig_name = signal.FUJIAN_INTERESTED_SIGNALS[0]
    sig = signal.Signal(name=sig_name)
    sig.connect(slot)

    sig.emit()

    assert sig_name == sig.name
    slot_mock.assert_called_once_with()

def test_emit_with_fujian_3():
    '''
    When we have Fujian, the Signal should call signal() and behave like a regular
    signal (with args).
    '''
    mock_fujian = mock.Mock()
    mock_fujian.signal = mock.Mock()
    signal._module_fujian = mock_fujian
    slot_mock = mock.Mock()
    def slot(**kwargs):
        slot_mock(**kwargs)
    sig_name = signal.FUJIAN_INTERESTED_SIGNALS[0]
    sig = signal.Signal(name=sig_name, args=['a', 'b'])
    sig.connect(slot)

    sig.emit(a=1, b=2)

    assert sig_name == sig.name
    mock_fujian.signal.assert_called_once_with(sig_name, a=1, b=2)
    slot_mock.assert_called_once_with(a=1, b=2)

def test_emit_with_fujian_4():
    '''
    When we have Fujian but it's not interested in this signal, the Signal should not call signal()
    but should behave like a regular signal.
    '''
    mock_fujian = mock.Mock()
    mock_fujian.signal = mock.Mock()
    signal._module_fujian = mock_fujian
    slot_mock = mock.Mock()
    def slot(**kwargs):
        slot_mock(**kwargs)
    sig_name = 'beep beep honk honk'
    sig = signal.Signal(name=sig_name, args=['a', 'b'])
    sig.connect(slot)
    elem = etree.Element('note')

    sig.emit(a=elem)

    assert sig_name == sig.name
    assert mock_fujian.signal.call_count == 0
    slot_mock.assert_called_once_with(a=elem)
