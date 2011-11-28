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

import commands
import logging
import os
import socket
import sys
import time
import threading


from service import Service
from functions import ServerFunctions
from lib_openmolar.server import logger
from lib_openmolar.server.verifying_servers import VerifyingServerSSL

##############################################################################
##  create a pair with openssl http://openssl.org/                          ##
##                                                                          ##
##  ~$ openssl req -new -x509 -days 365 -nodes -out cert.pem \              ##
##                             -keyout privatekey.pem                       ##
##                                                                          ##
##############################################################################

KEYFILE  = '/etc/openmolar/server/privatekey.pem'
CERTFILE = '/etc/openmolar/server/cert.pem'
SSL_AVAILABLE = os.path.exists(KEYFILE) and os.path.exists(CERTFILE)

SSL_PORT = 230
PORT = 1230

def ssl_available():
    return SSL_AVAILABLE

class OMServer(Service):
    server = None
    def __init__(self, verbose=False):
        self.log = logging.getLogger("openmolar_server")
        if verbose:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)

    def start(self):
        self.log.info("starting OMServer Process")

        try:
            self.server = VerifyingServerSSL(("", SSL_PORT), KEYFILE, CERTFILE)
        except socket.error:
            self.log.error('Unable to start the server.' +
                (' Port %d is in use' % SSL_PORT ) +
                ' (Perhaps openmolar server is already running?)')
            return

        self.log.info(
            "listening for ssl connections on port %d"% (SSL_PORT))

        # daemonise the process and write to /var/run
        self.start_()

        ## allow user to list methods?
        self.server.register_introspection_functions()
        self.server.register_instance(ServerFunctions())

        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.start()

    def stop(self):
        self.log.info("Stopping server")
        try:
            self.server.shutdown()
        except AttributeError: # could be a NoneType or pre 2.6 Baseserver
            pass
        self.stop_()

    def restart(self):
        self.stop()
        time.sleep(1)
        self.start()

    def status(self):
        self.status_()
