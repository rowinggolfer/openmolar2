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

import logging
import os
import sys
import ConfigParser

logging.basicConfig(level=logging.INFO)

DESCRIPTION = 'Dental Practice Management Software'
AUTHOR = 'Neil Wallace'
EMAIL = 'rowinggolfer@googlemail.com'
URL = 'http://www.openmolar.com'
LICENSE = 'GPL v3'

MAINCONF = "setup.cnf"
PARTCONF = "setup_part.cnf"

# keep a note of any setup created files which are to be removed
# I don't want any files own by root left behind.
cleanup_files = []

try:
    from configure import OMConfig
    CONF = MAINCONF
    if not os.path.isfile(CONF):
        logging.debug('%s not found..'% CONF)
        print ('please run python configure.py')
        sys.exit(1)

    ALL_PACKAGES_AVAILABLE = True
except ImportError:
    # this file works if included in an sdist package.
    # however it will only install one component
    logging.debug("partial setup mode")
    CONF = PARTCONF
    ALL_PACKAGES_AVAILABLE = False

config = ConfigParser.RawConfigParser()
config.read(CONF)

INSTALL_NAMESPACE = (config.has_section("namespace") and
                config.getboolean("namespace", "include"))

INSTALL_COMMON = (config.has_section("common") and
                config.getboolean("common", "include"))

INSTALL_ADMIN = (config.has_section("admin") and
                config.getboolean("admin", "include"))

INSTALL_CLIENT = (config.has_section("client") and
                config.getboolean("client", "include"))

INSTALL_SERVER = (config.has_section("server") and
                config.getboolean("server", "include"))

INSTALL_LANG = (config.has_section("lang") and
                config.getboolean("lang", "include"))

if INSTALL_SERVER and "win" in sys.platform and "install" in sys.argv:
    logging.error("Server package cannot be installed on windows")
    INSTALL_SERVER = False


if ALL_PACKAGES_AVAILABLE:
    logging.info("including the following packages (as per setup.cnf file)")
    for include, name in (
        (INSTALL_NAMESPACE, "namespace"),
        (INSTALL_COMMON, "common modules"),
        (INSTALL_COMMON, "client application"),
        (INSTALL_COMMON, "admin application"),
        (INSTALL_COMMON, "server daemon"),
        (INSTALL_COMMON, "language pack")):
        if include:
            logging.info ("package - %s"% name)

    if INSTALL_SERVER:
        from lib_openmolar.admin.db_tools.schema_manager import SchemaManager

        schema_path = "misc/server/blank_schema.sql"
        s_manager = SchemaManager()
        if not s_manager.match(schema_path):
            s_manager.write(schema_path)
            cleanup_files.append(schema_path)

def write_manifest_in(files=[]):
    f = open("MANIFEST.in", "w")
    f.write("include setup_part.cnf\n")
    for file_ in files:
        f.write("include %s\n"% file_)
    f.close()

def get_version(name):
    '''
    returns a string with in the format X.Y.Z+hg03d
    '''
    major_version = config.get(name, "version")
    try:
        return "%s+hg%03d"% ( major_version,
            config.getint(name, "revision_number"))
    except ConfigParser.NoSectionError:
        logging.warning("no hg version")
    except ConfigParser.NoOptionError:
        logging.warning("no hg version")
    return major_version

###############################################################################
##                        "namespace" setup starts                              ##
###############################################################################

if INSTALL_NAMESPACE:
    logging.info("running namespace setup")
    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")

    if ALL_PACKAGES_AVAILABLE:
        new_config = OMConfig()
        new_config.set("namespace", "include", True)
        f = open(PARTCONF, "w")
        new_config.write(f)
        f.close()

        write_manifest_in([])

    setup(
        name = 'openmolar-namespace',
        version = get_version("namespace"),
        description = DESCRIPTION + ' - namespace',
        author = AUTHOR,
        author_email = EMAIL,
        url = URL,
        license = LICENSE,
        package_dir = {'lib_openmolar' : 'src/lib_openmolar'},
        packages = ['lib_openmolar'],
        )

###############################################################################
##                        "common" setup starts                              ##
###############################################################################

if INSTALL_COMMON:
    logging.info("running common setup")
    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")

    if ALL_PACKAGES_AVAILABLE:
        new_config = OMConfig()
        new_config.set("common", "include", True)
        f = open(PARTCONF, "w")
        new_config.write(f)
        f.close()

        write_manifest_in(["src/main.py"])

    setup(
        name = 'openmolar-common',
        version = get_version("common"),
        description = DESCRIPTION + ' - common library',
        author = AUTHOR,
        author_email = EMAIL,
        url = URL,
        license = LICENSE,
        package_dir = {'lib_openmolar' : 'src/lib_openmolar'},
        packages = ['lib_openmolar.common',
                    'lib_openmolar.common.db_orm',
                    'lib_openmolar.common.connect',
                    'lib_openmolar.common.datatypes',
                    'lib_openmolar.common.import_export',
                    'lib_openmolar.common.qt4',
                    'lib_openmolar.common.qt4.dialogs',
                    'lib_openmolar.common.qt4.postgres',
                    'lib_openmolar.common.qt4.printing',
                    'lib_openmolar.common.qt4.widgets',
                    'lib_openmolar.common.qt4.plugin_tools',
                    ],
        )

