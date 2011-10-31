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

from lib_openmolar.server import logger
from lib_openmolar.server import xmlrpc_server

import logging

logger.setup(level = logging.INFO, console_echo=False)

log = logging.getLogger("openmolar_server")
log.info("openmolar_server starting up")

try:
    xmlrpc_server.main()
except KeyboardInterrupt as e:
    log.warning("Keyboard interupt")
    e.handled = True
except Exception as e:
    log.exception("Server Terminated")

log.warning("openmolar_server closed")
logging.shutdown()
