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
import sys
import ConfigParser

from lib_openmolar.server.functions.password_generator import (
    new_password, pass_hash)

ROOT_DIR = "/etc/openmolar/"
CONF_FILE = os.path.join(ROOT_DIR, "server.conf")
PASSWORD_FILE = os.path.join(ROOT_DIR, "manager_password.txt")

HEADER = '''
######################################################################
#                                                                    #
# This is the configuration file for the openmolar server.           #
#                                                                    #
# This file should be in read/write able by root only                #
#                                                                    #
######################################################################

'''

PASSWORD_HEADER = '''
######################################################################
#                                                                    #
# This file contains the password for the admin user of the          #
# openmolar-server                                                   #
# This file can be removed, as it is not read by the application,    #
# and password is checked against the hashed version in server.conf  #
#                                                                    #
# If you do remove this file.. PLEASE KEEP A NOTE OF THE PASSWORD!!  #
#                                                                    #
######################################################################
PASSWORD = '''

# alter this whenever changing the config file format
CONFIG_VERSION = "1.0"

class OMServerConfig(ConfigParser.SafeConfigParser):
    def __init__(self):
        ConfigParser.SafeConfigParser.__init__(self)
        try:
            self.readfp(open(CONF_FILE))
            self.__good_read = True
        except IOError as exc:
            self.__good_read = False
            if exc.errno == 13:
                LOGGER.warning(
        "Insufficient Permission unable to parse config file. Are You Root?")
                sys.exit("FATAL ERROR - Unable to read config file")
            elif exc.errno == 2:
                LOGGER.warning("no config file found")
            else:
                LOGGER.exception(
                "Unknown error in parsing config file.")
                raise exc

    @property
    def is_installed(self):
        '''
        see if the config file is installed.
        This is checked every server startup, and if returns False,
        re-installs stuff.. which could be devastating!
        '''
        if os.path.isfile(PASSWORD_FILE):
            LOGGER.warning("plain text password file exists")

        return self.__good_read

    @property
    def config_version(self):
        '''
        return the version of the stored conf file.
        '''
        try:
            return self.get("config", "version")
        except ConfigParser.NoSectionError as exc:
            LOGGER.info("no version found in server.conf")
            return None

    @property
    def is_current(self):
        '''
        returns a boolean stating whether the config file is up to date.
        '''
        return self.config_version == CONFIG_VERSION

    def new_config(self):
        ConfigParser.SafeConfigParser.__init__(self)

        self.add_section("config")
        self.set("config", "version", CONFIG_VERSION)

        self.add_section("postgresql")
        self.set("postgresql", "host", "localhost")
        self.set("postgresql", "port", "5432")
        self.set("postgresql", "user", "openmolar")
        self.set("postgresql", "password", new_password())

        plain, hash = pass_hash(8)
        f = open(PASSWORD_FILE, "w")
        f.write(PASSWORD_HEADER)
        f.write(plain+"\n")
        f.close()

        self.add_section("managers-md5")
        self.set("managers-md5", "admin", hash)

        self.add_section("230server")
        self.set("230server", "listen", "")
        self.set("230server", "port", "230")

        self.add_section("ssl")
        self.set("ssl", "cert", os.path.join(ROOT_DIR, "cert.pem"))
        self.set("ssl", "key", os.path.join(ROOT_DIR, "privatekey.pem"))

    def write(self, f=None):
        LOGGER.warning("writing conf file '%s'"% CONF_FILE)
        f = open(CONF_FILE, "w")
        f.write(HEADER)
        ConfigParser.SafeConfigParser.write(self, f)
        f.close()
        os.chmod(CONF_FILE, 384)

    @property
    def postgres_host(self):
        '''
        parse the conf file for the main postgresql location
        '''
        return self.get("postgresql", "host")

    @property
    def postgres_port(self):
        '''
        parse the conf file for the main postgresql password
        '''
        return self.get("postgresql", "port")

    @property
    def postgres_user(self):
        '''
        parse the conf file for the main postgresql user
        '''
        return self.get("postgresql", "user")

    @property
    def postgres_pass(self):
        '''
        parse the conf file for the main postgresql password
        '''
        return self.get("postgresql", "password")

    @property
    def etc_dir(self):
        return os.path.dirname(CONF_FILE)

    @property
    def pub_key(self):
        '''
        the location of the public key
        (for ssl connections with openmolar-server)
        '''
        return self.get("ssl", "cert")

    @property
    def private_key(self):
        '''
        the location of the private key
        (for ssl connections with openmolar-server)
        '''
        return self.get("ssl", "key")

    @property
    def location(self):
        return self.get("230server", "listen")

    @property
    def port(self):
        return self.getint("230server", "port")

    @property
    def managers(self):
        '''
        a list of user/passwords who authenticate with the server
        passwords should be md5 hashes.
        '''
        managers = []
        for manager, hash in self.items("managers-md5"):
            managers.append((manager, hash))
        return managers

    def update(self):
        '''
        move up to the lastest version
        '''
        if self.config_version is None:
            self._update_none_to_1_0()

    def _update_none_to_1_0(self):
        '''
        migrate to config file version 1_0
        '''
        existing_pass = self.get("superusers", "openmolar")
        self.new_config()
        self.set("postgresql", "password", existing_pass)
        self.write()

def _test():
    conf = OMServerConfig()
    #conf.new_config()
    #conf.write()
    LOGGER.debug("config is current? %s"% conf.is_current)
    conf.update()
    LOGGER.debug("installed = %s"% conf.is_installed)
    LOGGER.debug("managers - %s"% conf.managers)
    LOGGER.debug("postgres host %s"% conf.postgres_host)
    LOGGER.debug("postgres port %s"% conf.postgres_port)
    LOGGER.debug("postgres user %s"% conf.postgres_user)
    LOGGER.debug("postgres password %s"% ("*" * len(conf.postgres_pass)))



if __name__ == "__main__":
    import logging
    logging.basicConfig(level = logging.DEBUG)
    
    LOGGER = logging.getLogger("test")
    _test()
