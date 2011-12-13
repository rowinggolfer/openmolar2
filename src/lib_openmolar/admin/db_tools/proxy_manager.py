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

import re
import sys
import pickle
from xmlrpclib import Fault as ServerFault

from lib_openmolar.common.connect import (
    ProxyUser,
    OpenmolarConnection,
    OpenmolarConnectionError)

def user_perms(func):
    def userf(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionError:
            proxy_manager_instance = args[0]
            if proxy_manager_instance.switch_server_user():
                return func(*args, **kwargs)

    return userf

class PermissionError(Exception):
    '''
    A custom exception raised when user privileges are insufficient
    '''
    pass


class ProxyManager(object):
    '''
    This class is the core application.
    '''
    _proxy_server = None

    FAILURE_MESSAGE = '''
    <html><body><h1>%s</h1><a href="init_proxy">%s</a></body></html>
    '''% (_("Error connecting to the openmolar-server"),
    _("Try Again?"))

    def __init__(self):
        # not called when this class is subclassed by AdminMainWindow
        self.init_proxy()

    def wait(self, *args):
        '''
        dummy function can overwritten
        '''
        pass

    def advise(self, message, importance=None):
        '''
        advise function. normally overwritten
        '''
        if importance is None:
            AD_SETTINGS.log.debug(message)
        elif importance == 1:
            AD_SETTINGS.log.info(message)
        else:
            AD_SETTINGS.log.warning(message)

    def log(self, message):
        '''
        dummy function often overwritten
        '''
        self.advise(message, 1)

    def display_proxy_message(self):
        '''
        display the proxy message
        '''
        pass

    def init_proxy(self):
        '''
        attempt to connect to the server controller at startup
        '''
        self.advise(_("connecting..."))
        self.log("connecting to the openmolar_server")
        if self.proxy_server is not None:
            self.advise(_("Success!"))
            return True
        else:
            self.advise(_("Failure!"))
            return False

    @property
    def proxy_server(self):
        '''
        a connection to the xml_rpc server running on the server
        '''
        try:
            if self._proxy_server is None:
                self._proxy_server = OpenmolarConnection().connect(
                    AD_SETTINGS.server_location, AD_SETTINGS.server_port)
            self._proxy_server.ping()
        except OpenmolarConnectionError as ex:
            self.advise(u"%s<hr />%s"%(
            _("Unable to make a connection to the server controller"),
            ex), 2)

            self._proxy_server = None

        return self._proxy_server

    def switch_server_user(self):
        '''
        this needs to be a function to change the user of the proxy
        '''
        self.advise("we need to up your permissions for this", 1)
        return False

    @property
    def proxy_message(self):
        '''
        poll the openmolar xml_rpc server for messages
        '''
        if self.proxy_server is not None:
            try:
                payload = pickle.loads(self.proxy_server.admin_welcome())
                if not payload.permission:
                    raise PermissionError
                message = payload.payload
            except ServerFault:
                AD_SETTINGS.log.exception("error getting proxy message")
                message = '''<h1>Unexpected server error!</h1>
                please check the log and report a bug.'''
        else:
            message = self.FAILURE_MESSAGE
        return message

    @user_perms
    def create_demo_database(self):
        '''
        initiates the demo database
        '''
        continue_ = self.create_database("openmolar_demo")
        if not continue_:
            self.advise(_("failed"))
            return
        self.log("creating demo user")
        try:
            self.wait()
            self.advise("creating demo user")
            payload = pickle.loads(self.proxy_server.create_demo_user())
            self.wait(False)
            if not payload.permission:
                raise PermissionError, payload.error_message
            if payload.payload:
                self.advise(_("successfully created demo user"))
            else:
                self.advise(_("unable to create demo user"))
        except:
            message = "error creating demo_user"
            AD_SETTINGS.log.exception(message)
            self.advise(message, 2)
            continue_= False
        finally:
            self.wait(False)

        return payload.payload

    @user_perms
    def create_database(self, dbname):
        '''
        creates a new db
        '''
        success = False

        demo = dbname == "openmolar_demo"

        self.advise("%s '%s' <br />%s"%(
            _("Creating a new database"), dbname,
            _("This may take some time")))
        self.wait()

        if not demo:
            payload = pickle.loads(self.proxy_server.create_db(dbname))
        else:
            payload = pickle.loads(self.proxy_server.create_demodb())
        self.wait(False)
        if not payload.permission:
            raise PermissionError, payload.error_message

        if payload.payload:
            self.advise(_("success!"), 1)
            AD_SETTINGS.log.info("database %s created"% dbname)

        self.display_proxy_message()
        return payload.payload

    @user_perms
    def drop_db(self, dbname):
        '''
        send a message to the openmolar server to drop this database
        '''
        if dbname == "openmolar_demo":
            pickled_payload = self.proxy_server.drop_demodb()
        else:
            pickled_payload = self.proxy_server.drop_db(str(dbname))

        payload = pickle.loads(pickled_payload)
        if not payload.permission:
            raise PermissionError, payload.error_message

        if payload.payload:
            self.advise(u"%s %s"%(
                _("Sucessfully dropped database"), dbname), 1)
        else:
            self.advise(u"%s<hr />%s"%(
                _("unable to drop database"), payload.error_message), 2)

        self.display_proxy_message()

    def manage_shortcut(self, url):
        '''
        the admin browser
        (which commonly contains messages from the openmolar_server)
        is connected to this slot.
        when a url is clicked it finds it's way here for management.
        unrecognised signals are send to the user via the notification.
        '''
        if url == "init_proxy":
            AD_SETTINGS.log.debug("User shortcut - Re-try openmolar_server connection")
            self.init_proxy()
        elif url == "install_demo":
            AD_SETTINGS.log.debug("Install demo called via shortcut")
            self.create_demo_database()
        elif re.match("connect_.*", url):
            dbname = re.match("connect_(.*)", url).groups()[0]
            self.advise("connect to database %s"% dbname)
        elif re.match("manage_.*", url):
            dbname = re.match("manage_(.*)", url).groups()[0]
            self.manage_db(dbname)
        else:
            self.advise("%s<hr />%s"% (_("Shortcut not found"), url), 2)

def _test():
    pm = ProxyManager()

    AD_SETTINGS.log.debug(pm.init_proxy())
    AD_SETTINGS.log.debug(pm.proxy_server)
    #AD_SETTINGS.log.debug(pm.drop_db("openmolar_demo"))
    #AD_SETTINGS.log.debug(pm.create_demo_database())

if __name__ == "__main__":
    import lib_openmolar.admin
    import gettext
    gettext.install("openmolar")
    _test()
