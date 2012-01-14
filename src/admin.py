#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010, Neil Wallace <rowinggolfer@googlemail.com>               ##
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

'''
parses the command line options, which are minimal.
by default, raises the admin gui, but does expose some cli options.
'''
import logging
import os
import optparse
import sys

class Parser(optparse.OptionParser):
    def __init__(self):
        optparse.OptionParser.__init__(self,
            prog="openmolar-admin")
        
        self.add_option("--version",
        action="store_true", dest="show_version", default=False,
        help="show version and quit")

        self.add_option("-v", "--verbose",
            dest = "verbose",
            action="store_true", default=False,
            help = "verbose logging messages",
            )

        self.add_option("-q", "--quiet",
            dest = "quiet",
            action="store_true", default=False,
            help = "minimal logging messages",
            )

        self.add_option("-s", "--script",
            dest = "script",
            help = ("run the cli application"
                    "performing actions specified in plain text file SCRIPT"),
            type="string"
            )

def main():
    '''
    entry point for the openmolar-admin script.
    '''
    parser  = Parser()

    options, args = parser.parse_args()

    import lib_openmolar.admin

    if options.show_version:
        from lib_openmolar.admin.version import VERSION, revision_number
        print ("Openmolar-Admin %s~hg%s"% (VERSION, revision_number))
        sys.exit(0)

    if options.verbose:
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.warning("verbose output chosen (with -v flag)")
    elif options.quiet:
        LOGGER.setLevel(logging.WARNING)
        LOGGER.warning("minimal output chosen (with -q flag)")

    if options.script:
        if not os.path.isfile(options.script):
            sys.exit("no such script '%s'"% options.script)
        LOGGER.debug("using script - '%s'"% options.script)
        from lib_openmolar.admin import main_cli
        main_cli.main(options.script)
    else:
        from lib_openmolar.admin.qt4 import maingui
        maingui.main()


if __name__ == "__main__":
    main()