###############################################################################
##                        "admin" setup starts                               ##
###############################################################################

if INSTALL_ADMIN:
    logging.info("running admin setup")

    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")

    if ALL_PACKAGES_AVAILABLE:
        new_config = OMConfig()
        new_config.set("admin", "include", True)
        f = open(PARTCONF, "w")
        new_config.write(f)
        f.close()

        write_manifest_in(["misc/admin/*", "man/admin/*", "src/admin.py"])

    setup(
        name = 'openmolar-admin',
        version = get_version("admin"),
        description = DESCRIPTION + ' - admin library and application',
        author = AUTHOR,
        author_email = EMAIL,
        url = URL,
        license = LICENSE,
        package_dir = {'lib_openmolar' : 'src/lib_openmolar'},
        packages = ['lib_openmolar.admin',
                    'lib_openmolar.admin.data_import',
                    'lib_openmolar.admin.db_orm',
                    'lib_openmolar.admin.db_tools',
                    'lib_openmolar.admin.qt4',
                    'lib_openmolar.admin.qt4.classes',
                    'lib_openmolar.admin.qt4.dialogs',
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

if INSTALL_CLIENT:
    logging.info("running client setup")
    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")

    if ALL_PACKAGES_AVAILABLE:
        new_config = OMConfig()
        new_config.set("client", "include", True)
        f = open(PARTCONF, "w")
        new_config.write(f)
        f.close()

        write_manifest_in(["misc/client/*", "man/client/*", "src/client.py"])

    setup(
        name = 'openmolar-client',
        version = get_version("client"),
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
            'lib_openmolar.client.qt4',
            'lib_openmolar.client.qt4.widgets',
            'lib_openmolar.client.qt4.widgets.chart_editor',
            'lib_openmolar.client.qt4.widgets.chart_widgets',
            'lib_openmolar.client.qt4.widgets.procedures',
            'lib_openmolar.client.qt4.dialogs',
            'lib_openmolar.client.qt4.dialogs.address_dialogs',
            'lib_openmolar.client.qt4.dialogs.address_dialogs.components',
            'lib_openmolar.client.qt4.interfaces',
            'lib_openmolar.client.qt4.pages',
                    ],
        data_files = [
                        ('/usr/share/icons/hicolor/scalable/apps',
                            ['misc/client/openmolar2.svg']),

                        ('/usr/share/applications',
                            ['misc/client/openmolar2.desktop'])
                     ],
        scripts = ['misc/client/openmolar-client'],
        )


###############################################################################
##                        "server" setup starts                              ##
###############################################################################

if INSTALL_SERVER:
    logging.info("running server setup")
    if os.path.isfile("MANIFEST"):
        os.unlink("MANIFEST")

    if ALL_PACKAGES_AVAILABLE:
        new_config = OMConfig()
        new_config.set("server", "include", True)
        f = open(PARTCONF, "w")
        new_config.write(f)
        f.close()

        write_manifest_in([
                "misc/server/*",
                "man/server/*",
                "src/server.py",
                "src/shell_scripts/*"
                ])

    setup(
        name = 'openmolar-server',
        version = get_version("server"),
        description = DESCRIPTION + \
            ' - the xml_rpc server component of openmolar2',
        author = AUTHOR,
        author_email = EMAIL,
        url = URL,
        license = LICENSE,
        package_dir = {'lib_openmolar' : 'src/lib_openmolar'},
        packages = ['lib_openmolar.server',
                    'lib_openmolar.server.functions'],
        scripts = ['misc/server/openmolar-server',
                   'misc/server/openmolar-init-master-db',
                   'misc/server/openmolar-init-master-user',
                   'misc/server/openmolar-fuzzymatch',],
        data_files=[
                    ('/etc/init.d', ['misc/server/openmolar']),
                    ('/usr/share/openmolar/',
                        ['misc/server/master_schema.sql',
                         'misc/server/blank_schema.sql',
                         'misc/server/permissions.sql']),
                    ('/etc/openmolar/',
                        ['misc/server/privatekey.pem',
                         'misc/server/cert.pem']),
                   ],
        )


###############################################################################
##                        "lang" setup starts                                ##
###############################################################################

if INSTALL_LANG:
    logging.info("running lang setup")

    logging.error( "language pack not yet available")
    if ALL_PACKAGES_AVAILABLE:
        new_config = OMConfig()
        new_config.set("lang", "include", True)
        f = open(PARTCONF, "w")
        new_config.write(f)
        f.close()

        write_manifest_in()

###############################################################################
# and finally.. if we've got this far.. remove any unwanted cruft             #
###############################################################################

logging.info("cleaning up any temporary files")
if ALL_PACKAGES_AVAILABLE:
    cleanup_files.append(PARTCONF)
    cleanup_files.append("MANIFEST.in")
cleanup_files.append("MANIFEST")

for file_ in cleanup_files:
    try:
        if os.path.isfile(file_):
            os.remove(file_)
    except OSError:
        logging.exception("Unable to remove %s"% file_)

logging.info("ALL DONE!")
sys.exit(0)
