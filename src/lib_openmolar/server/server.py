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

from SimpleXMLRPCServer import SimpleXMLRPCServer

from service import Service
from functions import ServerFunctions
import logger

PORT = 42230

def ping():
    return True

class OMServer(Service):
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

        server = SimpleXMLRPCServer(("", PORT))
        server.register_function(ping)
        server.register_instance(ServerFunctions())

        self.log.info("listening on port %d"% (PORT))
        server.serve_forever()

    def stop(self):
        self.log.info("Stopping server")
        self.stop_()

    def restart(self):
        self.stop()
        self.start()

    def status(self):
        self.status_()
