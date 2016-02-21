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
    When we have Fujian, the Signal should call write_message() and behave like a regular
    signal (no args).
    '''
    mock_fujian = mock.Mock()
    mock_fujian.write_message = mock.Mock()
    signal._module_fujian = mock_fujian
    slot_mock = mock.Mock()
    def slot(**kwargs):
        slot_mock(**kwargs)
    sig_name = 'TestSignal'
    sig = signal.Signal(name=sig_name)
    sig.connect(slot)

    sig.emit()

    assert sig_name == sig.name
    mock_fujian.write_message.assert_called_once_with({'signal': sig_name})
    slot_mock.assert_called_once_with()

def test_emit_with_fujian_2():
    '''
    When we have Fujian with write_message() isn't there, the Signal should not explod when it tries
    calling write_message(), and then should behave like a regular signal (no args).
    '''
    mock_fujian = 5  # doesn't have a write_message() method
    slot_mock = mock.Mock()
    def slot(**kwargs):
        slot_mock(**kwargs)
    sig_name = 'TestSignal'
    sig = signal.Signal(name=sig_name)
    sig.connect(slot)

    sig.emit()

    assert sig_name == sig.name
    slot_mock.assert_called_once_with()

def test_emit_with_fujian_3():
    '''
    When we have Fujian, the Signal should call write_message() and behave like a regular
    signal (with args, no lxml Element).
    '''
    mock_fujian = mock.Mock()
    mock_fujian.write_message = mock.Mock()
    signal._module_fujian = mock_fujian
    slot_mock = mock.Mock()
    def slot(**kwargs):
        slot_mock(**kwargs)
    sig_name = 'TestSignal'
    sig = signal.Signal(name=sig_name, args=['a', 'b'])
    sig.connect(slot)

    sig.emit(a=1, b=2)

    assert sig_name == sig.name
    mock_fujian.write_message.assert_called_once_with({'signal': sig_name, 'a': '1', 'b': '2'})
    slot_mock.assert_called_once_with(a=1, b=2)

def test_emit_with_fujian_4():
    '''
    When we have Fujian, the Signal should call write_message() and behave like a regular
    signal (with an lxml Element arg, and one missing arg).
    '''
    mock_fujian = mock.Mock()
    mock_fujian.write_message = mock.Mock()
    signal._module_fujian = mock_fujian
    slot_mock = mock.Mock()
    def slot(**kwargs):
        slot_mock(**kwargs)
    sig_name = 'TestSignal'
    sig = signal.Signal(name=sig_name, args=['a', 'b'])
    sig.connect(slot)
    elem = etree.Element('note')
    exp_elem = etree.tostring(elem)

    sig.emit(a=elem)

    assert sig_name == sig.name
    mock_fujian.write_message.assert_called_once_with({'signal': sig_name, 'a': exp_elem})
    slot_mock.assert_called_once_with(a=elem)

def test_emit_with_fujian_5():
    '''
    When we have Fujian, the Signal should call write_message() and behave like a regular
    signal (with a dict).
    '''
    mock_fujian = mock.Mock()
    mock_fujian.write_message = mock.Mock()
    signal._module_fujian = mock_fujian
    slot_mock = mock.Mock()
    def slot(**kwargs):
        slot_mock(**kwargs)
    sig_name = 'TestSignal'
    sig = signal.Signal(name=sig_name, args=['a'])
    sig.connect(slot)
    the_dict = {'number': 42}
    exp_dict = '{"number": 42}'

    sig.emit(a=the_dict)

    assert sig_name == sig.name
    mock_fujian.write_message.assert_called_once_with({'signal': sig_name, 'a': exp_dict})
    slot_mock.assert_called_once_with(a=the_dict)
