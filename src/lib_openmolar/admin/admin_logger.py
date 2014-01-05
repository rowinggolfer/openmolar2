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

def get_logger(level):

    logging.basicConfig(level=level,
                format='%(asctime)s %(levelname)s %(message)s')

    LOGGER = logging.getLogger("openmolar-admin")

    return LOGGER

def install(level=logging.INFO):
    '''
    make an instance of this object acessible in the global namespace
    '''
    try:
        LOGGER
        LOGGER.warning(
        "\n\tAbandoned a second attempt to install LOGGER into globals\n"
        "\tTHIS SHOULD NOT HAPPEN!!\n"
        "\tperhaps code is being imported from both admin and client?"
        )
    except NameError:
        import __builtin__
        __builtin__.LOGGER = get_logger(level)

if __name__ == "__main__":
    install()
