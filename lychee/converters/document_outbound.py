#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/document_outbound.py
# Purpose:                "Converts" document metadata into an easier format for clients.
#
# Copyright (C) 2015 Christopher Antila
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
"Converts" document metadata into an easier format for clients.

NOTE: this module is likely to be rewritten, because I don't think I can accurately predict what
    it needs to do and how.

This module essentially uses the :mod:`lychee.document` module to extract metadata about the
internal LMEI document so it may be used by UIs.

Output Sample
-------------

Here is a sample of the data outputted from this module. This includes all possible values, but a
real score is unlikely to do so.

{
    'headers': {
        'fileDesc': {
            'titleStmt': {
                'title': {
                    'main': 'This is the Main Title',
                    'subordinate': 'This is a subtitle'
                }
            },
            'respStmt': [
                {
                    'id': 'p1234',
                    'full': 'Danceathon W. Smith',
                    'given': 'Danceathon',
                    'other': 'Wilfreda',
                    'family': 'Smith'
                },
                {
                    'id': 'p5678',
                    'full': '卓文萱',
                    'given': '文萱',
                    'other': 'Genie',
                    'family': '卓'
                },
            ],
            'arranger': {
                'full': 'Robert W. Smith'
            },
            'composer': {
                'id': 'p5678'
            },
            'author': { ... },
            'editor': { ... },
            'funder': { ... },
            'librettist': { ... },
            'lyricist': { ... },
            'sponsor': { ... }
            'pubStmt': {
                'unpub': 'This is an unpublished Lychee-MEI document.'
            }
        }
    },
    'sections': {
        # ??????????????
    }
}

Notes
^^^^^

Following Lychee-MEI, the different members of "title" may be one of the following: main, subordinate,
abbreviated, alternative, translated, uniform. The "main" title will always be included, though it
may be a placeholder.

The "roles" members ("arranger," "composer," and so on) refer to people. They may either use an "id"
field to refer to a user described in the "respStmt" section, or they may contain names.

While the "pubStmt" section is virtually useless as the moment (because Lychee is not aware when
one of its documents becomes published) it is included for completeness. It is required for a
complete and valid MEI document.

Data from the "workDesc" and "revisionDesc" MEI elements will be added later, as peers to the
"fileDesc" member, once they are implemented in Lychee.
'''

from lxml import etree

import lychee
from lychee import document as documentModule
from lychee import exceptions
from lychee.namespaces import mei, xml
from lychee.signals import outbound


# TODO: this should be set automatically
TESTREPO = 'testrepo'


def convert(document, **kwargs):
    '''
    Prepare document metadata in a useful format for clients.

    :param document: Ignored.
    :returns: Information from the internal LMEI document in the format described above.
    :rtype: dict
    '''
    outbound.CONVERSION_STARTED.emit()
    lychee.log('{}.convert() begins'.format(__name__), level='debug')

    try:
        doc = documentModule.Document(TESTREPO)
    except exceptions.HeaderNotFoundError:
        msg = '{} failed initializing a Document object; stopping conversion'.format(__name__)
        outbound.CONVERSION_ERROR.emit(msg=msg)
    else:
        post = {'headers': prepare_headers(doc)}
        outbound.CONVERSION_FINISH.emit(converted=post)
        lychee.log('{}.convert() after finish signal'.format(__name__), level='debug')


def format_person(person):
    '''
    Given a ``<persName>`` :class:`Element` or ``None``, either prepare a dictionary with the
    relevant keys and vales, or return ``None``.

    :param person: The ``<persName`` to convert, or ``None``.
    :type person: :class:`lxml.etree._Element`
    :returns: The converted stuff or ``None``.
    :rtype: dict or NoneType

    This function accepts and returns ``None`` to help simplify functions that call it.
    '''
    # TODO: tests
    post = {}

    if not isinstance(person, etree._Element):
        post = None

    elif person.get('nymref') is not None:
        nymref = person.get('nymref')
        if nymref.startswith('#'):
            nymref = nymref[1:]
        post = {'id': nymref}

    else:
        if person.get(xml.ID) is not None:
            post['id'] = person.get(xml.ID)
        for subElem in person:
            # TODO: check it's a <persName> element
            # TODO: check that @type is valid
            post[subElem.get('type')] = subElem.text

    return post


def prepare_headers(doc):
    '''
    Given a :class:`Document`, prepare the "headers" portion of this module's output.

    :param doc: The :class:`Document` from which to extract MEI header data.
    :type doc: :class:`lychee.document.Document`
    :returns: A dictionary with relevant header data.
    :rtype: dict

    This function returns the "headers" dictionary described at the top of :mod:`document_outbound`.
    '''
    # TODO: tests

    fileDesc = {}

    titleStmt = {}
    for elem in doc.get_from_head('title'):
        if mei.TITLE == elem.tag:
            titleStmt[elem.get('type')] = elem.text
        else:
            lychee.log('Unexpected element found in <titleStmt>: {}'.format(elem.tag), level='warning')
    fileDesc['titleStmt'] = titleStmt

    respStmt = []
    respStmtElem = doc.get_from_head('respStmt')
    if respStmtElem is not None:
        for elem in respStmtElem:
            if mei.NAME == elem:
                # TODO: this may be insufficient in the long term
                respStmt.append({'full': elem.text})
            elif mei.PERS_NAME == elem:
                respStmt.append(format_person(elem))
            else:
                lychee.log('Unexpected element found in <respStmt>: {}'.format(elem.tag), level='warning')
        fileDesc['respStmt'] = respStmt

    roles = ('arranger', 'author', 'composer', 'editor', 'funder', 'librettist', 'lyricist', 'sponsor')
    for role in roles:
        result = format_person(doc.get_from_head('sponsor'))
        if result is not None:
            fileDesc[role] = result

    pubStmt = {'unpub': 'This is an unpublished Lychee-MEI document.'}
    fileDesc['pubStmt'] = pubStmt

    return {'fileDesc': fileDesc}
