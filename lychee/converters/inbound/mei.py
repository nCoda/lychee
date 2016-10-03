#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/mei_to_lmei.py
# Purpose:                Converts a conventional MEI document to a Lychee-MEI document.
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
Converts a conventional MEI document to a Lychee-MEI document.

.. danger:: This module is not implemented yet.

.. warning::
    This module is intended for internal *Lychee* use only, so the API may change without notice.
    If you wish to use this module outside *Lychee*, please contact us to discuss the best way.

.. tip::
    We recommend that you use the converters indirectly.
    Refer to :ref:`how-to-use-converters` for more information.
'''

from lychee.logs import INBOUND_LOG as log
from lychee.signals import inbound


def convert(**kwargs):
    '''
    Convert an MEI document into a Lychee-MEI document.

    :param document: The MEI document. Must be provided as a kwarg.
    :type document: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    :returns: The corresponding Lychee-MEI document.
    :rtype: :class:`xml.etree.ElementTree.Element` or :class:`xml.etree.ElementTree.ElementTree`
    '''
    with log.info('convert MEI to LMEI'):
        inbound.CONVERSION_STARTED.emit()
        #inbound.CONVERSION_ERROR.emit()
        inbound.CONVERSION_FINISH.emit(converted='<l-mei stuff>')
