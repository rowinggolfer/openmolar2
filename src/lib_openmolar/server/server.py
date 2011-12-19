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
from lib_openmolar.server.functions.instance import ServerFunctions
from lib_openmolar.server.functions import logger
from lib_openmolar.server.verifying_servers import VerifyingServerSSL
from lib_openmolar.server.functions.om_server_config import OMServerConfig

##############################################################################
##  create a pair with openssl http://openssl.org/                          ##
##                                                                          ##
##  ~$ openssl req -new -x509 -days 365 -nodes -out cert.pem \              ##
##                             -keyout privatekey.pem                       ##
##                                                                          ##
##############################################################################

class OMServer(Service):
    server = None
    def __init__(self, verbose=False):
        self.log = logging.getLogger("openmolar_server")
        if verbose:
            self.log.setLevel(logging.DEBUG)
            self.log.debug("logging in verbose mode")
        else:
            self.log.setLevel(logging.INFO)

    def start(self):
        self.log.info("starting OMServer Process")
        config = OMServerConfig()
        loc = config.location
        port = config.port
        key = config.private_key
        cert = config.pub_key
        try:
            self.server = VerifyingServerSSL((loc, port), key, cert)
        except socket.error:
            self.log.error('Unable to start the server.' +
                (' Port %d is in use' % port ) +
                ' (Perhaps openmolar server is already running?)')
            return

        if loc == "":
            readable_loc = "on all interfaces"
        else:
            readable_loc = loc
        self.log.info(
            "listening for ssl connections %s port %d"% (readable_loc, port))
        self.log.debug("using cert %s"% cert)
        self.log.debug("using key %s"% key)

        # daemonise the process and write to /var/run
        self.start_(stderr=logger.LOCATION)

        ## allow user to list methods?
        self.server.register_introspection_functions()
        self.server.register_instance(ServerFunctions())

        for manager, hash in config.managers:
            self.server.add_user(manager, hash)

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
