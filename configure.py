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

import ConfigParser
import optparse
import StringIO

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

CONF = '''

[common]
version = 2.0
include = True

[client]
version = 2.0
include = True

[admin]
version = 2.0
include = True

[server]
version = 2.0
include = True

[lang]
version = 2.0
include = False
'''


#this next line is always written if manifest option is chosen
MANIFEST = 'include setup.conf'

#these lines are appended as required
MANIFEST_admin = "include misc/admin/*"
MANIFEST_client = "include misc/client/*"
MANIFEST_server = "include misc/server/*"

class Parser(optparse.OptionParser):
    def __init__(self):
        optparse.OptionParser.__init__(self)

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
        option = self.add_option("-w", "--write_manifest",
                        dest = "manifest",
                        action="store_true", default=True,
                        help = "write the manifest file"
                        )

def manual_select(options):
    print "please choose from the following"

    for att in ("common", "client", "admin", "server", "lang"):
        result = raw_input("Include %s (Y/n)"% att)
        options.__dict__[att] = result.lower() in ("y", "")

if __name__ == "__main__":

    parser  = Parser()
    options, args = parser.parse_args()

    if parser.values == parser.defaults:
        try:
            manual_select(options)
        except:
            parser.print_help()
            sys.exit("nothing to do")

    f = open("setup.conf", "w")
    f.write(CONF)
    f.close()

    config = ConfigParser.RawConfigParser()
    config.read("setup.conf")

    config.set("common", "include", options.common)
    config.set("client", "include", options.client)
    config.set("admin", "include", options.admin)
    config.set("server", "include", options.server)
    config.set("lang", "include", options.lang)

    f = open("setup.conf", "w")
    f.write(HEADER)
    config.write(f)
    f.close()

    if options.manifest:
        f = open("MANIFEST.in", "w")
        f.write(MANIFEST)
        if options.client:
            f.write(MANIFEST_client)
        if options.admin:
            f.write(MANIFEST_admin)
        if options.server:
            f.write(MANIFEST_admin)
        f.close()

