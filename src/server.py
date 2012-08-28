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

import logging
from optparse import OptionParser
import sys

from lib_openmolar.server import server
from lib_openmolar.server.misc import logger
from lib_openmolar.server.misc.om_server_config import OMServerConfig


def first_run():
    log = logging.getLogger("openmolar_server")
    conf = OMServerConfig()
    if not conf.is_installed:
        log.warning("First run of openmolar_server")
        from lib_openmolar.server.misc.installer import Installer
        installer = Installer()
        installer.install()
    else:
        conf.update()

def main():
    parser = OptionParser()
    parser.add_option("--start", action="store_true",
        help="start the server")
    parser.add_option("--stop", action="store_true",
        help="stop the server")
    parser.add_option("--restart", action="store_true",
        help="restart the server")
    parser.add_option("--status", action="store_true",
        help="check the status of the server")

    parser.add_option("--version",
        action="store_true", dest="show_version", default=False,
        help="show version and quit")

    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=True,
                  help="log debug messages")

    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose",
                  help="ignore debug messages")

    options, args = parser.parse_args()

    if options.show_version:
        from lib_openmolar.server.version import VERSION, revision_number
        print ("Openmolar-Server %s~hg%s"% (VERSION, revision_number))
        sys.exit(0)

    try:
        logger.setup(level = logging.INFO) #, console_echo=True)
    except IOError as exc:
        if exc.errno == 13:
            sys.exit("You have to be root to run this script")
        raise exc

    omserver = server.OMServer(options.verbose)

    if options.start:
        first_run()
        omserver.start()
    elif options.stop:
        omserver.stop()
        logging.shutdown()
    elif options.restart:
        first_run()
        omserver.restart()
    elif options.status:
        omserver.status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
