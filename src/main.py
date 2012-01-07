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
Test code, which offers the user a choice of admin or client app.
'''

import gettext
import os
import subprocess
import sys
import optparse

from version import VERSION, revision_number

gettext.install('openmolar', unicode=True)

class Parser(optparse.OptionParser):
    def __init__(self):
        self.version_str = "%s~hg%s"% (VERSION, revision_number)
        optparse.OptionParser.__init__(self,
            prog="openmolar2",
            version=self.version_str)

        option = self.add_option("-a", "--admin",
                        dest = "admin",
                        action="store_true", default=False,
                        help = _("launch the admin application")
                        )

        option = self.add_option("-c", "--client",
                        dest = "client",
                        action="store_true", default=False,
                        help = _("launch the client application"),
                        )

        option = self.add_option("-t", "--terminal",
                        dest = "terminal",
                        action="store_true", default=True,
                        help =  "run all chosen processes in terminals\n"
                                "(gnome-terminal)\n"
                                "True by default"
                       )

        option = self.add_option("-n", "--no-terminal",
                        dest = "terminal",
                        action="store_false",
                        help = "do not run all chosen processes in terminals\n"
                               "(overrides -t)"
                       )

        option = self.add_option("-s", "--test-suite",
                        dest = "tests",
                        action="store_true", default=False,
                        help = _("run the test suite"),
                        )

        option = self.add_option("-v", "--verbose",
                        dest = "verbose",
                        action="store_true", default=False,
                        help = _("verbose output (useful for debugging)"),
                        )


def change_dir():
    def determine_path ():
        """Borrowed from wxglade.py"""
        root = __file__
        if os.path.islink (root):
            root = os.path.realpath (root)
        retarg = os.path.dirname (os.path.abspath (root))
        return retarg

    os.chdir(determine_path())
    sys.path.insert(0, ".")

def main():
    '''
    entry point of the entire openmolar suite
    '''
    change_dir()

    parser  = Parser()

    options, args = parser.parse_args()
    if parser.values == parser.defaults:
        parser.print_help()
        sys.exit("nothing to do")

    prefixes, suffixes = [], []

    if options.terminal:
        prefixes += ["gnome-terminal", "-x"]

    if options.verbose:
        suffixes += ["-v"]
        print "Running openmolar version %s"% (parser.version_str)

    if options.admin:
        print "running admin app as process %s"%(
        subprocess.Popen(
            prefixes + ["python", "admin.py"] + suffixes
            ).pid)

    if options.client:
        print "running client app as process %s"%(
        subprocess.Popen(
            prefixes + ["python", "client.py"] + suffixes
            ).pid)

    if options.tests:
        print "running test suite as process %s"%(
        subprocess.Popen(
            prefixes + ["python", "tests.py"] + suffixes
            ).pid)


if __name__ == "__main__":
    main()
