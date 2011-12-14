#! /usr/bin/env python
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

import os
import shutil
import sys

from xml.dom import minidom

CONFDIR = os.path.join(os.path.expanduser("~"),".openmolar")
SAFEDIR = "/etc/openmolar"

CONF_FILES = []
CONF_FILES.append(os.path.join(SAFEDIR, "admin.conf"))
CONF_FILES.append(os.path.join(CONFDIR, "admin.conf"))

DEFAULT_XML = '''<?xml version="1.0" ?>
<settings>
    <version>1.0</version>
    <server name="localhost" location="localhost" port="230" />
</settings>
'''

class SettingsError(Exception):
    '''
    A custom exception
    '''
    pass

class AdminSettings(object):
    '''
    A class installed into the global namespace as AD_SETTINGS.
    '''
    _dom = None

    chosen_server=0
    '''
    if multiple servers are found in the config, this variable can be used to
    choose between them
    '''
    def __init__(self):
        pass

    @property
    def dom(self):
        if self._dom is None:
            for filepath in CONF_FILES:
                try:
                    self._dom = minidom.parse(filepath)
                    LOGGER.debug("using %s as adminconfig"% filepath)
                    continue
                except IOError:
                    try:
                        try:
                            os.makedirs(os.path.dirname(filepath))
                        except OSError:
                            pass
                        f = open(filepath, "w")
                        f.write(DEFAULT_XML)
                        f.close()
                    except IOError:
                        LOGGER.debug("unable to save adminconfig to %s"%
                            filepath)

            if self._dom is None:
                LOGGER.debug("falling back to default xml for admin config")
                self._dom = minidom.parseString(DEFAULT_XML)

        return self._dom

    @property
    def has_multiple_servers(self):
        '''
        returns true if the config file specifies more than one server
        a normal practice probably won't.
        '''
        return len(self._server_nodes) > 1

    @property
    def _server_nodes(self):
        return self.dom.getElementsByTagName("server")

    @property
    def _server_node(self):
        return self._server_nodes[self.chosen_server]

    @property
    def server_location(self):
        '''
        the server location specified in the config.
        '''
        if self.has_multiple_servers:
            self.log.warning("multiple servers found in admin config")
        return self._server_node.getAttributeNode("location").value

    @property
    def server_port(self):
        '''
        the port specified in the config
        '''
        return int(self._server_node.getAttributeNode("port").value)

def install():
    '''
    make an instance of this object acessible in the global namespace
    >>>
    '''
    import __builtin__
    __builtin__.__dict__["AD_SETTINGS"] = AdminSettings()

if __name__ == "__main__":
    import logging
    LOGGER = logging.getLogger("openmolar-admin")
    install()
