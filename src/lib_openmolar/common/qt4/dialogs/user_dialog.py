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
from lib_openmolar.common.qt4.dialogs import BaseDialog

class UserPasswordDialog(BaseDialog):
    '''
    a dialog which gets a username and password
    '''
    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Input Required"))
        frame = QtGui.QFrame()
        form = QtGui.QFormLayout(frame)
        self.name_lineEdit = QtGui.QLineEdit()
        self.pass_lineEdit = QtGui.QLineEdit()

        self.name_lineEdit.setMaxLength(30)
        self.pass_lineEdit.setMaxLength(30)

        self.pass_lineEdit.setEchoMode(QtGui.QLineEdit.Password)

        form.addRow(_("Name"),self.name_lineEdit)
        form.addRow(_("Password"),self.pass_lineEdit)

        self.insertWidget(frame)

        self.name_lineEdit.cursorPositionChanged.connect(self._check)

    def sizeHint(self):
        return QtCore.QSize(300,150)

    def _check(self):
        self.enableApply(self.name_lineEdit.text() != "")

    def set_name(self, name):
        self.name_lineEdit.setText(name)
        self._check()

    @property
    def name(self):
        return unicode(self.name_lineEdit.text())

    @property
    def password(self):
        return unicode(self.pass_lineEdit.text())


if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")
    app = QtGui.QApplication([])
    dl = UserPasswordDialog()
    if dl.exec_():
        print dl.name, dl.password
    app.closeAllWindows()