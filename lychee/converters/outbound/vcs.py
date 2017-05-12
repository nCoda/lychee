#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/converters/vcs_outbound.py
# Purpose:                "Converts" VCS data into an easier format for clients.
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
"Converts" VCS data into an easier format for clients.

.. warning::
    This module is intended for internal *Lychee* use only, so the API may change without notice.
    If you wish to use this module outside *Lychee*, please contact us to discuss the best way.

.. tip::
    We recommend that you use the converters indirectly.
    Refer to :ref:`how-to-use-converters` for more information.

.. note:: This is an outbound converter that does not emit signals directly. Refer to the
    :mod:`lychee.signals.outbound` module for more information.

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
                'number': '0',
            },
            '41962ee9069382d1fbbba5251ee0b5de99b18df6': {
                'hash': '41962ee9069382d1fbbba5251ee0b5de99b18df6',
                'user': 'Danceathon Smith <danceathon@example.com>',
                'date': 1424894400.0,
                'files': ['270842928'],
                'description': 'Add section C1',
                'number': '1',
            },
        }
    }

'''

import datetime

# from mercurial import error, ui, hg

import lychee
from lychee.signals import outbound


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


def convert(repo_dir, **kwargs):
    '''
    Prepare VCS data in a useful format for clients.

    :param str repo_dir: The absolute pathname to the repository for which to produce data.
    :raises: :exc:`lychee.exceptions.OutboundConversionError` when there is a forseeable error.
    '''
    return convert_helper(repo_dir)


def convert_helper(repo_dir):
    # TODO: migrate this functionality to the "mercurial-hug" library
    '''
    Do the actual work for :func:`convert`. This helper function exists so that the
    :mod:`document_outbound` converter can call this converter without having to emit the
    :const:`CONVERSION_FINISH` signal.

    :param str repo_dir: Absolute pathname to the Mercurial repository's directory.
    :returns: Information from the Version Control System in the format described above.
    :rtype: dict

    .. note::
        If the repository fails to initialize for any reason, this function returns an empty
        dictionary rather than raising an exception.
    '''
    myui = ui.ui()
    try:
        repo = hg.repository(myui, repo_dir)
    except error.RepoError:
        return {}

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
            'number': cset.rev(),
        }

    return post
