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

from db_functions import DBFunctions
from message_functions import MessageFunctions
from shell_functions import ShellFunctions

class ServerFunctions(DBFunctions, ShellFunctions, MessageFunctions):
    '''
    A class whose functions will be inherited by the server.
    Inherits from many other classes as only one call of
    SimpleXMLServer.register_instance is allowed.
    '''
    def __init__(self):
        f = open("/etc/openmolar/server/master_pword.txt", "r")
        self.MASTER_PWORD = f.readline()
        f.close()
        DBFunctions.__init__(self)

    def admin_welcome(self):
        dbs = self.available_databases()
        if dbs == []:
            message = self.no_databases_message()
        else:
            message = self.admin_welcome_template()
            db_list = ""
            for db in dbs:
                db_list += '''
                <li class='dboptions'>%s
                    <ul>
                        <li class="users">
                            <a href='users_%s'>manage users</a>
                        </li>
                        <li class="connect">
                            <a href='connect_%s?users=%s'>connect</a>
                        </li>
                        <li class="disconnect">
                            <a href='disconnect_%s'>disconnect</a>
                        </li>
                        <li class="populate">
                            <a href='populate_%s'>populate with demo data</a>
                        </li>
                        <li class="setup">
                            <a href='setup_wizard_%s'>run setup wizard</a>
                        </li>
                    </ul>
                </li>'''% (db, db, db, 'neil,om_demo', db, db, db)
            message = message.replace("{DATABASE LIST}", db_list)
        return message

    def last_backup(self):
        '''
        returns a iso formatted datetime string showing when the
        last backup was made
        '''
        import datetime
        return datetime.datetime.now().isoformat()


def _test():
    '''
    test the ShellFunctions class
    '''
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger("openmolar_server")
    sf = ServerFunctions()
    log.debug(sf.get_demo_user())
    log.debug(sf.admin_welcome())

if __name__ == "__main__":
    _test()
