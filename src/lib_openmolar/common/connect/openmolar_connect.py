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

'''
provides 2 classes.
ConnectionError - a custom python exception, raised if connection times out
OpenmolarConnection - a custom class which connects to
the openmolar xmlrpc server
'''
import socket
import xmlrpclib

import logging

class OpenmolarConnectionError(Exception):
    '''
    a custom Exception
    '''
    pass

class ProxyUser(object):
    '''
    a custom data type to hold the user details for connection to the
    openmolar-server.
    Will expire permission after 10 minutes.
    '''
    _creation_time = None

    #:
    timeout = 600

    def __init__(self, name=None, psword=None):
        if name is None and psword is None:
            name, psword = "default", "eihjfosdhvpwi"
        else:
            self._creation_time = int(time.time())
        self.name = name
        self.psword = psword

    @property
    def has_expired(self):
        '''
        privileged users get logged out after a timeout (default is 10 minutes)
        '''
        if self._creation_time is None:
            return False
        return time.time() > self._creation_time + self.timeout

class OpenmolarConnection(object):
    '''
    a class which connects to the openmolar xmlrpc server
    '''
    HOST = "127.0.0.1"
    PORT = 230

    def connect(self, host=HOST, port=PORT, user=None):
        '''
        attempt to connect to xmlrpc_server, and return this object
        raise a ConnectionError if no success.
        '''
        if user is None:
            user = ProxyUser()
        if user.has_expired:
            logging.warning("ProxyUser has expired - using default ProxyUser")
            user = ProxyUser()

        assert type(user) == ProxyUser, "incorrect connection params supplied"

        location = 'https://%s:%s@%s:%d'% (user.name, user.psword, host, port)
        logging.debug("attempting connection to %s"%
            location.replace(user.psword, "********"))
        try:
            proxy = xmlrpclib.ServerProxy(location)
            proxy.ping()
            logging.debug("connected and pingable (this is good!)")
            return proxy
        except xmlrpclib.ProtocolError:
            message = u"%s '%s'"% (_("connection refused for user"), user.name)
            logging.error(message)
            raise OpenmolarConnectionError(message)

        except socket.error as e:
            logging.exception(
            "error connecting to the openmolar-xmlrpc server %s"% location)

            raise OpenmolarConnectionError(
            'Is the host %s running and accepting connections on port %d?'% (
            host, port))


if __name__ == "__main__":
    import pickle
    from gettext import gettext as _

    logging.basicConfig(level=logging.DEBUG)

    omc = OpenmolarConnection()
    proxy = omc.connect()
    if proxy is not None:
        print proxy.system.listMethods()

        logging.debug("getting last backup")
        payload = pickle.loads(proxy.last_backup())
        logging.debug("received payload %s"% payload)
        if payload.payload:
            logging.debug("last backup %s"% payload.payload)
        else:
            logging.error(payload.error_message)

