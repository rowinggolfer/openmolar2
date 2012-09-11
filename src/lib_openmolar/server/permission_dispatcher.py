#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2012, Neil Wallace <neil@openmolar.com>                        ##
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


## if you want a method to be displayed by the admin application's
## ManageDatabaseDialog.. include the method in
## PermissionDispatcher.management_functions (below)

MANAGER_METHODS = ( 'drop_db',
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
        for method in MANAGER_METHODS:
            self.PERMISSIONS[method] = ["admin"]

    def _get_permission(self, method):
        '''
        check if current user has permission to user this method
        "root" can do anything it likes!
        other users depend on the list above.
        '''
        try:
            permission = self.user in self.PERMISSIONS[method]
        except KeyError:
            permission = True
        message = "permission for user '%s' for method '%s' - %s "% (
            self.user, method, "Granted" if permission else "Unauthorised")

        LOGGER.debug(message)
        return permission

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
            try:
                #this line executes the method!
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

    def management_functions(self):
        '''
        A list of tuples (func, description).
        Ultimately these are displayed to the user in a dialog.
        '''
        return (
            ("drop_db", _("Drop this database")),
            ("truncate_all_tables", _("Remove All Data from this database")),
            ("backup_db", _("Backup this database")),
            ("update_pt_index",
                _("Update Patient index (after import)")),
            )

    def pre_execution_warning(self, func_name):
        '''
        see if any warning needs to be confirmed before execution
        returns None if hasn't been specified here.
        '''
        warnings = {
        "drop_db" : u"%s<br /><b>%s</b>"% (
                    _("Are you sure you want to drop this database?"),
                    _("This action cannot be undone")),
        "truncate_all_tables" : u"%s<br /><b>%s</b>"% (
            _("Are you sure you want to remove All Data from this database?"),
            _("This action cannot be undone"))
                    }

        return warnings.get(func_name, None)

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
