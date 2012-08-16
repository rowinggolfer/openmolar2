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

import os
import subprocess

from lib_openmolar.server.misc.om_server_config import OMServerConfig
from lib_openmolar.server.misc.logger import LOGDIR


class Installer(object):
    '''
    A class to "install" the server application,
    creates a master user with random password,
    creates a master database,
    sets out the directory structure.
    '''
    def __init__(self):
        self.config = OMServerConfig()

    @property
    def chk_install(self):
        return self.config.is_installed

    def check_current(self):
        '''
        update the config file if neccessary
        '''
        if not self.config.is_current:
            self.config.update()

    def make_dirs(self):
        for dir in (self.config.conf_dir, LOGDIR):
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

        for script in (
        "openmolar-init-master-user",
        "openmolar-alter-master-user"
        ):
        
            LOGGER.info("calling script %s"% script)

            p = subprocess.Popen([script],
                stdout=subprocess.PIPE )

            while True:
                line = p.stdout.readline()
                if not line:
                    break
                LOGGER.info(line)

    def init_master_db(self):
        '''
        initialises the openmolar_master database
        '''
        LOGGER.info("calling script openmolar-init-master-db")

        p = subprocess.Popen(["openmolar-init-master-db"],
            stdout=subprocess.PIPE )

        while True:
            line = p.stdout.readline()
            if not line:
                break
            LOGGER.debug(line)

    def install(self):
        '''
        this should normally only be called on the very first running of the
        server application
        '''
        self.make_dirs()
        self.write_config()
        self.init_master_user()
        self.init_master_db()

