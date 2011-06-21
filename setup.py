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

import os, re, shutil, sys

VERSIONS = {}

DESCRIPTION = 'Dental Practice Management Software'
AUTHOR = 'Neil Wallace'
EMAIL = 'rowinggolfer@googlemail.com'
URL = 'http://www.openmolar.com'
LICENSE = 'GPL v3'


if os.path.isfile("om_setup.lck") or os.path.isfile("manifest.lck"):
    sys.exit("ERROR - setup.py is locked.."
    " did a previous installation fail to complete?\n"
    "this could have left MANIFEST.in and om_setup.cfg in a broken state\n"
    "Please execute this command before continuing\n\n"
    "mv manifest.lck MANIFEST.in && mv om_setup.lck om_setup.cfg\n\n"
    )
shutil.copy("om_setup.cfg", "om_setup.lck")
shutil.copy("MANIFEST.in", "manifest.lck")


packages = []
config_file = open("om_setup.cfg")

for line in config_file:
    m = re.match("([^#]*)_version=(.*)", line)
    if m:
        package, version = m.groups()
        VERSIONS[package] = version
        packages.append(package)

def mod_config(keep_package):
    '''
    if multiple packages are being installed, om_setup.cfg needs to be updated
    in between each call to setup()
    '''
    if len(packages) == 1:
        return
    f = open("om_setup.lck", "r")
    data = f.read()
    f.close()
    for package in packages:
        if package != keep_package:
            data = re.sub(package, "#"+package, data)
    f = open("om_setup.cfg", "w")
    f.write(data)
    f.close()
    
def mod_manifest(additions=[]):
    '''
    add addtions to the manifest file - starts from scratch each time
    '''
    f = open("manifest.lck", "r")
    data = f.read()
    f.close()
    f = open("MANIFEST.in", "w")
    f.write(data)
    f.writelines(additions)
    f.close()
        

#common setup

if "COMMON" in packages:

    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")

    mod_config("COMMON")

    setup(
        name = 'openmolar-common',
        version = VERSIONS.get("COMMON", "UNKNOWN"),
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
if "ADMIN" in packages:

    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")
    
    mod_config("ADMIN")
    mod_manifest(["include misc/admin/bin/*",])

    setup(
        name = 'openmolar-admin',
        version = VERSIONS.get("ADMIN", "UNKNOWN"),
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
if "CLIENT" in packages:

    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")
        
    mod_config("CLIENT")
    mod_manifest(["include misc/client/bin/*",])

    setup(
        name = 'openmolar-client',
        version = VERSIONS.get("CLIENT", "UNKNOWN"),
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
            'lib_openmolar.client.qt4gui.modules',
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
        
if os.path.isfile("MANIFEST"):
    os.unlink("MANIFEST")

# and finally.. if we've got this far.. remove the locks

shutil.move("om_setup.lck", "om_setup.cfg")
shutil.move("manifest.lck", "MANIFEST.in")
    
