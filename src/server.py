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
from lib_openmolar.server import logger
from lib_openmolar.server.password_generator import new_password

LOGDIR = "/var/log/openmolar/server/"
ETCDIR = "/etc/openmolar/server/"
PWORD_FILE = "/etc/openmolar/server/master_pword.txt"

class Installer(object):
    '''
    A class to install the server application,
    creates a master user with random password,
    creates a master database,
    sets out the directory structure.
    '''

    @property
    def chk_install(self):
        return (
            os.path.isfile(PWORD_FILE) and
            os.path.isdir(LOGDIR) and
            os.path.isdir(ETCDIR))

    def make_dirs(self):
        for dir in (ETCDIR, LOGDIR):
            try:
                print "making directory", dir
                os.makedirs(dir)
            except OSError as exc:
                if exc.errno == 13:
                    print ("You do not have permission to create %s"% dir)
                    print ("Are you Root?")
                    sys.exit(0)

    def create_password(self):
        '''
        look for a master password in %s
        if it doesn't exist, create it.
        the permissions of this file are changed to 600 so that only root can
        read and write it.
        '''% PWORD_FILE
        if not os.path.isfile(PWORD_FILE):
            f = open(PWORD_FILE, "w")
            f.write("%s\n"% new_password(20))
            f.close()
            os.chmod(PWORD_FILE, 600)

    def init_master_user(self):
        '''
        initialises the user "openmolar"
        '''
        log = logging.getLogger("openmolar_server")
        log.info("initiating master user")

        p = subprocess.Popen(["openmolar-init-master-user"])
        p.wait()

    def init_master_db(self):
        '''
        initialises the openmolar_master database
        '''
        log = logging.getLogger("openmolar_server")
        log.info("initiating master database")

        p = subprocess.Popen(["openmolar-init-master-db"])
        p.wait()

    def install(self):
        '''
        this should normally only be called on the very first running of the
        server application
        '''
        self.make_dirs()
        self.create_password()
        self.init_master_user()
        self.init_master_db()

def first_run():
    log = logging.getLogger("openmolar_server")
    installer = Installer()
    if not installer.chk_install:
        log.warning("First run of server")
        log.info("installing server")
        installer.install()

def main():
    logger.setup(level = logging.INFO, console_echo=True)
    log = logging.getLogger("openmolar_server")
    parser = OptionParser()
    parser.add_option("--start", action="store_true",
        help="start the server")
    parser.add_option("--stop", action="store_true",
        help="stop the server")
    parser.add_option("--restart", action="store_true",
        help="restart the server")
    parser.add_option("--status", action="store_true",
        help="check the status of the server")
    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=False,
                  help="don't print status messages to stdout")

    options, args = parser.parse_args()

    omserver = server.OMServer(verbose=True)

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
