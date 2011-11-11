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

class ShellFunctions(object):
    '''
    A class whose functions will be inherited by the server
    '''
    def install_fuzzymatch(self, name):
        '''
        installs fuzzymatch functions into database with the name given
        '''
        log = logging.getLogger("openmolar_server")
        log.info("Installing fuzzymatch functions into database '%s'"% name)
        try:
            p = subprocess.Popen(["openmolar-install-fuzzymatch", name])
            p.wait()
        except Exception as exc:
            log.exception("unable to install fuzzymatch into '%s'"% name)
            return False
        return True

def _test():
    '''
    test the ShellFunctions class
    '''
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger("openmolar_server")
    sf = ShellFunctions()
    #log.debug(sf.get_demo_user())

if __name__ == "__main__":
    _test()
