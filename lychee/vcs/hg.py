#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/vcs/hg.py
# Purpose:                Mercurial integration module for Lychee.
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
Mercurial integration module for *Lychee*. This is a wrapper for :mod:`mercurial-hug`.

.. warning::
    This module is intended for internal *Lychee* use only, so the API may change without notice.
    If you wish to use this module outside *Lychee*, please contact us to discuss the best way.

.. warning::
    This module may become deprecated, and is very likely to change.
    Refer to `T110 <https://goldman.ncodamusic.org/T110>`_ for more information.
'''


import time

from lychee.logs import VCS_LOG as log
from lychee.signals import vcs


_SIGNALS = None  # NOTE: this is defined at the end of this module


def connect_signals():
    '''
    Connect this VCS implementation module to Lychee's VCS signals.
    '''
    for signal, slot in _SIGNALS:
        signal.connect(slot)


def disconnect_signals():
    '''
    Disconnect this VCS implementation module from Lychee's VCS signals.
    '''
    for signal, slot in _SIGNALS:
        signal.disconnect(slot)


def init_repo(session, **kwargs):
    '''
    Initialize a repository in the "repodir" directory.

    This function currently does nothing.
    '''
    pass


def add(pathnames, session, **kwargs):
    '''
    Given a list of pathnames, ensure they are all tracked in the repository.
    '''
    session.hug.add(pathnames)


@log.wrap('info', 'make new Mercurial commit', 'action')
def commit(session, message=None, action=None, **kwargs):
    '''
    Make a new commit, optionally with the supplied commit message.

    :param message: A commit message to use.
    :type message: str

    If no commit message is supplied, a default is used.
    '''
    if message is None:
        message = 'Lychee autocommit {}'.format(time.time())

    try:
        session.hug.commit(message)
    except RuntimeError:
        action.failure('no files changed; commit aborted')


_SIGNALS = [
    # signal on the left will be connected to function on the right
    (vcs.INIT, init_repo),
    (vcs.ADD, add),
    (vcs.COMMIT, commit),
]
