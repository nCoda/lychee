#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/signals/__init__.py
# Purpose:                Initialize the "signals" module.
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

# NOTE that you must import the :mod:`lychee.signals.workflow` separately because it isn't imported
# by ``from lychee import *`` by default, because it caused too much trouble.

__all__ = ['document', 'inbound', 'vcs', 'outbound']
from . import *

from . import signal


def set_fujian(to_this):
    '''
    Call this with a :class:`fujian.FujianWebSocketHandler` instance. :class:`Signal` instances will
    use it to emit themselves over the WebSocket connection.
    '''
    from . import signal
    signal.set_fujian(to_this)


ACTION_START = signal.Signal(args=['dtype', 'doc', 'views_info'], name='ACTION_START')
'''
Emit this signal to start an "action" through Lychee.

:kwarg str dtype: The format (data type) of the inbound musical document. LilyPond, Abjad, etc.
:kwarg object doc: The inbound musical document. The required type is determined by each converter
    module individually.
:kwarg str views_info: Information for "views processing," being the @xml:id of the relevant
    ``<section>`` element. If the ``doc`` argument is also provided, this value *overrides* an
    @xml:id that may be assigned in ``doc``, which is assumed to correspond to the external format.
    If the ``doc`` argument is omitted, ``views_info`` is used for an outbound-only workflow.

**Outbound-only Workflow**

You can trigger the outbound steps for all registered outbound formats by emitting this signal
without the ``dtype`` or ``doc`` arguments. You may also specify that only a ``<section>`` or portion
of a ``<section>`` should be sent for outbound conversion by providing the @xml:id attribute of the
element you wish to convert.

For example:

>>> signals.ACTION_START.emit()

This causes the full score to be converted for all registered outbound data types. On the other hand:

>>> signals.ACTION_START.emit(views_info='Sme-s-m-l-e1182873')

This causes only the ``<section>`` with ``@xml:id="Sme-s-m-l-e1182873"`` to be sent for outbound
conversion.

.. note:: You should provide ``dtype`` and ``doc``, or ``views_info`` by itself.
'''
