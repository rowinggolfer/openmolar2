#!/usr/bin/env python
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

import __builtin__
import ConfigParser
import logging
import optparse
import os
import StringIO
import sys

from version_number import VERSION_NUMBER
import version_manager

version_manager.main()

sys.path.insert(0, os.path.abspath("src"))

logging.basicConfig(level=logging.ERROR)

class OMConfig(ConfigParser.RawConfigParser):
    '''
    subclass RawConfigParser with default values and an overwrite of the write
    function so that a nice header is included
    '''
    HEADER = '''
# As openmolar is a suite of applications with a common source code directory
# some configuration is required before running setup.py
#
# setup.py is capable of installing any combination of
# common, admin, server, client, language "packages"
#
# or creating a pure source distribution for that element
#
'''

    DICT = {"namespace":'False',
            "common": 'False',
            "client": 'False',
            "admin" : 'False',
            "server": 'False',
            "lang"  : 'False'}

    ATTS = DICT.keys()

    def __init__(self):
        ConfigParser.RawConfigParser.__init__(self)
        for att in self.ATTS:
            self.add_section(att)
            self.set(att, "include", self.DICT[att])
            self.set(att, "version", VERSION_NUMBER)
            try:
                if att not in ("namespace", "lang"):
                    # this is the equiv of
                    # from admin import version 
                    logging.debug("getting version for %s"% att)
                    version = __import__("lib_openmolar.%s.version"% att, fromlist=["version"])
                    self.set(att, "revision_number", version.revision_number)
                    self.set(att, "revision_id", version.revision_id)
                    try:
                        __builtin__.__dict__.pop("LOGGER")
                        __builtin__.__dict__.pop("SETTINGS")                        
                    except KeyError:
                        pass
            except ImportError:
                logging.exception(
                "IMPORT ERROR - hg generated version files not present for package %s"% att)
                sys.exit("version files not present. Unable to proceed")
                
    def write(self, f):
        '''
        re-implement write so that our header is included
        '''
        f.write(self.HEADER)
        ConfigParser.RawConfigParser.write(self, f)


class Parser(optparse.OptionParser):
    def __init__(self):
        optparse.OptionParser.__init__(self)

        option = self.add_option("-n", "--namespace",
                        dest = "namespace",
                        action="store_true", default=False,
                help = "package or install sources for the namespace"
                        )
        option = self.add_option("-a", "--admin",
                        dest = "admin",
                        action="store_true", default=False,
                help = "package or install sources for the admin application"
                        )

        option = self.add_option("-c", "--client",
                        dest = "client",
                        action="store_true", default=False,
                help = "package or install sources for the client application"
                        )

        option = self.add_option("-l", "--lang",
                        dest = "lang",
                        action="store_true", default=False,
                help = "package or install sources for the language pack"
                        )

        option = self.add_option("-o", "--common",
                        dest = "common",
                        action="store_true", default=False,
                help = "package or install sources for lib_openmolar.common"
                        )

        option = self.add_option("-s", "--server",
                        dest = "server",
                        action="store_true", default=False,
                help = "package or install sources for the server application"
                        )

def manual_select(options):
    print "please choose from the following"

    for att in OMConfig.ATTS:
        result = raw_input("Include %s (Y/n)"% att)
        options.__dict__[att] = str(result.lower() in ("y", ""))

if __name__ == "__main__":

    parser  = Parser()
    options, args = parser.parse_args()

    if parser.values == parser.defaults:
        try:
            manual_select(options)
        except:
            parser.print_help()
            sys.exit("nothing to do")

    config = OMConfig()
    for att in config.ATTS:
        config.set(att, "include", options.__dict__[att])

    f = open("setup.cnf", "w")
    config.write(f)
    f.close()


