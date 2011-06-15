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

from lib_openmolar.common.connect.new_connection_dialog import (
    NewConnectionDialog,
    EditConnectionDialog)


class ChooseConnectionWidget(QtGui.QWidget):
    def __init__(self, connections, parent=None):
        super(ChooseConnectionWidget, self).__init__(parent)

        self.toplabel = QtGui.QLabel(
            _("Choose from these known connections"))
        self.toplabel.setAlignment(QtCore.Qt.AlignCenter)

        self.list_widget = QtGui.QListWidget(self)
        self.list_widget.setAlternatingRowColors(True)

        self.details_browser = QtGui.QTextBrowser()

        self.bottomlabel = QtGui.QLabel(
            _('''To add, edit or delete connections,
go to edit-> preferences -> database connections'''))
        self.bottomlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.bottomlabel.setWordWrap(True)

        frame = QtGui.QFrame(self)
        self.grid_layout = QtGui.QGridLayout(frame)
        self.grid_layout.setMargin(0)

        self.grid_layout.addWidget(self.list_widget, 0, 0)
        self.grid_layout.addWidget(self.details_browser,0, 1)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.toplabel)
        self.layout.addWidget(frame)
        self.layout.addWidget(self.bottomlabel)

        self.connections = connections
        self._load_connections()
        self._connect_signals()

    def sizeHint(self):
        return QtCore.QSize(300,200)

    def _connect_signals(self):
        self.list_widget.itemSelectionChanged.connect(self.selection_changed)

    def _load_connections(self):
        self.list_widget.clear()
        for connection in self.connections:
            description = '%s  '% connection.human_name
            if connection.is_default:
                description += _("(default)")
            item = QtGui.QListWidgetItem(description, self.list_widget)
            if connection.is_default:
                self.list_widget.setCurrentItem(item)
        if self.list_widget.currentRow() == -1:
            self.list_widget.setCurrentRow(0)

        self.selection_changed()

    def get_current_selection(self):
        i = self.list_widget.currentRow()
        valid_selection = (i != -1)
        if self.list_widget.count() >0 and not valid_selection:
            QtGui.QMessageBox.warning(self, _("error"),
            _("No connection selected"))

        try:
            connection = self.connections[i]
        except IndexError:
            valid_selection = False
            connection = None
        return (valid_selection, connection)

    def selection_changed(self):
        valid_selection, connection = self.get_current_selection()
        if not valid_selection:
            message = _("please choose a connection")
        else:
            message = u'''<h2>%s</h2>
        <table width="100%%" border="1">
        <tr><td>host</td><td><b>%s</b></td></tr>
        <tr><td>port</td><td><b>%s</b></td></tr>
        <tr><td>user</td><td><b>%s</b></td></tr>
        <tr><td>password</td><td><b>%s</b></td></tr>
        <tr><td>database</td><td><b>%s</b></td></tr></table>'''% (
            connection.human_name,
            connection.host,
            connection.port,
            connection.username,
            ("*" * len(connection.password)),
            connection.db_name)

        self.details_browser.setText(message)
        self.emit(QtCore.SIGNAL("connection chosen"), connection)

class ConnectionsPreferenceWidget(ChooseConnectionWidget):
    '''
    a widget, added at runtime to the preferences dialog.
    '''
    def __init__(self, connections, parent):
        ChooseConnectionWidget.__init__(self, connections, parent)

        self.toplabel.setText(_("Known connections"))
        self.bottomlabel.hide() #setText("")

        self.new_but = QtGui.QPushButton(_("Enter a New Connection"))

        self.edit_button = QtGui.QPushButton(_("Edit this connection"))
        self.del_button = QtGui.QPushButton(_("Forget this connection"))
        self.default_button = QtGui.QPushButton(_("Set as default connection"))

        self.grid_layout.addWidget(self.list_widget, 0, 0, 4, 1)
        self.grid_layout.addWidget(self.details_browser,0, 1)
        self.grid_layout.addWidget(self.edit_button, 1, 1)
        self.grid_layout.addWidget(self.del_button, 2, 1)
        self.grid_layout.addWidget(self.default_button, 3, 1)

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
        self.default_button.clicked.connect(self._default_connection)


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
        valid_selection, connection = self.get_current_selection()
        if not valid_selection:
            return
        dl = EditConnectionDialog(self.parent())
        dl.fromConnectionData(connection)
        if dl.exec_():
            i = self.list_widget.currentRow()
            self.connections[i] = dl.toConnectionData
            self.emit(QtCore.SIGNAL("connections changed"), self.connections)
            self._load_connections()
            self.list_widget.setCurrentRow(i)

    def _delete_connection(self):
        valid_selection, connection = self.get_current_selection()
        if not valid_selection:
            return
        if QtGui.QMessageBox.question(self, _("Question"),
        _("Delete this connection?"),
        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Ok:

            self.connections.remove(connection)
            self.emit(QtCore.SIGNAL("connections changed"), self.connections)
            self._load_connections()

    def _default_connection(self):
        valid_selection, connection = self.get_current_selection()
        if not valid_selection:
            return

        for conn in self.connections:
            conn.is_default = False
        connection.is_default = True

        self.emit(QtCore.SIGNAL("connections changed"),self.connections)

        self._load_connections()



if __name__ == "__main__":
    import gettext

    def advise(*args):
        print args

    from connection_data import ConnectionData

    app = QtGui.QApplication([])

    gettext.install("")

    dl = QtGui.QDialog()
    dl.advise = advise

    cd1, cd2 = ConnectionData(), ConnectionData()
    cd1.demo_connection()
    cd2.demo_connection()

    cd1.is_default = True
    obj = ChooseConnectionWidget([cd1, cd2], dl)

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(obj)

    dl.exec_()