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

import hashlib
import random
import pickle
import string

from db_functions import DBFunctions
from message_functions import MessageFunctions
from shell_functions import ShellFunctions
from lib_openmolar.server.misc.om_server_config import OMServerConfig

class FunctionStore(DBFunctions, ShellFunctions, MessageFunctions):
    '''
    A class whose functions will be inherited by the server.
    Inherits from many other classes as only one call of
    SimpleXMLServer.register_instance is allowed.
    '''
    _user = None

    def __init__(self):
        self.config = OMServerConfig()
        DBFunctions.__init__(self)

    @property
    def MASTER_PWORD(self):
        return self.config.postgres_pass


    def last_backup(self):
        '''
        returns a iso formatted datetime string showing when the
        last backup was made
        '''
        import datetime
        return datetime.datetime.now().isoformat()


def _test():
    '''
    test the FunctionStore class
    '''
    sf = FunctionStore()
    print (sf.admin_welcome())

    print (dir(sf))
    print (sf.message_link("random_url_text"))

    sf.backup_db("openmolar_demo")
    sf.backup_db("openmolar_demo", schema_only=True)

    print (sf.get_update_script("/home/neil/tmp/openmolar_demo/orig.sql",
                        "/home/neil/tmp/openmolar_demo/new.sql" ))

if __name__ == "__main__":
    import __builtin__
    import logging
    logging.basicConfig(level=logging.DEBUG)
    __builtin__.LOGGER = logging.getLogger("openmolar_server")
    _test()
