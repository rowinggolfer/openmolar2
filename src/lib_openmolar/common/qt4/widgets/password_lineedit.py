#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
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

from PyQt4 import QtGui

class PasswordLineEdit(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.line_edit = QtGui.QLineEdit(self)
        self.line_edit.setEchoMode(QtGui.QLineEdit.Password)

        self.text = self.line_edit.text
        self.setText = self.line_edit.setText

        self.check_box = QtGui.QCheckBox(_("show"), self)
        self.check_box.toggled.connect(self.show_password)

        layout = QtGui.QHBoxLayout(self)

        layout.setMargin(0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.check_box)

    def show_password(self, val):
        if val:
            self.line_edit.setEchoMode(QtGui.QLineEdit.Normal)
        else:
            self.line_edit.setEchoMode(QtGui.QLineEdit.Password)

if __name__ == "__main__":
    import gettext
    gettext.install("")

    app = QtGui.QApplication([])
    obj = PasswordLineEdit()
    obj.show()
    app.exec_()
