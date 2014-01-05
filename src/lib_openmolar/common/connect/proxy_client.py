#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
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
import pickle
import socket
import xmlrpclib

from lib_openmolar.common.datatypes import Connection230Data
from lib_openmolar.common.connect import ProxyUser

class _ConnectionError(Exception):
    '''
    a custom Exception - becomes a property of :doc:`ProxyClient`
    '''
    pass

class _PermissionError(Exception):
    '''
    A custom exception raised when user privileges are insufficient
    becomes a property of :doc:`ProxyClient`
    '''
    pass

class DuckPayload(object):
    '''
    a mock type of lib_openmolar.server.misc.payload.Payload
    '''
    permission = True
    exception = None
    payload = None
    error_message = "No connection"

class ProxyClient(object):
    '''
    This class provides functionality for communicating with the 230 server.
    (the openmolar xmlrpc server)
    '''
    _server = None
    _is_connecting = False
    #:
    PermissionError = _PermissionError

    #:
    ConnectionError = _ConnectionError

    def __init__(self, connection230_data, user=None):
        '''
        :param:host(string)
        :param:port(int)
        :param:user :doc:`ProxyUser` or None

        '''

        assert type(connection230_data) == Connection230Data, \
        "ProxyClient must be initiated with a Connection230Data object"

        self.connection230_data = connection230_data
        if user is None:
            self.use_default_user()
        else:
            self.set_user(user)

    def __repr__(self):
        return "%s"% self.name

    def set_user(self, user):
        assert type(user) == ProxyUser, \
            "user must be of type ProxyUser"
        #LOGGER.debug("setting proxyclient user to %s"% user)
        self.user = user
        self._server = None
        self._is_connecting = False

    def use_default_user(self):
        user = ProxyUser()
        self.set_user(user)

    def connect(self):
        '''
        attempt to connect to xmlrpc_server, and return this object
        raise a ConnectionError if no success.
        '''
        self._server = None
        if not self.connection230_data.is_valid:
            raise self.ConnectionError(
            "connection data is invalid - check your conf files")

        if self.user.has_expired:
            LOGGER.warning("ProxyUser has expired - using default ProxyUser")
            self.use_default_user()

        location = 'https://%s:{PASSWORD}@%s:%d'% (
                    self.user.name,
                    self.connection230_data.host,
                    self.connection230_data.port
                    )

        if not self.user.psword:
            location = location.replace(":{PASSWORD}", "")

        LOGGER.debug("attempting connection to %s"%
            location.replace("{PASSWORD}", "*"*len(self.user.psword)))

        location = location.replace("{PASSWORD}", self.user.psword)

        self._is_connecting = True
        try:
            _server = xmlrpclib.ServerProxy(location)
            socket.setdefaulttimeout(1)
            _server.ping()
            LOGGER.debug("connected to OMServer as user '%s'"% self.user.name)
            self._server = _server
        except xmlrpclib.ProtocolError:
            message = u"%s '%s'"% (_("connection refused for user"),
                self.user.name)
            LOGGER.error(message)
            raise self.ConnectionError(message)
        except socket.timeout:
            message = ('OMServer Connection Timeout - ' +
            'Is the host %s running and accepting connections on port %d?'% (
            self.connection230_data.host, self.connection230_data.port))
            LOGGER.error(message)
            raise self.ConnectionError(message)
        except socket.error as exc:
            message = "Unable to connect to '%s':'%d'? %s"% (
                self.connection230_data.host,
                self.connection230_data.port,
                exc)
            LOGGER.error(message)
            raise self.ConnectionError(message)

        finally:
            socket.setdefaulttimeout(100)
            self._is_connecting = False

    @property
    def server(self):
        '''
        a bridge to remote functions on the XMLRPC server
        '''
        if self.is_connecting:
            LOGGER.debug("awaiting connection")
        if self._server is None:
            self.connect()
        return self._server

    @property
    def is_connected(self):
        '''
        A boolean value stating whether the client is connected
        (to a proxy server)
        '''
        try:
            return (self._server is not None and self.server.ping())
        except Exception:
            self._server = None
            return False
    @property
    def is_connecting(self):
        '''
        A boolean stating whether the connection is in progress
        (happens in a thread)
        '''
        return self._is_connecting

    @property
    def brief_name(self):
        return self.connection230_data.name

    @property
    def name(self):
        return "ProxyClient for %s"% (self.connection230_data)

    @property
    def host(self):
        return self.connection230_data.host

    def get_pg_user_list(self):
        '''
        get a list of users know to the pg server
        '''
        payload = self.call("login_roles")
        return payload.payload

    def get_pg_user_perms(self, user, dbname):
        '''
        get a list of users know to the pg server
        '''
        payload = self.call("get_user_permissions", user, dbname)
        return payload.payload

    def grant_pg_user_perms(
    self, user, dbname, admin=False, client=False):
        '''
        add user to group
        '''
        payload = self.call("grant_user_permissions", user, dbname,
        admin, client)

        return payload.payload

    def get_management_functions(self):
        '''
        get a list of management functions from the omserver
        (ie server side functions performed by user openmolar
        such as drop db, truncate db etc..)
        these are passed to a dialog for user interaction.
        '''
        payload = self.call("management_functions")
        return payload.payload

    def pre_execution_warning(self, func_name):
        payload = self.call("pre_execution_warning", func_name)
        return payload.payload

    def call(self, func, *args):
        '''
        a wrapper to call server functions.
        this is useful as it automatically unpickles the payloads
        this is the equivalent of self.server.func(args)

        returns an object of type
        :doc:`PayLoad`
        (or a DuckType thereof)
        '''
        if not self.is_connected:
            duck_payload = DuckPayload()
            duck_payload.error_message = "%s '%s':'%d'?"% (
                _("Unable to connect to"),
                self.connection230_data.host,
                self.connection230_data.port)
            return duck_payload

        try:
            pickled_payload = getattr(self.server, func).__call__(*args)
            return self._unpickle(pickled_payload)
        except xmlrpclib.Fault:
            LOGGER.exception("xmlrpc error")
            return DuckPayload()

    def _unpickle(self, pickled_payload):
        '''
        XMLRPC can not pass python objects, so they are pickled by the server
        and unpickled here.
        '''
        payload = pickle.loads(pickled_payload)

        if not payload.permission:
            raise self.PermissionError
        if payload.exception:
            raise payload.exception
        return payload

    @property
    def html(self):
        '''
        poll the openmolar xml_rpc server for messages
        '''
        payload = self.call("admin_welcome")
        message = payload.payload
        if message is None:
            LOGGER.error("unable to get ProxyClient.html")
            message = '''<h1>No connection</h1>%s<br />
            <a href='Retry_230_connection'>%s</a>'''% (
            self.connection230_data, _("Try Again"))
        return message

    def message_link(self, url_text):
        '''
        poll the openmolar xml_rpc server for messages
        '''
        if self._server is not None:
            payload = self.call("message_link", url_text)
            message = payload.payload

        else:
            message = '''<h1>No connection</h1>%s<br />
            <a href='Retry_230_connection'>%s</a>'''% (
            self.connection230_data, _("Try Again"))
        return message

def _test_instance():
    conn_data = Connection230Data()
    conn_data.default_connection()

    pc = ProxyClient(conn_data)
    pc.server
    return pc

def _test():
    import gettext
    gettext.install("openmolar")

    pc = _test_instance()
    LOGGER.debug("Ping Function Test %s"% pc.server.ping())

    LOGGER.debug("getting last backup")
    payload = pc.call("last_backup")
    if payload.error_message:
        LOGGER.error(payload.error_message)
    else:
        LOGGER.debug("last backup %s"% payload.payload)

    LOGGER.debug(pc.html)
    LOGGER.debug(pc.get_management_functions())
    #LOGGER.debug(pc.call("dropdb", "openmolar_demo"))

    LOGGER.debug(pc.get_pg_user_perms("om_demo", "openmolar_demo"))


if __name__ == "__main__":
    from lib_openmolar import admin
    import logging
    logging.basicConfig(level = logging.DEBUG)
    LOGGER = logging.getLogger("test")

    _test()
