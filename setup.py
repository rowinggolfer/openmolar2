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

if not os.path.isfile("setup.conf"):
    sys.exit("ERROR - setup.conf not found..\n"
    "please run python configure.py"
    )

if os.path.isfile("setup.lck"):
    if os.path.isfile("configure.py"):
        sys.exit("ERROR - setup.py is locked.."
        " did a previous installation fail to complete?\n"
        "This could have left setup.conf in a broken state\n"
        "You must delete setup.lck to remove this warning\n"
        "please re-run python configure.py"
        )

shutil.copy("setup.conf", "setup.lck")

config = ConfigParser.RawConfigParser()
config.read("setup.conf")        

#common setup
if config.has_section("common") and config.get("common", "include"):
    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")

    subprocess.Popen(["./configure.py","-o"]).wait()

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
        )
    
#setup admin
if config.has_section("admin") and config.get("admin", "include"):

    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")
    
    subprocess.Popen(["./configure.py","-a"]).wait()
    
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
                            ['misc/admin/bin/openmolar-admin.svg']),
            
                        ('/usr/share/applications', 
                            ['misc/admin/bin/openmolar2-admin.desktop']) 
                     ],
        scripts = ['src/openmolar2-admin'],
        )
        
    
#setup client
if config.has_section("client") and config.get("client", "include"):
    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")
    
    subprocess.Popen(["./configure.py","-c"]).wait()
    
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
                            ['misc/client/bin/openmolar.svg']),
            
                        ('/usr/share/applications', 
                            ['misc/client/bin/openmolar2.desktop']) 
                     ],
        scripts = ['src/openmolar2-client'],
        )

    
#setup command_center
if config.has_section("server") and config.get("server", "include"):
    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")
    
    subprocess.Popen(["./configure.py","-s"]).wait()

    setup(
        name = 'openmolar-server',
        version = config.get("server", "version"),
        description = DESCRIPTION + ' - the xml_rpc server component of openmolar2',
        author = AUTHOR,
        author_email = EMAIL,
        url = URL,
        license = LICENSE,
        package_dir = {'lib_openmolar' : 'src/lib_openmolar'},
        packages = ['lib_openmolar.server'],
        scripts = ['src/openmolar2-server'],
        )
    
if config.has_section("lang") and config.get("lang", "include"):
    print "WARNING - setup.py is unable to install language pack at the moment"    
    #subprocess.Popen(["./configure.py","-l"]).wait()
        
if os.path.isfile("MANIFEST"):
    os.unlink("MANIFEST")

# and finally.. if we've got this far.. remove the locks

shutil.move("setup.lck", "setup.conf")
    
