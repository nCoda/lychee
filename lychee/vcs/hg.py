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
Mercurial integration module for Lychee.
'''

'''
from mercurial import ui, hg, commands as cmds
myui = ui.ui()
repo = hg.repository(myui, '.')

cmds.commit(myui, repo, message='')
'''

from os import path
import time

from mercurial import error, ui, hg, commands

from lychee.signals import vcs


_MYUI = None
_REPO = None
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
    If necessary, initialize a repository in the "repodir" directory.
    '''
    global _MYUI
    global _REPO
    if _MYUI is None:
        _MYUI = ui.ui()

    repodir = path.abspath(repodir)

    try:
        _REPO = hg.repository(_MYUI, repodir)
    except error.RepoError:
        commands.init(_MYUI, repodir)
        _REPO = hg.repository(_MYUI, repodir)


def add(pathnames, **kwargs):
    '''
    Given a list of pathnames, ensure they are all tracked in the repository.
    '''
    global _MYUI
    global _REPO

    # these paths are assumed to be in the repository directory, which our "pathnames" may not be
    unknown = _REPO.status(unknown=True).unknown

    for each_path in pathnames:
        if path.split(each_path)[1] in unknown:
            commands.add(_MYUI, _REPO, path.abspath(each_path))


def commit(message=None, **kwargs):
    '''
    Make a new commit, optionally with the supplied commit message.

    :param message: A commit message to use.
    :type message: str

    If no commit message is supplied, a default is used.
    '''
    global _MYUI
    global _REPO

    # don't try to commit if nothing has changed
    stat = _REPO.status()
    if 0 == (len(stat.added) + len(stat.deleted) + len(stat.modified) + len(stat.removed)):
        return

    if message is None:
        message = 'Lychee autocommit {}'.format(time.time())

    commands.commit(_MYUI, _REPO, message=message)


_SIGNALS = [
    # signal on the left will be connected to function on the right
    (vcs.INIT, init_repo),
    (vcs.ADD, add),
    (vcs.COMMIT, commit),
]
