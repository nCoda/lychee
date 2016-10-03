#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/test/test_registrar.py
# Purpose:                Tests for the "registrar" module.
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
Tests for the "registrar" module.
'''

try:
    from unittest import mock
except ImportError:
    import mock

from lychee.converters import registrar


class TestSingleDtypeWithoutWho(object):
    def test_1(self):
        '''
        Register a single format without a "who" value.
        Check that it's registered.
        '''
        reg = registrar.Registrar()
        reg.register('mei')
        assert ['mei'] == reg.get_registered_formats()

    def test_2(self):
        '''
        Register a single format without a "who" value many times.
        Check that it's registered once.
        '''
        reg = registrar.Registrar()
        reg.register('mei')
        reg.register('mei')
        reg.register('mei')
        reg.register('mei')
        assert ['mei'] == reg.get_registered_formats()

    def test_3(self):
        '''
        Register a single format without a "who" value.
        Check that it's registered.
        Unregister the format.
        Check that it's unregistered.
        '''
        reg = registrar.Registrar()
        reg.register('mei')
        assert ['mei'] == reg.get_registered_formats()
        reg.unregister('mei')
        assert [] == reg.get_registered_formats()

    def test_4(self):
        '''
        Register a single format without a "who" value many times.
        Check that it's registered once.
        Unregister the format many times.
        Check that it's unregistered.
        '''
        reg = registrar.Registrar()
        reg.register('mei')
        reg.register('mei')
        reg.register('mei')
        reg.register('mei')
        assert ['mei'] == reg.get_registered_formats()
        reg.unregister('mei')
        reg.unregister('mei')
        reg.unregister('mei')
        reg.unregister('mei')
        assert [] == reg.get_registered_formats()

    def test_5(self):
        '''
        Register a single invalid format.
        Check that it doesn't register.
        '''
        reg = registrar.Registrar()
        reg.register('something proprietary')
        assert [] == reg.get_registered_formats()

    def test_6(self):
        '''
        Register a single invalid format many times.
        Check that it doesn't register.
        '''
        reg = registrar.Registrar()
        reg.register('something proprietary')
        reg.register('something proprietary')
        reg.register('something proprietary')
        reg.register('something proprietary')
        assert [] == reg.get_registered_formats()


class TestSingleDtypeWithWho(object):
    def test_1(self):
        '''
        Register a single format with a "who" value.
        Check that it's registered.
        '''
        reg = registrar.Registrar()
        reg.register('mei', '123')
        reg.register('mei', '9903')
        reg.register('mei', 'nuren')
        assert ['mei'] == reg.get_registered_formats()

    def test_2(self):
        '''
        Register a single format with the same "who" value many times.
        Check that it's registered once.
        '''
        reg = registrar.Registrar()
        reg.register('mei', '123')
        reg.register('mei', '9903')
        reg.register('mei', 'nuren')
        reg.register('mei', '9903')
        reg.register('mei', '9903')
        reg.register('mei', '123')
        assert ['mei'] == reg.get_registered_formats()

    def test_3(self):
        '''
        Register a single format with a "who" value.
        Check that it's registered.
        Unregister the format.
        Check that it's unregistered.
        '''
        reg = registrar.Registrar()
        reg.register('mei', '123')
        reg.register('mei', '9903')
        reg.register('mei', 'nuren')
        assert ['mei'] == reg.get_registered_formats()
        reg.unregister('mei', '123')
        assert ['mei'] == reg.get_registered_formats()
        reg.unregister('mei', '9903')
        assert ['mei'] == reg.get_registered_formats()
        reg.unregister('mei', 'nuren')
        assert [] == reg.get_registered_formats()

    def test_4(self):
        '''
        Register a single format with the same "who" value many times.
        Check that it's registered once.
        Unregister the format many times.
        Check that it's unregistered.
        '''
        reg = registrar.Registrar()
        reg.register('mei', '123')
        reg.register('mei', '9903')
        reg.register('mei', 'nuren')
        reg.register('mei', '9903')
        reg.register('mei', '9903')
        reg.register('mei', '123')
        assert ['mei'] == reg.get_registered_formats()

        reg.unregister('mei', '123')
        assert ['mei'] == reg.get_registered_formats()

        reg.unregister('mei', '123')
        reg.unregister('mei', '9903')
        assert ['mei'] == reg.get_registered_formats()

        reg.unregister('mei', '123')
        reg.unregister('mei', '123')
        reg.unregister('mei', 'nuren')
        reg.unregister('mei', '9903')
        reg.unregister('mei', '9903')
        reg.unregister('mei', 'nuren')
        assert [] == reg.get_registered_formats()

    def test_5(self):
        '''
        Register a single invalid format with "who" values.
        Check that it doesn't register.
        '''
        reg = registrar.Registrar()
        reg.register('something proprietary', 'n2n2')
        reg.register('something proprietary', 'n3n3')
        reg.register('something proprietary', 'n4n4')
        assert [] == reg.get_registered_formats()


class TestManyDtypeWithoutWho(object):
    def test_1(self):
        '''
        Register three formats without a "who" value.
        Check that it's registered.
        '''
        reg = registrar.Registrar()
        reg.register('mei')
        reg.register('verovio')
        reg.register('lilypond')
        expected = ['mei', 'verovio', 'lilypond']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual

    def test_2(self):
        '''
        Register three formats without a "who" value many times.
        Check that it's registered once.
        '''
        reg = registrar.Registrar()
        reg.register('mei')
        reg.register('verovio')
        reg.register('lilypond')
        reg.register('mei')
        reg.register('verovio')
        reg.register('lilypond')
        reg.register('mei')
        reg.register('verovio')
        reg.register('lilypond')
        expected = ['mei', 'verovio', 'lilypond']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual

    def test_3(self):
        '''
        Register three formats without a "who" value.
        Check that it's registered.
        Unregister the formats one by one.
        Check that it's unregistered.
        '''
        reg = registrar.Registrar()
        reg.register('mei')
        reg.register('verovio')
        reg.register('lilypond')
        expected = ['mei', 'verovio', 'lilypond']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual

        reg.unregister('mei')
        expected = ['verovio', 'lilypond']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual

        reg.unregister('verovio')
        assert ['lilypond'] == reg.get_registered_formats()

        reg.unregister('lilypond')
        assert [] == reg.get_registered_formats()

    def test_4(self):
        '''
        Register a single format without a "who" value many times.
        Check that it's registered once.
        Unregister the format many times.
        Check that it's unregistered.
        '''
        reg = registrar.Registrar()
        reg.register('mei')
        reg.register('verovio')
        reg.register('lilypond')
        reg.register('mei')
        reg.register('verovio')
        reg.register('lilypond')
        expected = ['mei', 'verovio', 'lilypond']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual

        reg.unregister('mei')
        expected = ['verovio', 'lilypond']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual

        reg.unregister('mei')
        reg.unregister('verovio')
        reg.unregister('verovio')
        reg.unregister('mei')
        assert ['lilypond'] == reg.get_registered_formats()

        reg.unregister('lilypond')
        reg.unregister('lilypond')
        reg.unregister('mei')
        reg.unregister('verovio')
        assert [] == reg.get_registered_formats()

    def test_5(self):
        '''
        Register a several invalid formats without "who" values.
        Check that they doesn't register.
        '''
        reg = registrar.Registrar()
        reg.register('proprietary 1')
        reg.register('proprietary 2')
        reg.register('proprietary 3')
        assert [] == reg.get_registered_formats()

    def test_6(self):
        '''
        Register a mix of several invalid and valid formats without "who" values.
        Check that they register appropriately.
        '''
        reg = registrar.Registrar()
        reg.register('proprietary 1')
        reg.register('mei')
        reg.register('proprietary 2')
        reg.register('abjad')
        reg.register('proprietary 3')
        expected = ['mei', 'abjad']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual


class TestManyDtypeWithWho(object):
    def test_1(self):
        '''
        Register three formats with two different "who" values.
        Check that it's registered.
        '''
        reg = registrar.Registrar()
        reg.register('mei', '123')
        reg.register('mei', '666')
        reg.register('verovio', '123')
        reg.register('verovio', '666')
        reg.register('lilypond', '123')
        reg.register('lilypond', '666')
        expected = ['mei', 'verovio', 'lilypond']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual

    def test_2(self):
        '''
        Register three formats with two different "who" values many times.
        Check that it's registered once.
        '''
        reg = registrar.Registrar()
        reg.register('mei', '123')
        reg.register('mei', '666')
        reg.register('verovio', '123')
        reg.register('verovio', '666')
        reg.register('lilypond', '123')
        reg.register('lilypond', '666')
        reg.register('mei', '123')
        reg.register('mei', '666')
        reg.register('verovio', '123')
        reg.register('verovio', '666')
        reg.register('lilypond', '123')
        reg.register('lilypond', '666')
        expected = ['mei', 'verovio', 'lilypond']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual

    def test_3(self):
        '''
        Register three formats with two "who" values.
        Check that it's registered.
        Unregister the formats one by one.
        Check that it's unregistered.
        '''
        reg = registrar.Registrar()
        reg.register('mei', '123')
        reg.register('mei', '666')
        reg.register('verovio', '123')
        reg.register('verovio', '666')
        reg.register('lilypond', '123')
        reg.register('lilypond', '666')
        expected = ['mei', 'verovio', 'lilypond']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual

        # unregister the '123' component
        reg.unregister('mei', '123')
        reg.unregister('verovio', '123')
        reg.unregister('lilypond', '123')
        expected = ['mei', 'verovio', 'lilypond']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual

        # unregister the '666' component
        reg.unregister('mei', '666')
        reg.unregister('verovio', '666')
        reg.unregister('lilypond', '666')
        assert [] == reg.get_registered_formats()

    def test_4(self):
        '''
        Register a single format with two "who" values many times.
        Check that it's registered once.
        Unregister the format many times.
        Check that it's unregistered.
        '''
        reg = registrar.Registrar()
        reg.register('mei', '123')
        reg.register('mei', '666')
        reg.register('verovio', '123')
        reg.register('verovio', '666')
        reg.register('lilypond', '123')
        reg.register('lilypond', '666')
        reg.register('mei', '123')
        reg.register('mei', '666')
        reg.register('verovio', '123')
        reg.register('verovio', '666')
        reg.register('lilypond', '123')
        reg.register('lilypond', '666')
        expected = ['mei', 'verovio', 'lilypond']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual

        # unregister the '123' component
        reg.unregister('mei', '123')
        reg.unregister('verovio', '123')
        reg.unregister('lilypond', '123')
        expected = ['mei', 'verovio', 'lilypond']
        actual = reg.get_registered_formats()
        assert len(expected) == len(actual)
        for each in expected:
            assert each in actual

        # unregister the '666' component
        reg.unregister('mei', '123')
        reg.unregister('verovio', '123')
        reg.unregister('lilypond', '123')
        reg.unregister('mei', '666')
        reg.unregister('verovio', '666')
        reg.unregister('lilypond', '666')
        reg.unregister('mei', '666')
        reg.unregister('verovio', '666')
        reg.unregister('lilypond', '666')
        reg.unregister('mei', '666')
        reg.unregister('verovio', '666')
        reg.unregister('lilypond', '666')
        assert [] == reg.get_registered_formats()


class TestRegisterOutbound(object):
    '''
    Make sure the register() method's "outbound" argument works as advertised.
    '''

    @mock.patch('lychee.converters.registrar.signals')
    def test_true(self, mock_signals):
        '''
        When the "outbound" argument is True, emit the ACTION_START signal.
        '''
        reg = registrar.Registrar()
        reg.register('mei', '111', True)
        mock_signals.ACTION_START.emit.assert_called_with()

    @mock.patch('lychee.converters.registrar.signals')
    def test_false(self, mock_signals):
        '''
        When the "outbound" argument is False, do not emit the ACTION_START signal.
        '''
        reg = registrar.Registrar()
        reg.register('mei', '111', False)
        assert mock_signals.ACTION_START.emit.call_count == 0

    @mock.patch('lychee.converters.registrar.signals')
    def test_registration_fails(self, mock_signals):
        '''
        When the "outbound" argument is True but the "dtype" does not exist, registration will fail
        and the ACTION_START signal is not emitted.
        '''
        reg = registrar.Registrar()
        reg.register('WrongMEI', '111', True)
        assert len(reg.get_registered_formats()) == 0
        assert mock_signals.ACTION_START.emit.call_count == 0


# Okay, I think that's far enough overboard for this module...
