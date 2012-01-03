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

import hashlib
import logging
import random
import pickle
import string

from db_functions import DBFunctions
from message_functions import MessageFunctions
from shell_functions import ShellFunctions
from payload import PayLoad
from om_server_config import OMServerConfig

LOOSE_METHODS = (   'system.listMethods',
                    'admin_welcome',
                    #'admin_welcome_template',
                    'available_databases',
                    #'create_db',
                    'create_demodb',
                    'create_demo_user',
                    #'create_user',
                    #'current_user',
                    'default_conn_atts',
                    #'drop_db',
                    'drop_demo_user',
                    'drop_demodb',
                    #'drop_user',
                    #'grant_user_permissions',
                    #'install_fuzzymatch',
                    'last_backup',
                    'last_error',
                    #'log',
                    #'newDB_sql',
                    'no_databases_message',
                    'refresh_saved_schema',
                    #'save_schema'
                    )

MANAGER_METHODS = ( 'create_db',
                    'create_user',
                    #'current_user',
                    'drop_db',
                    'drop_user',
                    'grant_user_permissions',
                    #'install_fuzzymatch',
                    #'log',
                    #'newDB_sql',
                    )

class ServerFunctions(DBFunctions, ShellFunctions, MessageFunctions):
    '''
    A class whose functions will be inherited by the server.
    Inherits from many other classes as only one call of
    SimpleXMLServer.register_instance is allowed.
    '''
    _user = None
    log = logging.getLogger("openmolar_server")
    PERMISSIONS = {}

    def __init__(self):
        self.config = OMServerConfig()
        DBFunctions.__init__(self)
        self._init_permissions()

    @property
    def MASTER_PWORD(self):
        return self.config.openmolar_pass

    def _init_permissions(self):
        '''
        parse the tuples above into a dictionary of lists
        '''
        for method in LOOSE_METHODS:
            self.PERMISSIONS[method] = ["admin", "default"]
        for method in MANAGER_METHODS:
            if self.PERMISSIONS.has_key(method):
                self.log.debug(
                "whoops... permissions has a duplicate entry for method '%s'"%
                method)
            else:
                self.PERMISSIONS[method] = ["admin"]

    def _get_permission(self, method):
        '''
        check if current user has permission to user this method
        "root" can do anything it likes!
        other users depend on the list above.
        '''
        user = self._user
        message = "permission for user '%s' for method '%s'"% (user, method)

        if (user == "root" or user in self.PERMISSIONS.get(method, [])):
            self.log.debug("granted %s"% message)
            return True
        else :
            self.log.debug("DENIED %s"% message)
            return False

    def _dispatch(self, method, params):
        '''
        overwrite the special _dispatch function which is a wrapper
        around all functions.
        returns a pickled object of type ..doc `Payload`
        '''
        self.log.debug("_dispatch called for method %s"% method)
        pl = PayLoad(method)
        pl.permission = self._get_permission(method)
        if pl.permission:
            #this line execute the method!
            try:
                pl.set_payload(getattr(self, method)(*params))
            except Exception as exc:
                pl.set_payload("openmolar server error - check the server log")
                pl.set_exception(exc)
                self.log.exception("exception in method %s"% method)

        self.log.debug("returning (pickled) %s"% pl)
        return pickle.dumps(pl)

    def admin_welcome(self):
        '''
        the html shown on startup to the admin application
        '''
        dbs = self.available_databases()
        if dbs == []:
            message = self.no_databases_message()
        else:
            message = self.admin_welcome_template()
            db_list = ""
            for db in dbs:
                db_list += '''
                <div class="database">
                    <ul>
                        <li class="header">%s</li>
                        <li class="connect">
                            <a href='connect_%s?'>connect</a>
                        </li>
                        <li class="manage">
                            <a href='manage_%s'>manage</a>
                        </li>
                    </ul>
                </div>
                '''% (db, db, db)
            message = message.replace("{DATABASE LIST}", db_list)
        return message

    def last_backup(self):
        '''
        returns a iso formatted datetime string showing when the
        last backup was made
        '''
        import datetime
        return datetime.datetime.now().isoformat()

    def _remember_user(self, user):
        self._user = user

def _test():
    '''
    test the ShellFunctions class
    '''
    logging.basicConfig(level=logging.DEBUG)
    sf = ServerFunctions()
    sf.log.debug(sf.admin_welcome())

    print (dir(sf))

if __name__ == "__main__":
    _test()
