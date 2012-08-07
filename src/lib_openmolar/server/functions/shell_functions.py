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
import subprocess
import sys

def log_exception(func):
    def shell_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            LOGGER.exception("unhandled exception")
            return ""
    return shell_func

class ShellFunctions(object):
    '''
    A class whose functions will be inherited by the server
    '''
    
    @log_exception
    def install_fuzzymatch(self, dbname):
        '''
        installs fuzzymatch functions into database with the name given
        '''
        LOGGER.info("Installing fuzzymatch functions into database '%s'"% dbname)
        try:
            p = subprocess.Popen(["openmolar-fuzzymatch", dbname],
                stdout = subprocess.PIPE)
            while True:
                line = p.stdout.readline()
                if not line:
                    break
                LOGGER.info(line)
        except Exception as exc:
            LOGGER.exception("unable to install fuzzymatch into '%s'"% dbname)
            return False
        return True

def _test():
    '''
    test the ShellFunctions class
    '''
    sf = ShellFunctions()
    sf.install_fuzzymatch("openmolar_demo")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    LOGGER = logging.getLogger("openmolar_server")
    
    _test()
