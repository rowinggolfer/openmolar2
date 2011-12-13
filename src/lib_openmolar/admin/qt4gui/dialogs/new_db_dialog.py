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

import re
from PyQt4 import QtCore, QtGui

from lib_openmolar.common.dialogs import ExtendableDialog

class NewDatabaseDialog(ExtendableDialog):
    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent)

        self.setWindowTitle(_("New Database"))

        label = QtGui.QLabel("<b>%s %s %s</b>"% (
        _('You are about to install a new database'),
        _("(correctly called a 'schema')"),
        _("onto your postgresql server")))
        label.setWordWrap(True)

        label1 = QtGui.QLabel(_("Please enter a name for this new database"))
        label1.setWordWrap(True)

        self.lineedit = QtGui.QLineEdit()

        self.insertWidget(label)
        self.insertWidget(label1)
        self.insertWidget(self.lineedit)

        advanced_label = QtGui.QLabel("no advanced options as yet")

        self.add_advanced_widget(advanced_label)

        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    @property
    def database_name(self):
        '''
        the name the user has enetered
        '''
        return unicode(self.lineedit.text()).strip(" ")

    def set_database_name(self, name):
        '''
        set the name the user has enetered
        '''
        self.lineedit.setText(name)

    def exec_(self):
        while True:
            if ExtendableDialog.exec_(self):
                if self.database_name == "":
                    QtGui.QMessageBox.warning(self, _("Error"),
                    _("Please enter a name for this new database"))
                elif " " in self.database_name:
                    QtGui.QMessageBox.warning(self, _("Error"),
                    _("Database names cannot contain spaces"))
                else:
                    break
            else:
                return False

        return True

if __name__ == "__main__":
    from gettext import gettext as _

    app = QtGui.QApplication([])

    dl = NewDatabaseDialog()

    dl.exec_()
