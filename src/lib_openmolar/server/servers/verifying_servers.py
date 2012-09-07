#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
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

from base64 import b64decode
from hashlib import md5
import pickle
import socket
import ssl
from SocketServer import BaseServer
from SimpleXMLRPCServer import (
    SimpleXMLRPCServer,
    SimpleXMLRPCDispatcher,
    SimpleXMLRPCRequestHandler)


def ping():
    '''
    A trivial function given to all servers for testing purposes
    '''
    #LOGGER.debug("server has been pinged")
    return True

class VerifyingServer(SimpleXMLRPCServer):
    '''
    an extension of SimpleXMLPRCServer
    which enforces user authentication
    '''

    USERDICT = {"default":md5("eihjfosdhvpwi").hexdigest()}

    registered_instance = None
    '''
    this attribute is a pointer to the instance passed into
    SimpleXMLRPCServer.register_instance()
    if this instance needs to know the user.. give it a special function
    _remember_user(user)
    '''

    def __init__(self, addr):
        SimpleXMLRPCDispatcher.__init__(self)
        SimpleXMLRPCServer.__init__(self, addr, VerifyingRequestHandler)
        self.logRequests = False # the request handler logs enough detail

        self.register_function(ping, "ping")

    def register_instance(self, klass):
        '''
        re-implement this function so that our set_user function makes sense!
        '''
        LOGGER.debug("registering instance %s"% klass)
        self.registered_instance = klass
        try:
            klass._remember_user(None)
            self.HAS_SMART_INSTANCE = True
        except AttributeError:
            self.HAS_SMART_INSTANCE = False
            LOGGER.debug(
    "the registered instance does not have special function _remember_user")

        SimpleXMLRPCServer.register_instance(self, klass)

    def add_user(self, user, hash):
        '''
        add a user to the userdict
        password should be MD5 hashed.
        '''
        LOGGER.debug("adding user %s with hashed pass %s"% (user, hash))
        self.USERDICT[user] = hash
        LOGGER.debug("current user list is %s"% sorted(self.USERDICT.keys()))


class VerifyingServerSSL(VerifyingServer):
    '''
    an extension of SimpleXMLPRCServer
    which enforces ssl connection, and user authentication
    '''

    def __init__(self, addr, KEYFILE, CERTFILE):
        SimpleXMLRPCDispatcher.__init__(self)

        VerifyingServer.__init__(self, addr)
        self.socket = ssl.wrap_socket(
            socket.socket(self.address_family, self.socket_type),
            server_side=True,
            keyfile=KEYFILE,
            certfile=CERTFILE,
            cert_reqs=ssl.CERT_NONE,
            ssl_version=ssl.PROTOCOL_SSLv23,
            )

        self.server_bind()
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

        auth_header = headers.get('Authorization')
        if auth_header is None:
            return False

        #    Confirm that Authorization header is set to Basic
        (basic, _, encoded) = auth_header.partition(' ')
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
        LOGGER.debug("checking_user %s"% username)
        self.set_proxy_user()
        if username in self.server.USERDICT:
            if self.server.USERDICT[username] == md5(password).hexdigest():
                self.set_proxy_user(username)
                LOGGER.debug("authenticated user '%s'"% username)
                return True
        LOGGER.error("authenticate failure for user '%s'"% username)
        return False

    def set_proxy_user(self, user=None):
        '''
        when a user authenticates, make the username accessible to the
        registered functions
        '''
        self.server.registered_instance._remember_user(user)

def _test():
    s = VerifyingServer(("",1430))
    s.serve_forever()

def _test_ssl():
    s = VerifyingServerSSL(("",1430),
        '/usr/share/openmolar/privatekey.pem',
        '/usr/share/openmolar/cert.pem')
    LOGGER.debug(s.USERDICT)

    s.serve_forever()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level = logging.DEBUG)

    LOGGER = logging.getLogger("test")
    #_test()
    _test_ssl()
