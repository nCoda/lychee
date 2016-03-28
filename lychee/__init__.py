#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/__init__.py
# Purpose:                Initialize Lychee.
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
Initialize Lychee.
'''

import atexit
import os
import os.path
import shutil
import tempfile
import time

from mercurial import error as hg_error

import hug


__version__ = '0.0.1'
__all__ = ['converters', 'document', 'namespaces', 'signals', 'tui', 'workflow', 'vcs', 'views']

DEBUG = False


def log(message, level=None):
    '''
    Log a message according to runtime settings.

    :param str message: The message to log. Context will be prepended (time, module, etc.).
    :param str level: The level of the message in question (i.e., whether this is a "debug" or
        "warning" or "error" message). The default is "debug."

    **Side Effect**

    This method may cause a message to be printed to stdout or stderr or into a file.
    '''

    if level is None:
        level = 'debug'

    level = level.lower()

    if 'debug' == level and not DEBUG:
        return

    message = '[{time}] {name}: {message}'.format(name=__name__,
                                                  time=time.strftime('%H:%M:%S'),
                                                  message=message)

    print(message)


# many other modules will want to import :mod:`exceptions`, so it should be imported first
from lychee import exceptions


# For managing the repository directory.
_repo_dir = None
_temp_dir = False  # whether the "_repo_dir" refers to a temporary directory we created


def _clean_temp_dir():
    '''
    This function deletes a temporary directory created by this module.
    '''
    global _temp_dir
    global _repo_dir
    if _temp_dir:
        shutil.rmtree(_repo_dir)
        _repo_dir = None
        _temp_dir = False


def set_repo_dir(path):
    '''
    Change the pathname to Lychee's repository.

    :param str path: The pathname of the directory of the repository. This should either be an
        absolute path or something that will become absolute with :func:`os.path.abspath`. If this
        argument is ``''`` (an empty string) the repository will be initialized in a temporary
        directory that is automatically deleted when :mod:`lychee` is garbage collected.
    :raises: :exc:`~lychee.exceptions.RepositoryError` when ``path`` exists and contains files but
        is not a Mercurial repository, or is a repository but cannot be written to.
    :raises: :exc:`~lychee.exceptions.RepositoryError` when ``path`` does not exist and cannot be
        created.

    If ``path`` does not exist, it will be created.

    .. warning:: If the module is already using a temporary directory of its own creation, this
        directory is deleted before setting the new repository directory.
    '''
    global _temp_dir
    global _repo_dir
    _clean_temp_dir()

    if '' == path:
        atexit.register(_clean_temp_dir)
        path = tempfile.mkdtemp()
        _temp_dir = True

    else:
        path = os.path.abspath(path)

        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError:
                raise exceptions.RepositoryError('Could not create repository directory')

    try:
        hug.Hug(path, safe=True)
    except hg_error.RepoError:
        raise exceptions.RepositoryError('Could not safely initialize the repository')

    _repo_dir = path

    return _repo_dir


def get_repo_dir():
    '''
    Return the absolute pathname for the directory holding Lychee's repository.

    :returns: The repository pathname.
    :rtype: str

    .. note:: If no repository pathname has been set, this function will initialize an empty
        repository in a temporary directory and return its path.
    '''
    global _temp_dir
    global _repo_dir
    if _repo_dir:
        return _repo_dir
    else:
        return set_repo_dir('')


from lychee import *


InteractiveSession = workflow.session.InteractiveSession
