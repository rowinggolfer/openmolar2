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
import random
import pickle
import string

from lib_openmolar.server.functions import FunctionStore
from lib_openmolar.server.misc.payload import PayLoad


LOOSE_METHODS = (   'admin_welcome',
                    'available_databases',
                    'create_db',
                    'create_demodb',
                    'create_demo_user',
                    'default_conn_atts',
                    'drop_demo_user',
                    'drop_demodb',
                    'last_backup',
                    'last_error',
                    'no_databases_message',
                    'refresh_saved_schema',
                    'truncate_demo',
                    'message_link',
                    'management_functions'
                    )

MANAGER_METHODS = ( 'create_user',
                    'drop_db',
                    'drop_user',
                    'grant_user_permissions',
                    'truncate_all_tables',
                    )

class PermissionDispatcher(FunctionStore):
    '''
    wraps all the calls and checks if the user has permissions to run 
    that method
    '''
    _user = None
    PERMISSIONS = {}

    def __init__(self):
        FunctionStore.__init__(self)
        self._init_permissions()
        
    def _init_permissions(self):
        '''
        parse the tuples above into a dictionary of lists
        '''
        for method in LOOSE_METHODS:
            self.PERMISSIONS[method] = ["admin", "default"]
        for method in MANAGER_METHODS:
            if self.PERMISSIONS.has_key(method):
                LOGGER.debug(
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
        user = self.user
        message = "permission for user '%s' for method '%s'"% (user, method)

        if (user == "root" or user in self.PERMISSIONS.get(method, [])):
            LOGGER.debug("granted %s"% message)
            return True
        else :
            LOGGER.debug("DENIED %s"% message)
            return False

    def _dispatch(self, method, params):
        '''
        overwrite the special _dispatch function which is a wrapper
        around all functions.
        returns a pickled object of type ..doc `Payload`
        '''
        
        LOGGER.debug("_dispatch called for method %s"% method)
        pl = PayLoad(method)
        pl.permission = self._get_permission(method)
        if pl.permission:
            #this line execute the method!
            try:
                pl.set_payload(getattr(self, method)(*params))
            except Exception as exc:
                pl.set_payload("openmolar server error - check the server log")
                pl.set_exception(exc)
                LOGGER.exception("exception in method %s"% method)

        LOGGER.debug("returning (pickled) %s"% pl)
        return pickle.dumps(pl)
        
    @property
    def user(self):
        return self._user        

    def _remember_user(self, user):
        '''
        remember the current user
        '''
        self._user = user

    
def _test():
    '''
    test the DispatchServer class
    '''
    pd = PermissionDispatcher()
    
if __name__ == "__main__":
    import __builtin__
    import logging
    logging.basicConfig(level=logging.DEBUG)
    __builtin__.LOGGER = logging.getLogger("openmolar_server")
    _test()
