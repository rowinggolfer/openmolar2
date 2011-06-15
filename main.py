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

from PyQt4 import QtGui, QtCore

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

def run_admin():
    print "running admin app as process %s"%(
    subprocess.Popen(["python", "admin_app.py"]).pid)

def run_client():
    print "running client app as process %s"%(
    subprocess.Popen(["python", "client_app.py"]).pid)

def run():
    '''
    main function
    '''
    from lib_openmolar.common.dialogs import BaseDialog

    class ChoiceDialog(BaseDialog):
        def __init__(self, parent=None):
            super (ChoiceDialog, self).__init__(parent)
            self.setWindowTitle(_("OpenMolar2 Control Panel"))
            self.setMinimumSize(300, 200)
            message = u"%s<br />%s"% (
            _("Please select which application to run."),
            _("Or be brave, and run both!"))

            label = QtGui.QLabel(message)
            label.setMinimumHeight(50)
            label.setAlignment(QtCore.Qt.AlignCenter)

            self.client_checkbox = QtGui.QCheckBox(_("Client"), self)
            self.admin_checkbox = QtGui.QCheckBox(_("Admin Tools"), self)

            self.insertWidget(label)
            self.insertWidget(self.client_checkbox)
            self.insertWidget(self.admin_checkbox)

            self.client_checkbox.toggled.connect(self._check)
            self.admin_checkbox.toggled.connect(self._check)

        def _check(self):
            '''
            if user has selected one or both guis.. enable the apply button
            '''
            self.enableApply(self.client_checkbox.isChecked() or
                self.admin_checkbox.isChecked())

    app = QtGui.QApplication(sys.argv)
    dl = ChoiceDialog()
    if dl.exec_():
        if dl.admin_checkbox.isChecked():
            run_admin()
        if dl.client_checkbox.isChecked():
            run_client()
    else:
        sys.exit(app.closeAllWindows())
    app.closeAllWindows()
    app = None
    sys.exit()

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

    os.chdir(os.path.join(determine_path(), "src"))
    print sys.path
    run()
