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
Mercurial integration module for *Lychee*.
'''


from os import path
import time

import hug

import lychee
from lychee.signals import vcs


_HUG = None  # created by init_repo()
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


def init_repo(repodir, **kwargs):
    '''
    Initialize a repository in the "repodir" directory.
    '''
    global _HUG
    _HUG = hug.Hug(repodir, safe=True)


def add(pathnames, **kwargs):
    '''
    Given a list of pathnames, ensure they are all tracked in the repository.
    '''
    global _HUG
    _HUG.add(pathnames)


def commit(message=None, **kwargs):
    '''
    Make a new commit, optionally with the supplied commit message.

    :param message: A commit message to use.
    :type message: str

    If no commit message is supplied, a default is used.
    '''
    global _HUG

    if message is None:
        message = 'Lychee autocommit {}'.format(time.time())

    try:
        _HUG.commit(message)
    except RuntimeError:
        lychee.log('No files changed; commit aborted.', level='info')


_SIGNALS = [
    # signal on the left will be connected to function on the right
    (vcs.INIT, init_repo),
    (vcs.ADD, add),
    (vcs.COMMIT, commit),
]
