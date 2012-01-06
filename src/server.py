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
from optparse import OptionParser
import os
import sys
import subprocess
from lib_openmolar.server import server
from lib_openmolar.server.functions import logger
from lib_openmolar.server.functions.om_server_config import OMServerConfig

LOGDIR = "/var/log/openmolar/server/"

class Installer(object):
    '''
    A class to install the server application,
    creates a master user with random password,
    creates a master database,
    sets out the directory structure.
    '''
    def __init__(self):
        self.config = OMServerConfig()

    @property
    def chk_install(self):
        return self.config.is_installed

    def make_dirs(self):
        for dir in (self.config.etc_dir, LOGDIR):
            try:
                print "making directory", dir
                os.makedirs(dir)
            except OSError as exc:
                if exc.errno == 13:
                    print ("You do not have permission to create %s"% dir)
                    print ("Are you Root?")
                    sys.exit(0)

    def write_config(self):
        '''
        write the config file for openmolar
        '''
        self.config.new_config()
        self.config.write()

    def init_master_user(self):
        '''
        initialises the user "openmolar"
        '''
        log = logging.getLogger("openmolar_server")
        log.info("calling script openmolar-init-master-user")

        p = subprocess.Popen(["openmolar-init-master-user"],
            stdout=subprocess.PIPE )

        while True:
            line = p.stdout.readline()
            if not line:
                break
            log.info(line)

    def init_master_db(self):
        '''
        initialises the openmolar_master database
        '''
        log = logging.getLogger("openmolar_server")
        log.info("calling script openmolar-init-master-db")

        p = subprocess.Popen(["openmolar-init-master-db"],
            stdout=subprocess.PIPE )

        while True:
            line = p.stdout.readline()
            if not line:
                break
            log.info(line)

    def install(self):
        '''
        this should normally only be called on the very first running of the
        server application
        '''
        self.make_dirs()
        self.write_config()
        self.init_master_user()
        self.init_master_db()

def first_run():
    log = logging.getLogger("openmolar_server")
    installer = Installer()
    if not installer.chk_install:
        log.warning("First run of openmolar_server")
        log.info("installing server")
        installer.install()

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

    log = logging.getLogger("openmolar_server")
    omserver = server.OMServer(options.verbose)

    if options.start:
        first_run()
        omserver.start()
    elif options.stop:
        omserver.stop()
    elif options.restart:
        first_run()
        omserver.restart()
    elif options.status:
        omserver.status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
