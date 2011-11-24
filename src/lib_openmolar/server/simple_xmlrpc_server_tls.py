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

from hashlib import md5
import pickle
import socket
import ssl
from SocketServer import BaseServer
from SimpleXMLRPCServer import (
    SimpleXMLRPCServer,
    SimpleXMLRPCDispatcher,
    SimpleXMLRPCRequestHandler)

##############################################################################
##  create a pair with openssl http://openssl.org/                          ##
##                                                                          ##
##  ~$ openssl req -new -x509 -days 365 -nodes -out cert.pem \              ##
##                             -keyout privatekey.pem                       ##
##                                                                          ##
##############################################################################

import logging

KEYFILE  = '/etc/openmolar/server/privatekey.pem'
CERTFILE = '/etc/openmolar/server/cert.pem'

USERDICT = {"restricted":md5("eihjfosdhvpwi").hexdigest(),
            "neil":md5("eihjfosdhvpwi").hexdigest()}

class SimpleXMLRPCServerTLS(SimpleXMLRPCServer):
    '''
    an extension of SimpleXMLPRCServer
    which enforces ssl connection, and user authentication
    '''
    def __init__(self, addr):
        SimpleXMLRPCDispatcher.__init__(self)

        BaseServer.__init__(self, addr, VerifyingRequestHandler)
        self.socket = ssl.wrap_socket(
            socket.socket(self.address_family, self.socket_type),
            server_side=True,
            keyfile=KEYFILE,
            certfile=CERTFILE,
            cert_reqs=ssl.CERT_NONE,
            ssl_version=ssl.PROTOCOL_SSLv23,
            )

        self.logRequests = False

        self.server_bind()
        #self.server._current_user = None
        self.server_activate()

class VerifyingRequestHandler(SimpleXMLRPCRequestHandler):
    '''
    Request Handler that verifies username and password passed to
    XML RPC server in HTTP URL sent by client.
    '''

    def parse_request(self):
        # first, call the original implementation which returns
        # True if all OK so far
        if SimpleXMLRPCRequestHandler.parse_request(self):
            # next we authenticate
            if self.authenticate(self.headers):
                return True
            else:
                # if authentication fails, tell the client
                self.send_error(401, 'Authentication failed')
        return False

    def authenticate(self, headers):
        from base64 import b64decode
        #    Confirm that Authorization header is set to Basic
        (basic, _, encoded) = headers.get('Authorization').partition(' ')
        assert basic == 'Basic', 'Only basic authentication supported'

        #    Encoded portion of the header is a string
        #    Need to convert to bytestring
        encodedByteString = encoded.encode()

        #    Decode Base64 byte String to a decoded Byte String
        decodedBytes = b64decode(encodedByteString)

        #    Convert from byte string to a regular String
        decodedString = decodedBytes.decode()

        #    Get the username and password from the string
        (username, _, password) = decodedString.partition(':')
        return self.check_user(username,password)

    def check_user(self, username, password):
        '''
        see if this user has authenticated correctly
        return a simple True or False
        '''
        log = logging.getLogger("openmolar_server")
        self.set_proxy_user()
        if username in USERDICT:
            if USERDICT[username] == md5(password).hexdigest():
                self.set_proxy_user(username)
                log.info("authenticated user '%s'"% username)
                return True
        log.error("authenticate failure for user '%s'"% username)
        return False

    def set_proxy_user(self, user=None):
        '''
        when a user authenticates, make the username accessible to the
        registered functions
        '''
        self.server.function_instance._current_user = user

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    logging.debug(USERDICT)
