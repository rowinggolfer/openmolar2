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

class OpenmolarConnection(object):
    '''
    a class which connects to the openmolar xmlrpc server
    '''
    HOST = "127.0.0.1"
    PORT = 230
    def connect(self, host=HOST, port=PORT):
        '''
        attempt to connect to xmlrpc_server, and return this object
        raise a ConnectionError if no success.
        '''
        location = 'http://%s:%d'% (host, port)
        logging.debug("attempting connection to %s"% location)
        try:
            proxy = xmlrpclib.ServerProxy(location)
            proxy.ping()
            logging.debug("connected and pingable (this is good!)")
            return proxy
        except socket.error as e:
            logging.exception(
            "error connecting to the openmolar-xmlrpc server %s"% location)

            raise OpenmolarConnectionError(
            'Is the host %s running and accepting connections on port %d?'% (
            host, port))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    omc = OpenmolarConnection()
    proxy = omc.connect()
    if proxy is not None:
        print proxy.last_backup()