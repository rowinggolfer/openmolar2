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


import socket
import pickle
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
            user = ProxyUser()
        self.set_user(user)

        #socket.setdefaulttimeout(5.0)

    def __repr__(self):
        return "%s"% self.name

    def set_user(self, user):
        assert type(user) == ProxyUser, \
            "user must be of type ProxyUser"
        self.user = user
        self._server = None

    def connect(self):
        '''
        attempt to connect to xmlrpc_server, and return this object
        raise a ConnectionError if no success.
        '''
        if self.user.has_expired:
            LOGGER.warning("ProxyUser has expired - using default ProxyUser")
            self.user = ProxyUser()

        location = 'https://%s:%s@%s:%d'% (
                    self.user.name, 
                    self.user.psword,
                    self.connection230_data.host, 
                    self.connection230_data.port
                    )

        LOGGER.debug("attempting connection to %s"%
            location.replace(self.user.psword, "********"))

        self._is_connecting = True
        try:
            _server = xmlrpclib.ServerProxy(location)
            LOGGER.debug("server proxy created.. will attempt ping")
            _server.ping()
            LOGGER.debug("connected and pingable (this is very good!)")
            self._server = _server
        except xmlrpclib.ProtocolError:
            self._is_connecting = False
            message = u"%s '%s'"% (_("connection refused for user"),
                self.user.name)
            LOGGER.error(message)
            raise self.ConnectionError(message)

        except socket.error as e:
            LOGGER.exception("unable to connect")
            self._is_connecting = False
            raise self.ConnectionError(
            'Is the host %s running and accepting connections on port %d?'% (
            self.connection230_data.host, self.connection230_data.port))

        self._is_connecting = False

    @property
    def server(self):
        '''
        a bridge to remote functions on the XMLRPC server
        '''
        if self.is_connecting:
            LOGGER.debug("awaiting connection")
        if self._server is None:
            try:
                self.connect()
            except self.ConnectionError:
                LOGGER.exception
                self._server = None
        return self._server

    @property
    def is_connected(self):
        '''
        A boolean value stating whether the client is connected
        (to a proxy server)
        '''
        return self._server is not None

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

    @property
    def html(self):
        '''
        poll the openmolar xml_rpc server for messages
        '''
        if self._server is not None:
            try:
                payload = pickle.loads(self.server.admin_welcome())
                if not payload.permission:
                    raise self.PermissionError
                message = payload.payload
            except xmlrpclib.Fault:
                LOGGER.exception("error getting proxy message")
                message = '''<h1>Unexpected server error!</h1>
                please check the log and report a bug.'''
            except Exception:
                return "unknown error in proxy_message"
        else:
            message = '''<h1>No connection</h1>%s<br />
            <a href='Retry_230_connection'>%s</a>'''% (
            self.connection230_data, _("Try Again"))
        return message

def _test():
    import gettext
    gettext.install("openmolar")

    conn_data = Connection230Data()
    conn_data.default_connection()

    pc = ProxyClient(conn_data)
    
    if pc.server is not None:
        print pc.server.system.listMethods()

        LOGGER.debug("getting last backup")
        payload = pickle.loads(pc.server.last_backup())
        LOGGER.debug("received payload %s"% payload)
        if payload.payload:
            LOGGER.debug("last backup %s"% payload.payload)
        else:
            LOGGER.error(payload.error_message)
            
    else:
        LOGGER.error("unable to connect")

    LOGGER.debug(pc.html)

if __name__ == "__main__":

    import logging
    logging.basicConfig(level = logging.DEBUG)
    LOGGER = logging.getLogger("test")
    
    _test()
