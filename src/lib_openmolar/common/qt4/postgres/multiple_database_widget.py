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

from PyQt4 import QtGui, QtCore

class MultipleDatabaseWidget(QtGui.QWidget):
    '''
    A widget which provides enough information for a user to select from a
    number of connections.
    '''
    connection_chosen = QtCore.pyqtSignal(object)

    _connections = []
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.toplabel = QtGui.QLabel(
            _("Choose from these known connections"))
        self.toplabel.setAlignment(QtCore.Qt.AlignCenter)

        self.list_widget = QtGui.QListWidget(self)
        self.list_widget.setAlternatingRowColors(True)

        self.details_browser = QtGui.QTextBrowser()

        frame = QtGui.QFrame(self)
        self.grid_layout = QtGui.QGridLayout(frame)
        self.grid_layout.setMargin(0)

        self.grid_layout.addWidget(self.list_widget, 0, 0)
        self.grid_layout.addWidget(self.details_browser,0, 1)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.toplabel)
        self.layout.addWidget(frame)

        self._load_connections()
        self._connect_signals()

    def sizeHint(self):
        return QtCore.QSize(300,200)

    def _connect_signals(self):
        self.list_widget.itemSelectionChanged.connect(self.selection_changed)

    @property
    def connections(self):
        '''
        return all known connections
        '''
        return self._connections

    def set_connections(self, connections):
        '''
        set known connections (a list of :doc:`ConnectionData` )
        '''
        self._connections = connections
        self._load_connections()

    def _load_connections(self):
        self.list_widget.clear()
        for connection in self.connections:
            description = '%s  '% connection.brief_name
            item = QtGui.QListWidgetItem(description, self.list_widget)
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
        valid_selection, conn_data = self.get_current_selection()
        if not valid_selection:
            message = _("please choose a connection")
        else:
            message = conn_data.to_html()

        self.details_browser.setText(message)
        self.connection_chosen.emit(conn_data)

if __name__ == "__main__":
    import gettext
    gettext.install("")

    from lib_openmolar.common.datatypes import ConnectionData

    app = QtGui.QApplication([])

    dl = QtGui.QDialog()

    cd1, cd2 = ConnectionData(), ConnectionData()
    cd1.demo_connection()
    cd2.demo_connection()

    widg = MultipleDatabaseWidget(dl)
    widg.set_connections([cd1, cd2])

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(widg)

    dl.exec_()
