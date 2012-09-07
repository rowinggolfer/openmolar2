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

import logging
import types

from PyQt4 import QtGui, QtCore
from lib_openmolar.common.datatypes import ConnectionData

from lib_openmolar.common.qt4.dialogs import ExtendableDialog

from multiple_database_widget import MultipleDatabaseWidget

class ConnectDialog(ExtendableDialog):
    '''
    this dialog will invite the user to enter the parameters required to
    connect to a database
    '''

    _known_connections = []
    _chosen_index = 0

    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent)

        self.setWindowTitle(_("Connect to Database"))

        self.enableApply()

        self.multiple_db_widg = MultipleDatabaseWidget(self)

        self.add_advanced_widget(self.multiple_db_widg)

        self.label = QtGui.QLabel()

        self.insertWidget(self.label)

        self.set_advanced_but_text(_("other databases"))

    def _connect_signals(self):
        self.multiple_db_widg.connection_chosen.connect(self.alternate_chosen)

    @property
    def known_connections(self):
        '''
        returns a list of type :doc:`ConnectionData`
        '''
        return self._known_connections

    def set_known_connections(self, connections):
        '''
        set connections
        '''
        logging.debug("setting known connections")
        assert type(connections) == types.ListType, "connections must be list"
        for conn_data in connections:
            logging.debug(conn_data)
            assert type(conn_data) == ConnectionData, "connection type unknown"

        self._known_connections = connections
        self.multiple_db_widg.set_connections(connections)

    @property
    def connection(self):
        if not self.known_connections:
            QtGui.QMessageBox.information(self.parent(), _("information"),
            u'<b>%s</b><br/>%s'%(
            _('NO database details found'),
            _('will offer connection to the demo database on localhost.')))

            conn_data = ConnectionData()
            conn_data.demo_connection()
            self._known_connections = [conn_data]
            return conn_data

        return self.known_connections[self._chosen_index]

    def _clicked(self, but):
        '''
        Overwrite :doc:`ExtendableDialog` function to enable the active widget
        '''
        self.multiple_db_widg.setEnabled(True)
        ExtendableDialog._clicked(self, but)

    def set_label(self):
        header = _('Connect to this database?')

        message = u'<div align="center"><b>%s</b></div><ul>%s'% (header,
            self.connection.to_html())

        self.label.setText(message)

    def sizeHint(self):
        return QtCore.QSize(400,150)

    def alternate_chosen(self, conn_data):
        if QtGui.QMessageBox.question(self, _("Confirm"),
            u"%s %s" %(_("use connection"), conn_data.brief_name),
            QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
            QtGui.QMessageBox.Ok) == QtGui.QMessageBox.Ok:
            self._chosen_index = self.known_connections.index(conn_data)

            self.set_label()
            self.multiple_db_widg.setEnabled(False)
            QtCore.QTimer.singleShot(500, self.more_but.click)

    @property
    def chosen_connection(self):
        return self.connection

    def exec_(self):
        self.set_label()
        self._connect_signals()
        return ExtendableDialog.exec_(self)

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")

    app = QtGui.QApplication([])

    dl = ConnectDialog()

    cd1, cd2 = ConnectionData(), ConnectionData()
    cd1.demo_connection()
    cd2.demo_connection()
    cd2._connection_name = "alternate"
    dl.set_known_connections([cd1, cd2])

    if dl.exec_():
        print dl.chosen_connection
    app.closeAllWindows()
