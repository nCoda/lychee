#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/registrar.py
# Purpose:                An object to manage registrations of outbound data formats.
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
Registrar: an object to manage registrations of outbound data formats.

The runtime instance is created when Lychee is imported, stored in the :mod:`lychee.__init__`
module.
'''

import six

import lychee
from lychee import signals

# translatable strings
_DTYPE_DOES_NOT_EXIST = 'Cannot register an invalid dtype ({dtype}) for outbound conversion.'
_DTYPE_NOT_REGISTERED = 'Dtype/identifier was already unregistered: {dtype} and {identifier}.'


class Registrar(object):
    '''
    Manage registrations of data formats for production during outbound conversion.

    This class does not manage format conversion. This class accepts registrations and
    unregistrations, and also produces a list of the formats that are currently registered.

    The "who" part of registrations allows Lychee to disambiguate multiple interface components
    that require data in the same format. If one component registers without a ``who`` argument,
    and another component unregisters without a ``who`` argument, :class:`Registrar` cannot know
    that these actions were requested by different components. However, if each interface component
    uses a unique "who" argument, :class:`Registrar` will ensure the data format is always produced
    until all registered components have unregistered themselves.
    '''

    # self._registrations is a dictionary that holds registrations. The currently-registered formats
    # are the dictionary keys. Values are a list of currently registered "who" values. If the "who"
    # argument is omitted, it will be None, so this is represented in the list as None.

    def __init__(self):
        ""
        self._registrations = {}

    def register(self, dtype, who=None, outbound=False, **kwargs):
        '''
        Register a format for outbound conversion.

        :param str dtype: The format to register for conversion.
        :param str who: An optional identifying string.
        :param bool outbound: An optional "True" to specify that the "ACTION_START" signal should
            be emitted after registering the outbound format, which will run the outbound step.

        If ``dtype`` does not have a converter listed in :const:`lychee.converters.OUTBOUND_CONVERTERS`,
        the format will not be registered and WARN message will be written to the log.
        '''
        if dtype not in lychee.converters.OUTBOUND_CONVERTERS:
            lychee.log(_DTYPE_DOES_NOT_EXIST.format(dtype=dtype), 'WARN')
        elif dtype in self._registrations:
            if who not in self._registrations[dtype]:
                self._registrations[dtype].append(who)
        else:
            self._registrations[dtype] = [who]

        if outbound:
            signals.ACTION_START.emit()

    def unregister(self, dtype, who=None, **kwargs):
        '''
        Unregister a format from outbound conversion.

        :param str dtype: The format to register for conversion.
        :param str who: An optional identifying string.

        If the ``dtype`` and ``who`` combination are not currently registered for outbound
        conversion, a DEBUG message will be written to the log.
        '''
        if dtype in self._registrations and who in self._registrations[dtype]:
            if [who] == self._registrations[dtype]:
                del self._registrations[dtype]
            else:
                new_reg = []
                for each_who in self._registrations[dtype]:
                    if who != each_who:
                        new_reg.append(each_who)
                self._registrations[dtype] = new_reg
        else:
            lychee.log(_DTYPE_NOT_REGISTERED.format(dtype=dtype, identifier=who), 'DEBUG')

    def get_registered_formats(self):
        '''
        Return a list of the formats that are currently registered for outbound conversion.

        :returns: The list.
        :rtype: list of str
        '''
        return list(six.iterkeys(self._registrations))
