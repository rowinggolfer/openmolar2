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

def get_logger(level):
    #formatter = logging.Formatter("%(levelname)s:%(message)s")

    #handler = logging.StreamHandler()
    #handler.setFormatter(formatter)

    logging.basicConfig(level=level,
                format='%(asctime)s %(levelname)s %(message)s')

    LOGGER = logging.getLogger("openmolar-admin")
    #LOGGER.setLevel(level)
    #LOGGER.addHandler(handler)

    return LOGGER

def install(level=logging.DEBUG):
    '''
    make an instance of this object acessible in the global namespace
    >>>
    '''
    import __builtin__
    __builtin__.__dict__["LOGGER"] = get_logger(level)
    LOGGER.debug("Installing an instance of LOGGER into globals")

if __name__ == "__main__":
    install()
