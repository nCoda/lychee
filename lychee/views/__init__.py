#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/views/__init__.py
# Purpose:                Initialize the "views" module.
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
Initialize the :mod:`views` module.
'''

import lychee
from lychee.signals import inbound, outbound


def inbound_views_processor(dtype, doc, converted, **kwargs):
    inbound.VIEWS_STARTED.emit()
    lychee.log('{}.inbound_views_processor("{}", "{}", "{}")'.format(__name__, dtype, doc, converted))
    #inbound.VIEWS_ERROR.emit()
    inbound.VIEWS_FINISH.emit(views_info='<serialized views info>')
    lychee.log('{}.inbound_views_processor() after finish signal'.format(__name__))

def outbound_views_processor(dtype, **kwargs):
    outbound.VIEWS_STARTED.emit()
    lychee.log('{}.outbound_views_processor("{}")'.format(__name__, dtype))
    #outbound.VIEWS_ERROR.emit()
    outbound.VIEWS_FINISH.emit(dtype=dtype, views_info='<serialized views info>')
    lychee.log('{}.outbound_views_processor() after finish signal'.format(__name__))


inbound.VIEWS_START.connect(inbound_views_processor)
outbound.VIEWS_START.connect(outbound_views_processor)
