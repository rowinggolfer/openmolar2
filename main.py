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
from optparse import OptionParser


lang = os.environ.get("LANG")
if lang:
    try:
        lang1 = gettext.translation('openmolar', languages=[lang,])
        lang1.install(unicode=True)
    except IOError:
        print "%s not found, using default"% lang
        gettext.install('openmolar', unicode=True)
else:
    print "no language environment found"
    gettext.install('openmolar', unicode=True)


class Parser(OptionParser):
    def __init__(self):
        OptionParser.__init__(self)

        self.add_option("-a", "--admin",
                        dest = "admin",
                        action="store_true", default=False,
                        help = _("open the admin appliation")
                        )

        self.add_option("-c", "--client",
                        dest = "client",
                        action="store_true", default=False,
                        help = _("open the admin appliation"),
                        )

        self.add_option("--install-demo",
                        dest = "install_demo",
                        action="store_true", default=False,
                        help = "install a demo database",
                        )

        self.add_option("--test-suite",
                        dest = "test_suite",
                        action="store_true", default=False,
                        help = "run the code test suite",
                        )

def change_dir():
    def determine_path ():
        """Borrowed from wxglade.py"""
        root = __file__
        if os.path.islink (root):
            root = os.path.realpath (root)
        retarg = os.path.dirname (os.path.abspath (root))
        return retarg

    os.chdir(os.path.join(determine_path(), "src"))

def main():
    '''
    entry point of the entire openmolar suite
    '''
    change_dir()

    parser  = Parser()
    options, args = parser.parse_args()

    if parser.values == parser.defaults:
        import options_gui
        if options_gui.main(parser):
            parser  = Parser()
        options, args = parser.parse_args()

    if options.admin:
        print "running admin app as process %s"%(
        subprocess.Popen(["python", "admin_app.py"]).pid)

    if options.client:
        print "running client app as process %s"%(
        subprocess.Popen(["python", "client_app.py"]).pid)

    if options.install_demo:
        print "install a demo db"

    if options.test_suite:
        print "running test suite as process %s"%(
        subprocess.Popen(["python", "test_suite.py"]).pid)


if __name__ == "__main__":
    main()
