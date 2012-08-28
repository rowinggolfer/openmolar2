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

import __builtin__
import logging
import logging.handlers
import os
import sys

BASE = "openmolar"
APPLICATION = "server"

LOGNAME = "%s_%s"% (BASE, APPLICATION)
LOCATION = "/var/log/%s/%s.log"% (BASE, APPLICATION)

LOGDIR = os.path.dirname(LOCATION)

def setup(level=logging.DEBUG):
    """
    initiates the logger.
    allows caller to set the debug level and whether to echo the log to stdout
    """
    if not os.path.isdir(LOGDIR):
        os.makedirs(LOGDIR)

    logger = logging.getLogger(LOGNAME)

    logging.basicConfig(level=level)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.handlers.TimedRotatingFileHandler(
        LOCATION, when="D", interval=1, backupCount=10, utc=True)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    __builtin__.LOGGER = logger

def _test():
    try:
        setup()
        LOGGER.debug("debug message")
        LOGGER.info("info message")
        LOGGER.warn("warn message")
        LOGGER.error("error message")
        LOGGER.critical("critical message")
    except IOError as exc:
        if exc.errno == 13:
            sys.stderr.write(
            "You do not have permission to write this log to\n%s\n"% LOCATION)
    logging.shutdown()

if __name__ == "__main__":
    _test()
