#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           Lychee
# Program Description:    MEI document manager for formalized document control
#
# Filename:               lychee/vcs/__init__.py
# Purpose:                Initialize the "vcs" module.
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
Initialize the :mod:`vcs` module.
'''

from os import path
import subprocess
import time

import lychee
from lychee.signals import vcs


def vcs_processor(pathnames, **kwargs):
    vcs.STARTED.emit()
    lychee.log('{}.vcs_processor(pathnames)'.format(__name__, pathnames))

    # TODO: this is going to cause problems later...
    _, pathnames[0] = path.split(pathnames[0])

    for each_file in pathnames:
        with subprocess.Popen(['hg', 'add', each_file], cwd='testrepo') as add:
            pass

    with subprocess.Popen(['hg', 'commit', '-m', '"some message {}"'.format(time.time())], cwd='testrepo') as proc:
        pass

    vcs.FINISH.emit()
    lychee.log('{}.vcs_processor() after finish signal'.format(__name__))


vcs.START.connect(vcs_processor)
