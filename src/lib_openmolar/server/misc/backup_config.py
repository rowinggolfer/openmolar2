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

from lib_openmolar.server.misc.om_server_config import SERVER_DIR

BACKUP_FILE = os.path.join(SERVER_DIR, "backup.conf")

class BackupConfig(ConfigParser.SafeConfigParser):
    def __init__(self):
        ConfigParser.SafeConfigParser.__init__(self)
        try:
            self.readfp(open(BACKUP_FILE))
            self.__good_read = True
        except IOError as exc:
            self.__good_read = False
            if exc.errno == 2:
                LOGGER.warning("no config file found")
            else:
                LOGGER.exception(
                "Unknown error in parsing config file.")
                raise exc

    @property
    def config_version(self):
        '''
        return the version of the stored conf file.
        '''
        try:
            return self.get("config", "version")
        except ConfigParser.NoSectionError as exc:
            LOGGER.info("no version found in backup.conf")
            return None

    @property
    def backup_dir(self):
        '''
        parse the conf file for the main postgresql password
        '''
        try:
            return self.get("backup", "location")
        except ConfigParser.NoSectionError as exc:
            LOGGER.info("no backup location found in backup.conf")
            raise IOError("misconfigured or missing backup file")
        
if __name__ == "__main__":
    import logging
    logging.basicConfig(level = logging.DEBUG)
    
    LOGGER = logging.getLogger("test")
    bc = BackupConfig()
    LOGGER.info(bc.backup_dir)