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

import ConfigParser
import os
import logging

from PyQt4 import QtGui, QtCore
from lib_openmolar.common.dialogs import ExtendableDialog
from lib_openmolar.common.connect.connection_data import ConnectionData
from lib_openmolar.common.connect.edit_known_connections \
    import ChooseConnectionWidget

class ConnectDialog(ExtendableDialog):
    '''
    this dialog will invite the user to enter the parameters required to
    connect to a database
    '''

    _known_connections = None

    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent)

        self.connection = self.default_connection

        self.setWindowTitle(_("Connect to Database"))

        self.enableApply()

        self.choice_widg = ChooseConnectionWidget(self.known_connections, self)

        self.add_advanced_widget(self.choice_widg)

        self.label = QtGui.QLabel()

        self.insertWidget(self.label)

        self.set_label()

        self.connect(self.choice_widg, QtCore.SIGNAL("connection chosen"),
            self.alternate_chosen)

    @property
    def known_connections(self):
        '''
        parse the allowed locations for connections.
        '''
        if self._known_connections is None:
            self._known_connections = []
            parser = ConfigParser.SafeConfigParser()
            for root, dir_, files in os.walk(
                "/home/neil/.openmolar2/connections-enabled"):
                for file_ in files:
                    logging.debug("checking %s for config"% file_)
                    parser.readfp(open(os.path.join(root, file_)))

                    conn = ConnectionData()
                    conn.host = parser.get("CONNECTION", "host", "localhost")
                    conn.port = parser.get("CONNECTION", "port", "5432")
                    conn.db_name = parser.get("CONNECTION", "db_name", "port")
                    conn.username = parser.get("CONNECTION", "user")
                    conn.password = parser.get("CONNECTION", "password")

                    self._known_connections.append(conn)

        return self._known_connections

    @property
    def default_connection(self):
        if self.known_connections:
            default_found = False
            for connection in self.known_connections:
                if connection.is_default:
                    default_found = True
                    break
            if default_found:
                return connection
            return self.known_connections[0]
        else:
            QtGui.QMessageBox.information(self.parent(), _("information"),
            u'<b>%s</b><br/>%s'%(
            _('NO PREVIOUS database details found'),
            _('will default to the demo database on localhost.')))

            connection = ConnectionData()
            connection.demo_connection()
            connection.is_default = True
            self._known_connections = [connection]
            return connection

    def set_label(self):
        header = _('Connect to this database?')

        message = u'''<div align="center">%s</div><ul>
        <li>alias - <b>"%s"</b></li>
        <li>host - <b>%s</b></li>
        <li>port - <b>%s</b></li>
        <li>user - <b>%s</b></li>
        <li>use password - <b>%s</b></li>
        <li>database - <b>%s</b></li></ul>'''% (header,
            self.connection.human_name,
            self.connection.host,
            self.connection.port,
            self.connection.username,
            _("YES") if self.connection.password !="" else _("NO"),
            self.connection.db_name)

        self.label.setText(message)

    def sizeHint(self):
        return QtCore.QSize(400,150)

    def load_connections(self, connections):
        self.known_connections = connections
        self.set_label()

    def alternate_chosen(self, connection):
        self.connection = connection
        self.set_label()
        QtCore.QTimer.singleShot(2000, self.more_but.click)

    @property
    def chosen_connection(self):
        return self.connection

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")

    app = QtGui.QApplication([])
    dl = ConnectDialog()
    if dl.exec_():
        print dl.chosen_connection
    app.closeAllWindows()
