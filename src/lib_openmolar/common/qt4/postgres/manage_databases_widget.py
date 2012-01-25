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

from new_connection_dialog import NewConnectionDialog
from edit_connection_dialog import EditConnectionDialog
from multiple_database_widget import MultipleDatabaseWidget

class ManageDatabasesWidget(MultipleDatabaseWidget):
    '''
    a widget, added at runtime to the preferences dialog.
    '''
    def __init__(self, parent):
        MultipleDatabaseWidget.__init__(self, parent)

        self.toplabel.setText(_("Known connections"))
        self.bottomlabel.hide() #setText("")

        self.new_but = QtGui.QPushButton(_("Enter a New Connection"))

        self.edit_button = QtGui.QPushButton(_("Edit this connection"))
        self.del_button = QtGui.QPushButton(_("Delete this connection"))

        self.grid_layout.addWidget(self.list_widget, 0, 0, 4, 1)
        self.grid_layout.addWidget(self.details_browser,0, 1)
        self.grid_layout.addWidget(self.edit_button, 1, 1)
        self.grid_layout.addWidget(self.del_button, 2, 1)

        line = QtGui.QFrame(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Fixed)
        line.setSizePolicy(sizePolicy)
        line.setMinimumSize(QtCore.QSize(0, 16))
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)

        self.layout.addWidget(line)
        self.layout.addWidget(self.new_but)
        self.connect_signals()

    def sizeHint(self):
        return QtCore.QSize(500,300)

    def connect_signals(self):
        self.new_but.clicked.connect(self.new_connection)
        self.edit_button.clicked.connect(self.edit_connection)
        self.del_button.clicked.connect(self._delete_connection)

    def new_connection(self):
        dl = NewConnectionDialog(self.parent())
        if dl.exec_():
            connection = dl.toConnectionData
            self.connections.append(connection)
            self._load_connections()
            self.emit(QtCore.SIGNAL("connections changed"),
                self.connections)
            self.list_widget.setCurrentRow(len(self.connections)-1)

    def edit_connection(self):
        valid_selection, conn_data = self.get_current_selection()
        if not valid_selection:
            return
        dl = EditConnectionDialog(conn_data, self)
        if dl.exec_():
            i = self.list_widget.currentRow()
            self.emit(QtCore.SIGNAL("connections changed"), self.connections)
            self._load_connections()
            self.list_widget.setCurrentRow(i)

    def _delete_connection(self):
        valid_selection, conn_data = self.get_current_selection()
        if not valid_selection:
            return
        if QtGui.QMessageBox.question(self, _("Question"),
        u"%s '%s'?"% (_("Delete connection"), conn_data.brief_name),
        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Ok:
            try:
                os.remove(conn_data.conf_file)
            except Exception as exc:
                QtGui.QMessageBox.warning(self, _("error"),
                   u"%s %s"% (_("Unable to remove file"), conn_data.conf_file))
                return

            self.connections.remove(connection)
            self.emit(QtCore.SIGNAL("connections changed"), self.connections)
            self._load_connections()

if __name__ == "__main__":
    import gettext

    def advise(*args):
        print args

    from lib_openmolar.common.datatypes import ConnectionData

    app = QtGui.QApplication([])

    gettext.install("")

    dl = QtGui.QDialog()
    dl.advise = advise

    cd1, cd2 = ConnectionData(), ConnectionData()
    cd1.demo_connection()
    cd2.demo_connection()

    cd1.is_default = True
    obj = ManageDatabasesWidget(dl)
    obj.set_connections([cd1, cd2])

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(obj)

    dl.exec_()
