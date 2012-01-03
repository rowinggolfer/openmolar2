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

from PyQt4 import QtCore, QtGui
from lib_openmolar.common.dialogs import BaseDialog

class NewUserPasswordDialog(BaseDialog):
    '''
    gets a user / password by asking them their name
    followed by asking their password twice
    '''
    def __init__(self, parent=None):
        super (NewUserPasswordDialog, self).__init__(parent)
        self.setWindowTitle(_("Add a User"))
        self.setMinimumSize(300,200)
        frame = QtGui.QFrame()
        form = QtGui.QFormLayout(frame)
        self.name_lineEdit = QtGui.QLineEdit()
        self.pass_lineEdit = QtGui.QLineEdit()
        self.repeat_pass_lineEdit = QtGui.QLineEdit()

        self.name_lineEdit.setMaxLength(30)
        self.pass_lineEdit.setMaxLength(30)
        self.repeat_pass_lineEdit.setMaxLength(30)

        self.pass_lineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.repeat_pass_lineEdit.setEchoMode(QtGui.QLineEdit.Password)

        form.addRow("Name",self.name_lineEdit)
        form.addRow("Password",self.pass_lineEdit)
        form.addRow("Confirm Password",self.repeat_pass_lineEdit)

        self.insertWidget(frame)

        self.name_lineEdit.cursorPositionChanged.connect(self._check)
        self.pass_lineEdit.cursorPositionChanged.connect(self._check)
        self.repeat_pass_lineEdit.cursorPositionChanged.connect(self._check)

    def _check(self):
        enable = (self.name_lineEdit.text() != "" and
            self.pass_lineEdit.text() != "" and
            self.repeat_pass_lineEdit.text() != "")

        self.enableApply(enable)

    def getValues(self):
        '''
        will return (True, username, password) if dialog accepted
        or (False, "", "" if not
        '''
        while True:
            if self.exec_():
                errors = []
                name = unicode(self.name_lineEdit.text())
                password = unicode(self.pass_lineEdit.text())
                confirm = unicode(self.repeat_pass_lineEdit.text())

                if name == "":
                    errors.append(_("No Name Entered"))

                if password != confirm:
                    errors.append(_("Passwords didn't match!"))

                if errors:
                    message = u"<body>%s<hr /><ul>" %(
                        _("Please check the following"))
                    for error in errors:
                        message += "<li>%s</li>"% error
                    message += "</ul></body>"
                    QtGui.QMessageBox.warning(self, "Warning", message)
                else:
                    break
            else:
                return (False, "", "")

        return (True, name, password)

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")
    app = QtGui.QApplication([])
    dl = NewUserPasswordDialog()
    print dl.getValues()
    app.closeAllWindows()