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

from distutils.core import setup
from distutils.command.install_data import install_data

import os
import re
import shutil
import sys
import ConfigParser
import subprocess

DESCRIPTION = 'Dental Practice Management Software'
AUTHOR = 'Neil Wallace'
EMAIL = 'rowinggolfer@googlemail.com'
URL = 'http://www.openmolar.com'
LICENSE = 'GPL v3'

MAINCONF = "setup.cnf"
PARTCONF = "setup_part.cnf"

try:
    from configure import OMConfig
    CONF = MAINCONF
    if not os.path.isfile(CONF):
        sys.exit('ERROR - %s not found..'% CONF +
        'please run python configure.py')

except ImportError:
    print "partial setup detected"
    CONF = PARTCONF

if os.path.isfile("setup.lck"):
    sys.exit("ERROR - setup.py is locked.."
    " did a previous installation fail to complete?\n"
    "You must delete setup.lck to remove this warning\n"
    )

open("setup.lck", "a")

config = ConfigParser.RawConfigParser()
config.read(CONF)

def write_manifest_in(files=[]):
    f = open("MANIFEST.in", "w")
    f.write("include setup_part.cnf\n")
    for file_ in files:
        f.write("include %s\n"% file_)
    f.close()

###############################################################################
##                        "common" setup starts                              ##
###############################################################################

if config.has_section("common") and config.getboolean("common", "include"):
    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")

    if CONF == MAINCONF:
        config = OMConfig()
        config.set("common", "include", True)
        f = open(PARTCONF, "w")
        config.write(f)
        f.close()

        write_manifest_in()

    setup(
        name = 'openmolar-common',
        version = config.get("common", "version"),
        description = DESCRIPTION + ' - common library',
        author = AUTHOR,
        author_email = EMAIL,
        url = URL,
        license = LICENSE,
        package_dir = {'lib_openmolar' : 'src/lib_openmolar'},
        packages = ['lib_openmolar',
                    'lib_openmolar.common',
                    'lib_openmolar.common.classes',
                    'lib_openmolar.common.common_db_orm',
                    'lib_openmolar.common.connect',
                    'lib_openmolar.common.dialogs',
                    'lib_openmolar.common.import_export',
                    'lib_openmolar.common.widgets',
                    ],
        scripts = ['misc/openmolar2'],
        )

###############################################################################
##                        "admin" setup starts                               ##
###############################################################################

if config.has_section("admin") and config.getboolean("admin", "include"):

    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")

    if CONF == MAINCONF:
        config = OMConfig()
        config.set("admin", "include", True)
        f = open(PARTCONF, "w")
        config.write(f)
        f.close()

        write_manifest_in(["misc/admin/*"])

    setup(
        name = 'openmolar-admin',
        version = config.get("admin", "version"),
        description = DESCRIPTION + ' - admin library and application',
        author = AUTHOR,
        author_email = EMAIL,
        url = URL,
        license = LICENSE,
        package_dir = {'lib_openmolar' : 'src/lib_openmolar'},
        packages = ['lib_openmolar.admin',
                    'lib_openmolar.admin.data_import',
                    'lib_openmolar.admin.data_import.import_om1',
                    'lib_openmolar.admin.db_orm',
                    'lib_openmolar.admin.qt4gui',
                    'lib_openmolar.admin.qt4gui.classes',
                    'lib_openmolar.admin.qt4gui.dialogs',
                    ],
        data_files = [
                        ('/usr/share/icons/hicolor/scalable/apps',
                            ['misc/admin/openmolar-admin.svg']),

                        ('/usr/share/applications',
                            ['misc/admin/openmolar2-admin.desktop'])
                     ],
        scripts = ['misc/admin/openmolar-admin'],
        )


###############################################################################
##                        "client" setup starts                              ##
###############################################################################

if config.has_section("client") and config.getboolean("client", "include"):
    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")

    if CONF == MAINCONF:
        config = OMConfig()
        config.set("client", "include", True)
        f = open(PARTCONF, "w")
        config.write(f)
        f.close()

        write_manifest_in(["misc/client/*"])

    setup(
        name = 'openmolar-client',
        version = config.get("client", "version"),
        description = DESCRIPTION + ' - client library and application',
        author = AUTHOR,
        author_email = EMAIL,
        url = URL,
        license = LICENSE,
        package_dir = {'lib_openmolar' : 'src/lib_openmolar'},
        packages = [
            'lib_openmolar.client',
            'lib_openmolar.client.classes',
            'lib_openmolar.client.db_orm',
            'lib_openmolar.client.db_orm.diary',
            'lib_openmolar.client.db_orm.table_models',
            'lib_openmolar.client.qt4gui',
            'lib_openmolar.client.qt4gui.client_widgets',
            'lib_openmolar.client.qt4gui.client_widgets.chart_editor',
            'lib_openmolar.client.qt4gui.client_widgets.chart_widgets',
            'lib_openmolar.client.qt4gui.client_widgets.procedures',
            'lib_openmolar.client.qt4gui.dialogs',
            'lib_openmolar.client.qt4gui.dialogs.address_dialogs',
            'lib_openmolar.client.qt4gui.dialogs.address_dialogs.components',
            'lib_openmolar.client.qt4gui.interfaces',
            'lib_openmolar.client.qt4gui.pages',
            'lib_openmolar.client.scripts',
                    ],
        data_files = [
                        ('/usr/share/icons/hicolor/scalable/apps',
                            ['misc/client/openmolar.svg']),

                        ('/usr/share/applications',
                            ['misc/client/openmolar2.desktop'])
                     ],
        scripts = ['misc/client/openmolar-client'],
        )


###############################################################################
##                        "server" setup starts                              ##
###############################################################################

class InstallData(install_data):
    '''
    subclass install_data so that updat.rc is executed
    '''
    def run(self):
        install_data.run(self)
        print "RUNNING update-rc.d"
        p = subprocess.Popen(["update-rc.d","openmolar","defaults"])
        p.wait()

if config.has_section("server") and config.getboolean("server", "include"):
    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")

    if CONF == MAINCONF:
        config = OMConfig()
        config.set("server", "include", True)
        f = open(PARTCONF, "w")
        config.write(f)
        f.close()

        write_manifest_in(["misc/server/*"])

    setup(
        name = 'openmolar-server',
        version = config.get("server", "version"),
        description = DESCRIPTION + \
            ' - the xml_rpc server component of openmolar2',
        author = AUTHOR,
        author_email = EMAIL,
        url = URL,
        license = LICENSE,
        package_dir = {'lib_openmolar' : 'src/lib_openmolar'},
        packages = ['lib_openmolar', 'lib_openmolar.server'],
        scripts = ['misc/server/openmolar-server',
                   'misc/server/openmolar-init-master-db',
                   'misc/server/openmolar-init-master-user',
                   'misc/server/openmolar-fuzzymatch',],
        data_files=[('/etc/init.d', ['misc/server/openmolar'])],
        cmdclass = {'install_data':InstallData}
        )


###############################################################################
##                        "lang" setup starts                                ##
###############################################################################

if config.has_section("lang") and config.getboolean("lang", "include"):
    print "WARNING - setup.py is unable to install language pack at the moment"
    if CONF == MAINCONF:
        config = OMConfig()
        config.set("lang", "include", True)
        f = open(PARTCONF, "w")
        config.write(f)
        f.close()

        write_manifest_in()

if os.path.isfile("MANIFEST"):
    os.unlink("MANIFEST")

# and finally.. if we've got this far.. remove the locks

os.remove("setup.lck")

