#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
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

import __builtin__
import os
import shutil
import sys

from lib_openmolar.common.settings import singleton, CommonSettings
from lib_openmolar.common.datatypes import Connection230Data
from lib_openmolar.common.qt4.plugin_tools.plugin_handler import PluginHandler


class SettingsError(Exception):
    '''
    A custom exception
    '''
    pass

@singleton
class AdminSettings(CommonSettings, PluginHandler):
    '''
    A class installed into the global namespace as SETTINGS.
    '''

    connection230s = []

    proxy_user = None
    '''
    the user of the proxy server, should be None to use the
    default (unprivileged) user, or an instance of :doc:`ProxyUser`
    '''

    def __init__(self):
        CommonSettings.__init__(self)

        self.VERSION
        self.load()

    @property
    def VERSION(self):
        try:
            from lib_openmolar.admin import version
            VERSION = "Admin version %s~hg%s"% (
                version.VERSION, version.revision_number)
            from lib_openmolar.common import version
            VERSION += "\nCommon version %s~hg%s"% (
                version.VERSION, version.revision_number)
        except ImportError:
            VERSION = "Unknown"
            LOGGER.exception("unable to parse for admin versioning")
        LOGGER.debug("VERSION %s"% VERSION)
        return VERSION

    def load(self):
        for root, dir_, files in os.walk(self.CONF230_DIR):
            for file_ in sorted(files):
                filepath = os.path.join(root, file_)
                conndata = Connection230Data()
                conndata.from_conf_file(filepath)
                self.connection230s.append(conndata)

        if self.connection230s == []:
            LOGGER.warning("no 230 connections found in %s"% self.CONF230_DIR)
            LOGGER.warning("defaulting to localhost")
            conndata = Connection230Data()
            conndata.default_connection()
            self.connection230s.append(conndata)

    @property
    def om_connections(self):
        '''
        A list of connections (loaded at __init__)
        '''
        return self.connection230s

    @property
    def CONF_DIR(self):
        '''
        will return the os equivalent of "/etc/openmolar/admin/connections"
        '''
        return os.path.join(self.ROOT_FOLDER, "admin", "connections")


    @property
    def CONF230_DIR(self):
        '''
        will return the os equivalent of "/etc/openmolar/admin/connections230"
        '''
        return os.path.join(self.ROOT_FOLDER, "admin", "connections230")


    @property
    def CONNECTION_CONFDIRS(self):
        '''
        directories where conf files are found.
        '''

        user_dir = os.path.join(self.LOCALFOLDER, "admin", "connections")
        root_dir = os.path.join(self.ROOT_FOLDER, "admin", "connections")

        if not os.path.isdir(user_dir):
            os.makedirs(user_dir)

        return [user_dir, root_dir]


def install():
    '''
    make an instance of this object acessible in the global namespace
    '''
    __builtin__.SETTINGS = AdminSettings()

def _test():
    import logging
    import admin_logger
    admin_logger.install()
    LOGGER.setLevel(logging.DEBUG)
    install()
    LOGGER.debug("testing %s"% __file__)
    LOGGER.debug("proxy_servers = %s "% SETTINGS.om_connections)
    LOGGER.debug(SETTINGS.CONNECTION_CONFDIRS)

if __name__ == "__main__":
    _test()
