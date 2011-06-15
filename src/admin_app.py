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
this module puts the "lib_openmolar" onto the python path,
and starts the admin gui
'''

import gettext
import os
import sys

from PyQt4 import QtGui, QtCore

lang = os.environ.get("LANG")
if lang:
    try:
        print "trying to install your environment language", lang
        lang1 = gettext.translation('openmolar', languages=[lang,])
        lang1.install(unicode=True)
    except IOError:
        print "%s not found, using default"% lang
        gettext.install('openmolar', unicode=True)
else:
    print "no language environment found"
    gettext.install('openmolar', unicode=True)

def run():
    '''
    main function
    '''
    from lib_openmolar.admin.qt4gui import maingui
    maingui.main()

if __name__ == "__main__":
    def determine_path ():
        """Borrowed from wxglade.py"""
        try:
            root = __file__
            if os.path.islink (root):
                root = os.path.realpath (root)
            retarg = os.path.dirname (os.path.abspath (root))
            return retarg
        except:
            print "I'm sorry, but something is wrong."
            print "There is no __file__ variable. Please contact the author."
            sys.exit ()

    lib_om_dir = determine_path()
    if lib_om_dir != sys.path[0]:
        sys.path.insert(0, lib_om_dir)

    run()
