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
    a custom Exception - becomes a property of Proxyclient
    '''
    pass

class _PermissionError(Exception):
    '''
    A custom exception raised when user privileges are insufficient
    becomes a property of Proxyclient
    '''
    pass


class ProxyClient(object):
    '''
    This class provides functionality for communicating with the 230 server.
    (the openmolar xmlrpc server)
    '''
    _server = None

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

        if user is None:
            user = ProxyUser()

        assert (type(user) == ProxyUser and type(connection230_data)
        == Connection230Data), "incorrect connection params supplied"

        self.connection230_data = connection230_data
        self.user = user #AD_SETTINGS.proxy_user

        LOGGER.debug("attempting to connect to the openmolar_server....")
        if self.server is not None:
            LOGGER.info("connected to the openmolar_server")
        else:
            LOGGER.error("not connected")

    def connect(self):
        '''
        attempt to connect to xmlrpc_server, and return this object
        raise a ConnectionError if no success.
        '''
        if self.user.has_expired:
            LOGGER.warning("ProxyUser has expired - using default ProxyUser")
            self.user = ProxyUser()

        location = 'https://%s:%s@%s:%d'% (self.user.name, self.user.psword,
        self.connection230_data.host, self.connection230_data.port)

        LOGGER.debug("attempting connection to %s"%
            location.replace(self.user.psword, "********"))
        try:
            _server = xmlrpclib.ServerProxy(location)
            LOGGER.debug("connected (this is good!)")
            _server.ping()
            LOGGER.debug("connected and pingable (this is very good!)")
            self._server = _server
        except xmlrpclib.ProtocolError:
            message = u"%s '%s'"% (_("connection refused for user"),
                self.user.name)
            LOGGER.error(message)
            raise self.ConnectionError(message)

        except socket.error as e:
            LOGGER.error(
            "error connecting to the openmolar-xmlrpc server %s"% location)

            #raise self.ConnectionError(
            #'Is the host %s running and accepting connections on port %d?'% (
            #self.connection230_data.host, self.connection230_data.port))

    @property
    def server(self):
        '''
        a bridge to remote functions on the XMLRPC server
        '''
        if self._server is None:
            self.connect()

        return self._server

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
            message = "<h1>No connection</h1>%s"% self.connection230_data
        return message

def _test():
    import logging
    logging.basicConfig(level = logging.DEBUG)
    import __builtin__
    __builtin__.__dict__["LOGGER"] = logging.getLogger()
    import gettext
    gettext.install("openmolar")

    conn_data = Connection230Data()
    conn_data.default_connection()

    pc = ProxyClient(conn_data)
    pc.connect()

    if pc.server is not None:
        print pc.server.system.listMethods()

        LOGGER.debug("getting last backup")
        payload = pickle.loads(pc.server.last_backup())
        LOGGER.debug("received payload %s"% payload)
        if payload.payload:
            LOGGER.debug("last backup %s"% payload.payload)
        else:
            LOGGER.error(payload.error_message)

    LOGGER.debug(pc.name)
    LOGGER.debug(pc.html)

if __name__ == "__main__":
    _test()
