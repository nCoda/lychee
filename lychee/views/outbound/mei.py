#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/views/outbound/mei.py
# Purpose:                Outbound views processing for MEI.
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
Outbound views processing for MEI.
'''

from lychee import document


def get_view(repo_dir, views_info, dtype):  # TODO: untested until T33
    '''
    Do the outbound views processing for the provided document. In other words, this function lets
    you get a "view" on Lychee's document.

    Parameters are the same as :func:`lychee.workflow.steps.do_outbound_steps`.

    :returns: A two-tuple of views information for the ``CONVERSION_FINISHED`` signal, and the
        Lychee-MEI document portion corresponding to ``views_info``.
    :rtype: 2-tuple of string and :class:`~lxml.etree.Element`
    '''
    if not views_info.startswith('Sme-'):
        raise NotImplementedError('MEI outbound views can only process <section> elements so far.')
    else:
        doc = document.Document(repo_dir)
        return views_info, doc.get_section(views_info)
