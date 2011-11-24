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
import socket
import sys
import threading

from simple_xmlrpc_server_tls import SimpleXMLRPCServerTLS

from service import Service
from functions import ServerFunctions
import logger

PORT = 230

def ping():
    return True

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
        if not self.start_():
            return False
        self.log.info("creating server...")

        self.server = SimpleXMLRPCServerTLS(("", PORT))
        self.server.register_function(ping)

        ## allow user to list methods?
        self.server.register_introspection_functions()

        functions = ServerFunctions()
        self.server.register_instance(functions)
        self.server.function_instance = functions
        self.log.info("listening on port %d"% (PORT))
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
        self.start()

    def status(self):
        self.status_()
