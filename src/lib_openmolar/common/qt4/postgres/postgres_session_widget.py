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

from lib_openmolar.common.datatypes import ConnectionData
from openmolar_database import ConnectionError, OpenmolarDatabase

class PostgresSessionWidget(QtGui.QWidget):
    
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.pg_session = None
        '''pointer to the QtSqlQDatabase'''
        self.setup_ui()

    def setup_ui(self):
        layout = QtGui.QVBoxLayout(self)
        self.label1 = QtGui.QLabel("brief")
        self.label2 = QtGui.QLabel("verbose")
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)

    def sizeHint(self):
        return QtCore.QSize(400,300)

    def closeEvent(self, event=None):
        if self.is_connected:
            if QtGui.QMessageBox.question(self, _("confirm"),
            _("End database Session?"),
            QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
            QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Cancel:
                event.ignore()
                return
            self.pg_session.close()
        QtGui.QWidget.closeEvent(self, event)

    def set_session(self, session):
        assert OpenmolarDatabase in session.__class__.__mro__
        self.pg_session = session

    def get_session_status(self):
        '''
        returns a tuple, (brief, verbose)
        '''
        if self.pg_session is None:
            return "No session", "No session"
        name = self.pg_session.databaseName()
        host = self.pg_session.hostName()
        port = self.pg_session.port()

        if self.pg_session.isOpen():
            verbose = u"%s '%s' %s %s@%s:%s"% (
                _("Connected as "),  self.pg_session.userName(),
                _("to"), name,
                host, port)

            brief = "'%s' %s:%s" %(name, host, port)
        else:
            verbose = verbose = u"%s %s %s:%s %s"% (
                _("NOT CONNECTED TO"), name,
                host, port, self.pg_session.lastError().text())
            brief = "%s '%s' %s:%s" %(_("NOT CONNECTED"), name, host, port)

        return brief, verbose

    def update_status(self):
        '''
        let the user know the connection state
        '''
        brief, verbose = self.get_session_status()
        self.label1.setText(brief)
        self.label2.setText(verbose)

    @property
    def is_connected(self):
        '''
        does this widget have an open connection to a postgres database?
        '''
        return self.pg_session and self.pg_session.isOpen()

def _test():
    app = QtGui.QApplication([])
    conn_data = ConnectionData()
    conn_data.demo_connection()
    session = OpenmolarDatabase(conn_data)
    session.connect()
    psw = PostgresSessionWidget()
    psw.set_session(session)
    psw.update_status()
    psw.show()
    app.exec_()

if __name__ == "__main__":
    import __builtin__
    import logging
    __builtin__.LOGGER = logging.getLogger()

    from lib_openmolar.common.settings import CommonSettings
    SETTINGS = CommonSettings()

    import gettext
    gettext.install("openmolar")
    _test()
