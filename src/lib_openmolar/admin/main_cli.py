#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010, Neil Wallace <rowinggolfer@googlemail.com>               ##
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

import ConfigParser
from lib_openmolar.admin.db_tools.proxy_manager import ProxyManager
from lib_openmolar.common.connect import ProxyUser

class AdminMain(ProxyManager):
    '''
    This class is the core commandline application.
    '''
    log = LOGGER
    def __init__(self, filepath):
        LOGGER.debug("Using admin command line interface!")

        self.parser = ConfigParser.SafeConfigParser()
        self.parser.readfp(open(filepath))

        ProxyManager.__init__(self)

        self.actions()

    def set_user(self):
        '''
        set the user specified in the script (if any!)
        '''
        if self.parser.has_section("user"):
            name = self.parser.get("user","name")
            psword = self.parser.get("user", "password")
            AD_SETTINGS.proxy_user = ProxyUser(name, psword)

            #force reload of server at next use
            self._proxy_server = None
            return True
        return False

    def switch_server_user(self):
        '''
        a custom override of :doc:`ProxyManager` function
        '''
        LOGGER.debug("switching server user")
        return self.set_user()

    def actions(self):
        actions = self.parser.items('actions')
        LOGGER.debug("script file has actions %s"% actions)
        for action, param in actions:
            if action == "drop_db":
                LOGGER.info(
                "script calling for '%s' on database '%s'"% (action, param))
                if self.drop_db(param):
                    LOGGER.info("successfully dropped %s"% param)
                else:
                    LOGGER.error("drop FAILED")
            elif action == "create_database":
                LOGGER.info(
                "script calling for '%s' on database '%s'"% (action, param))
                if self.create_database(param):
                    LOGGER.info("successfully created %s"% param)
                else:
                    LOGGER.error("creation FAILED")
            else:
                LOGGER.warning("unknown action '%s' specified"% action)

def main(filepath):
    admin = AdminMain(filepath)
    admin.init_proxy()

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")
    sys.exit(main())
