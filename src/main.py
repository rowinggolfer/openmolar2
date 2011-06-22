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

VERSION = "1.2.0alpha1"

gettext.install('openmolar', unicode=True)

class Parser(optparse.OptionParser):
    def __init__(self):
        from lib_openmolar import _version

        optparse.OptionParser.__init__(self,
            prog="openmolar2",
            version="%s~hg%s"%(VERSION, _version.revision_number),
            )

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

        option = self.add_option("-i", "--install-demo",
                        dest = "install_demo",
                        action="store_true", default=False,
                        help = "install a demo database (in default location)",
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
        
    if options.terminal:
        term_prefix = ["gnome-terminal", "-x"]
    else:
        term_prefix = []

    if options.admin:
        print "running admin app as process %s"%(
        subprocess.Popen(term_prefix +
            ["python", "admin_app.py"]).pid)

    if options.client:
        print "running client app as process %s"%(
        subprocess.Popen(term_prefix +
            ["python", "client_app.py"]).pid)

    if options.install_demo:
        print "install a demo db - process id %s"% (

        #I might have to do something like this??

        #subprocess.Popen(term_prefix +
        #    ["gksu", "-u", "postgres",
        #    "python admin_app.py --install-demo"]).pid)

        subprocess.Popen(term_prefix +
            ["python", "admin_app.py", "--install-demo"]).pid)

    
if __name__ == "__main__":
    main()
