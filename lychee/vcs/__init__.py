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

import lychee
from lychee.signals import vcs
from . import hg


hg.connect_signals()


def vcs_processor(pathnames, **kwargs):
    vcs.STARTED.emit()
    lychee.log('{}.vcs_processor({})'.format(__name__, pathnames))

    repodir = 'testrepo'
    message = None

    vcs.PREINIT.emit(repodir=repodir)
    vcs.INIT.emit(repodir=repodir)
    vcs.POSTINIT.emit(repodir=repodir)

    vcs.PREADD.emit(pathnames=pathnames)
    vcs.ADD.emit(pathnames=pathnames)
    vcs.POSTADD.emit(pathnames=pathnames)

    vcs.PRECOMMIT.emit(message=message)
    vcs.COMMIT.emit(message=message)
    vcs.POSTCOMMIT.emit(message=message)

    vcs.FINISH.emit()
    lychee.log('{}.vcs_processor() after finish signal'.format(__name__))


vcs.START.connect(vcs_processor)
