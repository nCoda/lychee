#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/workflow/steps.py
# Purpose:                Functions to combine as "steps" in a workflow action.
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
Functions to combine as "steps" in a workflow action.

.. caution:: We intend the functions in this module to be used by primarily an
    :class:`~lychee.workflow.session.InteractiveSession` instance, which knows the proper sequencing
    and error-handling strategies. We invite you to use this module too when you are extending and
    working with Lychee, but be careful---mistakes in the order or the input data can cause loss or
    corruption of the Lychee-MEI document and repository.

The module defines several "steps," which follow a determinate order but are not all mandatory:

#. inbound conversion
#. inbound views
#. document
#. VCS
#. outbound views
#. outbound conversion

Also note that the steps need not necessarily happen in order, sequentially, or only once per Lychee
"action." For example, the VCS step can happen simultaneously with most of the outbound
views/conversion steps. The views/conversion steps themselves are likely to happen several times,
possibly simultaneously, depending on which outbound formats are registered.
'''

from lxml import etree

import lychee
from lychee.namespaces import mei


def do_inbound_conversion(session):
    '''
    '''
    raise NotImplementedError()


def do_inbound_views(session):
    '''
    '''
    raise NotImplementedError()


def do_document(session, converted, views_info):
    '''
    Run the "document" step.

    :param session:
    :param converted:
    :param views_info:
    :returns: A list of the pathnames in this Lychee-MEI document.
    :rtype: list of str

    .. note:: This function is only partially implemented. At the moment, it simply replaces the
        active score with a new one containing only the just-converted ``<section>``.
    '''
    lychee.log('Beginning the "document" step.')

    score = etree.Element(mei.SCORE)
    score.append(converted)
    doc = session.get_document()
    doc.put_score(score)
    document_pathnames = doc.save_everything()

    lychee.log('Finished the "document" step.')

    return document_pathnames


def do_vcs(session):
    '''
    '''
    raise NotImplementedError()


def do_outbound_views(session):
    '''
    '''
    raise NotImplementedError()


def do_outbound_conversion(session):
    '''
    '''
    raise NotImplementedError()
