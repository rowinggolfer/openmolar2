#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011, Neil Wallace <rowinggolfer@googlemail.com>               ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

'''
This module is used as a "hook" for mercurial so that revision updates occur
whenever an update or commit is performed on the repo (or nested sub repo).

Major Version numbers are also placed here (and ONLY here!)

Openmolar uses standard major.minor.point versioning

the majority of the code in this module is taken from 
https://bitbucket.org/dowski/mercurial-version-info-plugin

'''

import os
import time

from mercurial import util

###############################################################################
##                                                                           ##
##          ADJUST VERSION NUMBERS HERE.                                     ##
##                                                                           ##
VERSION_NUMBER = "2.0.2"
##                                                                           ##
##          ALL DONE!!                                                       ##
##                                                                           ##
###############################################################################


TEMPLATE = '''\
VERSION = %(version)r
revision_id = %(revision_id)r
revision_number = %(revision_number)r
branch = %(branch)r
tags = %(tags)r
date = %(date)r
'''

def hook(ui, repo, node=None, **params):
    conf = _load_config(ui)
    changeset = repo[node]
    if not changeset.node():
        # this can happen when this function is called as an extension in a
        # working directory. in that case get the first parent changeset.
        changeset = changeset.parents()[0]
    versionfile = open(os.path.join(repo.root, conf['version_file_path']), 'w')
    _write_version_info(changeset, versionfile)

def _write_version_info(changeset, versionfile):
    template_vars = {
    	'version':VERSION_NUMBER,
        'revision_id':changeset.node().encode('hex'),
        'revision_number':changeset.rev(),
        'branch':changeset.branch(),
        'tags':changeset.tags(),
        'date':time.ctime(changeset.date()[0]),
    }
    versionfile.write(TEMPLATE % template_vars)

def _load_config(ui):
    conf = dict(ui.configitems('hgversioninfo'))
    if not conf:
        raise util.Abort('You need a [hgversioninfo] section in your config')
    if not conf.get('version_file_path'):
        msg = ('You need to define the version_file_path in your '
                '[hgversioninfo] config section.')
        raise util.Abort(msg)
    return conf
