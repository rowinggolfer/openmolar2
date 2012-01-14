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

from PyQt4 import QtGui, QtCore

if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.abspath("../../"))
    print sys.path

from lib_openmolar.common.qt4.widgets.password_lineedit import PasswordLineEdit
from lib_openmolar.common.dialogs import BaseDialog
from lib_openmolar.common.connect.connection_data import ConnectionData

class NewConnectionDialog(BaseDialog):
    '''
    allow an additional database to be added to the stored list
    '''
    def __init__(self, parent=None):
        super(NewConnectionDialog, self).__init__(parent)
        self.setWindowTitle(_("Connection"))

        self.label = QtGui.QLabel(u"<b>%s</b>"% _(
        'Enter New Connection'), self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.humanname_edit = QtGui.QLineEdit(self)
        self.username_edit = QtGui.QLineEdit(self)
        self.password_edit = PasswordLineEdit(self)
        self.host_edit = QtGui.QLineEdit(self)
        self.port_edit = QtGui.QLineEdit(self)
        self.db_name_edit = QtGui.QLineEdit(self)


        frame = QtGui.QFrame(self)
        form = QtGui.QFormLayout(frame)
        form.addRow(_("ALIAS (eg. 'main server')"), self.humanname_edit)
        form.addRow(_("Username"), self.username_edit)
        form.addRow(_("Password"), self.password_edit)
        form.addRow(_("Host"), self.host_edit)
        form.addRow(_("Port (default is 5432)"), self.port_edit)
        form.addRow(_("Database Name"), self.db_name_edit)


        self.layout.insertWidget(0, self.label)
        self.layout.insertWidget(1, frame)
        #self.layout.insertWidget(2, self.default_checkbox)

        self.username_edit.setFocus()
        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(400,300)

    @property
    def toConnectionData(self):
        '''
        returns a ConnectionData object
        '''
        cd = ConnectionData(
            human_name=self.human_name,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            db_name=self.db_name)
        return cd

    @property
    def human_name(self):
        return unicode(self.humanname_edit.text())
    @property
    def username(self):
        return unicode(self.username_edit.text())

    @property
    def password(self):
        return unicode(self.password_edit.text())

    @property
    def host(self):
        return unicode(self.host_edit.text())

    @property
    def port(self):
        return self.port_edit.text().toInt()[0]

    @property
    def db_name(self):
        return unicode(self.db_name_edit.text())


class EditConnectionDialog(NewConnectionDialog):
    def __init__(self, parent=None):
        super(EditConnectionDialog, self).__init__(parent)
        self.label.setText(_("Edit connection"))

    def fromConnectionData(self, cd):
        '''
        loads ConnectionData object (for editing)
        '''
        self.humanname_edit.setText(cd.human_name)
        self.username_edit.setText(cd.username)
        self.password_edit.setText(cd.password)
        self.host_edit.setText(cd.host)
        self.port_edit.setText(unicode(cd.port))
        self.db_name_edit.setText(cd.db_name)


if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")

    app = QtGui.QApplication([])
    dl = NewConnectionDialog()
    if dl.exec_():
        print dl.toConnectionData
    app.closeAllWindows()
