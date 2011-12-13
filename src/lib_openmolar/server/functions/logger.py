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

import logging
import logging.handlers
import os
import sys

BASE = "openmolar"
APPLICATION = "server"

LOGNAME = "%s_%s"% (BASE, APPLICATION)
LOCATION = "/var/log/%s/%s.log"% (BASE, APPLICATION)

def setup(level=logging.DEBUG, console_echo=True):
    """
    initiates the logger.
    allows caller to set the debug level and whether to echo the log to stdout
    """
    logger = logging.getLogger(LOGNAME)
    logger.setLevel(level)

    dirname = os.path.dirname(LOCATION)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s")

    handler = logging.handlers.TimedRotatingFileHandler(
        LOCATION, "D", 1, backupCount=10)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if console_echo:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

def _test():
    try:
        setup()
        my_logger = logging.getLogger(LOGNAME)
        my_logger.debug("debug message")
        my_logger.info("info message")
        my_logger.warn("warn message")
        my_logger.error("error message")
        my_logger.critical("critical message")
    except IOError as exc:
        if exc.errno == 13:
            sys.stderr.write(
            "You do not have permission to write this log to\n%s\n"% LOCATION)
    logging.shutdown()

if __name__ == "__main__":
    _test()
