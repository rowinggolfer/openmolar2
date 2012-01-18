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

from lib_openmolar.common.qt4.dialogs import ExtendableDialog

class ManageDatabaseDialog(ExtendableDialog):

    manage_users = False
    drop_db = False

    def __init__(self, dbname, parent=None):
        ExtendableDialog.__init__(self, parent)

        self.dbname = dbname
        self.setWindowTitle(u"%s %s"% (_("Manage Database"), dbname))

        label = QtGui.QLabel("<b>%s</b>"% (
            _('The following options can be performed.')))
        label.setWordWrap(True)

        drop_but = QtGui.QPushButton(_("Drop (delete) this database"))
        users_but = QtGui.QPushButton(_("Manage users for this database"))

        self.insertWidget(label)
        self.insertWidget(drop_but)
        self.insertWidget(users_but)

        advanced_label = QtGui.QLabel("no advanced options as yet")

        self.add_advanced_widget(advanced_label)

        self.apply_but.hide()
        #self.enableApply()

        drop_but.clicked.connect(self.drop_but_clicked)
        users_but.clicked.connect(self.users_but_clicked)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def drop_but_clicked(self):
        if QtGui.QMessageBox.question(self, _("Confirm"),
        u"%s '%s'?<br /><b>%s</b>"% (
            _("Drop Database"),
            self.dbname,
        _   ("This operation cannot be undone!")),
        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Ok:
            self.drop_db = True
            self.accept()

    def users_but_clicked(self):
        self.manage_users = True
        self.accept()

def _test():
    app = QtGui.QApplication([])
    dl = ManageDatabaseDialog("foo")
    dl.exec_()

if __name__ == "__main__":
    from gettext import gettext as _
    _test()
