#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/vcs_outbound.py
# Purpose:                "Converts" VCS data into an easier format for clients.
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
"Converts" VCS data into an easier format for clients.

Here is a sample of the data outputted from this module.

::

    {
        # "history" is the order of changelogs leading to the current tip
        'history': ['529003fcbb3d8394f324bbd6ccb5586101864cbb', '41962ee9069382d1fbbba5251ee0b5de99b18df6'],
        # "users" is a dict where keys are the users responsible for a changelog leading to the current
        #    tip, and values are a list of their changesets
        'users': {
            'Fortitude Johnson <strong_john@example.com>': ['529003fcbb3d8394f324bbd6ccb5586101864cbb'],
            'Danceathon Smith <danceathon@example.com>': ['41962ee9069382d1fbbba5251ee0b5de99b18df6'],
        },
        # "changesets" is a dict of dicts with information about changesets
        'changesets': {
            '529003fcbb3d8394f324bbd6ccb5586101864cbb': {
                'hash': '529003fcbb3d8394f324bbd6ccb5586101864cbb',
                'user': 'Fortitude Johnson <strong_john@example.com>',
                # "date" as a Unix timestamp in UTC...
                # ... multiply by 1000 for JavaScript's Date.setTime()
                'date': 1424721600.0,
                # list of "score" and/or @xml:id of affected <section> elements
                'files': ['score'],
                'description': 'Add "section_B.mei" to all_files and score',
            },
            '41962ee9069382d1fbbba5251ee0b5de99b18df6': {
                'hash': '41962ee9069382d1fbbba5251ee0b5de99b18df6',
                'user': 'Danceathon Smith <danceathon@example.com>',
                'date': 1424894400.0,
                'files': ['270842928'],
                'description': 'Add section C1',
            },
        }
    }

'''

import datetime

from mercurial import ui, hg

import lychee
from lychee.signals import outbound


REPODIR = 'testrepo'


def prep_files(files):
    '''
    Given the list of files modified, prepare the output for Julius.

    This removes the ".mei" extension for everything except "all_files.mei," which is not returned.
    '''
    post = []
    for path in files:
        if 'all_files.mei' == path:
            continue
        else:
            post.append(path.replace('.mei', ''))

    return post


def convert(document, **kwargs):
    '''
    Prepare VCS data in a useful format for clients.

    :param document: Ignored.
    :returns: Information from the Version Control System in the format described above.
    :rtype: dict
    '''
    outbound.CONVERSION_STARTED.emit()
    lychee.log('{}.convert()'.format(__name__))

    myui = ui.ui()
    repo = hg.repository(myui, REPODIR)

    post = {'history': [], 'users': {}, 'changesets': {}}

    for i in repo:
        # get this changeset
        cset = repo[i]

        # get its ID as hexadecimal string
        cset_id = cset.hex()

        # append the ID to the list of changeset order
        post['history'].append(cset_id)

        # add the ID to the author's list of changesets
        if cset.user() in post['users']:
            post['users'][cset.user()].append(cset_id)
        else:
            post['users'][cset.user()] = [cset_id]

        # add changeset details
        post['changesets'][cset_id] = {
            'hash': cset.hex(),
            'user': cset.user(),
            'date': cset.date()[0],
            'files': prep_files(cset.files()),
            'description': cset.description(),
        }

    outbound.CONVERSION_FINISH.emit(converted=post)
    lychee.log('{}.convert() after finish signal'.format(__name__))
