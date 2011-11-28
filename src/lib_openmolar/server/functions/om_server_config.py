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

import logging
import os
import sys
import ConfigParser

from lib_openmolar.server.functions.password_generator import (
    new_password, pass_hash)

CONF_FILE = "/etc/openmolar/server/openmolar.conf"

HEADER = '''
######################################################################
#                                                                    #
# This is the configuration file for the openmolar server.           #
#                                                                    #
# This file should be in read/write able by root only                #
#                                                                    #
######################################################################
'''

class OMServerConfig(ConfigParser.SafeConfigParser):
    def __init__(self):
        ConfigParser.SafeConfigParser.__init__(self)
        try:
            self.readfp(open(CONF_FILE))
            self.__good_read = True
        except IOError as exc:
            self.__good_read = False
            if exc.errno == 13:
                logging.warning(
        "Insufficient Permission unable to parse config file. Are You Root?")
                sys.exit("FATAL ERROR - Unable to read config file")
            else:
                logging.exception(
                "Unknown error in parsing config file.")
                raise exc

    @property
    def is_installed(self):
        '''
        see if the config file is installed.
        This is checked every server startup, and if returns False,
        re-installs stuff.. which could be devastating!
        '''
        if not self.__good_read:
            return False
        try:
            if self.openmolar_pass =="":
                return False
            if not os.path.isfile(self.pub_key):
                return False
            if not os.path.isfile(self.private_key):
                return False
        except ConfigParser.NoSectionError:
            return False
        return True

    def new_config(self):
        self.add_section("superusers")
        self.set("superusers", "openmolar", new_password())

        man_pass = pass_hash(8)
        for i, section in enumerate(["managers-plain", "managers"]):
            self.add_section(section)
            self.set(section, "admin", man_pass[i])

        self.add_section("server")
        self.add_section("listen", "")
        self.add_section("port", 230)

    def write(self, f=None):
        logging.warning("writing conf file '%s'"% CONF_FILE)
        f = open(CONF_FILE, "w")
        f.write(header)
        ConfigParser.SafeConfigParser.write(self, f)
        f.close()

    @property
    def openmolar_pass(self):
        return self.get("superusers", "openmolar")

    @property
    def etc_dir(self):
        os.path.dirname(CONF_FILE)

    @property
    def pub_key(self):
        '''
        the location of the public key
        (for ssl connections with openmolar-server)
        '''
        return os.path.join(self.etc_dir, "cert.pem")

    @property
    def private_key(self):
        '''
        the location of the private key
        (for ssl connections with openmolar-server)
        '''
        return os.path.join(self.etc_dir, "privatekey.pem")


def _test():
    conf = OMServerConfig()
    #conf.new_config()
    #conf.write()
    logging.debug("master pass '%s'"% conf.openmolar_pass)
    logging.debug("installed = %s"% conf.is_installed)

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    _test()
