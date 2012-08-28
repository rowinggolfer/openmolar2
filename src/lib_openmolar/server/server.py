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

'''
This module provides the OpenMolar Server.
'''

import logging
import os
import socket
import time
import threading

from lib_openmolar.server.daemon.service import Service
from lib_openmolar.server.permission_dispatcher import PermissionDispatcher
from lib_openmolar.server.misc import logger
from lib_openmolar.server.servers.verifying_servers import VerifyingServerSSL
from lib_openmolar.server.misc.om_server_config import OMServerConfig


##############################################################################
##  create a pair with openssl http://openssl.org/                          ##
##                                                                          ##
##  ~$ openssl req -new -x509 -days 365 -nodes -out cert.pem  \             ##
##                             -keyout privatekey.pem                       ##
##                                                                          ##
##############################################################################

class OMServer(Service):

    server = None
    '''
    A pointer to the :doc:`VerifyingServerSSL`
    '''
    def __init__(self, verbose=False):
        if verbose:
            LOGGER.setLevel(logging.DEBUG)
            LOGGER.debug("logging in verbose mode")
            import lib_openmolar
            LOGGER.debug(
                "using module lib_openmolar from %s"% lib_openmolar.__file__)
        else:
            LOGGER.setLevel(logging.INFO)

    def start(self):
        '''
        start the server
        '''
        LOGGER.info("starting OMServer Process")
        config = OMServerConfig()
        loc = config.location
        port = config.port
        key = config.private_key
        cert = config.pub_key
        if not (os.path.isfile(key) and os.path.isfile(cert)):
            raise IOError, "certificate '%s' and/or key '%s' not found"% (
                                                                cert, key)
        try:
            self.server = VerifyingServerSSL((loc, port), key, cert)
        except socket.error:
            LOGGER.error('Unable to start the server.' +
                (' Port %d is in use' % port ) +
                ' (Perhaps openmolar server is already running?)')
            return

        if loc == "":
            readable_loc = "on all interfaces"
        else:
            readable_loc = loc
        LOGGER.info(
            "listening for ssl connections %s port %d"% (readable_loc, port))
        LOGGER.debug("using cert %s"% cert)
        LOGGER.debug("using key %s"% key)

        # daemonise the process and write to /var/run
        self.start_(stderr=logger.LOCATION)

        self.server.register_instance(PermissionDispatcher())
        for manager, hash in config.managers:
            self.server.add_user(manager, hash)

        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.start()

    def stop(self):
        '''
        stop the server
        '''
        if not self.is_running:
            return
        LOGGER.info("Stopping server")
        try:
            self.server.shutdown()
        except AttributeError:
            # will be thrown if self.server is None
            # or pre 2.6 Baseserver(which lacks this function)
            pass
        self.stop_()

    def restart(self):
        '''
        restart the server
        '''
        self.stop()
        time.sleep(1)
        self.start()

    def status(self):
        '''
        report the status of the server
        '''
        self.status_()
