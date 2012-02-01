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
import os
import sys
from PyQt4 import QtGui, QtCore

from lib_openmolar.common import SETTINGS
from lib_openmolar.common.datatypes import ConnectionData

from lib_openmolar.common.qt4.widgets import (
    RestorableApplication,
    BaseMainWindow,
    Preference,
    PreferencesDialog)

from connect_dialog import ConnectDialog
from postgres_database import ConnectionError, PostgresDatabase
from manage_databases_widget import ManageDatabasesWidget
#from new_connection_dialog import NewUserPasswordDialog, UserPasswordDialog

class PostgresMainWindow(BaseMainWindow):
    '''
    A main window with functions to connect to postgres
    '''
    _preferences_dialog = None
    _connection_dialog = None
    _known_connections = None
    CONN_CLASS = PostgresDatabase

    def __init__(self, parent=None):
        BaseMainWindow.__init__(self, parent)
        self.setMinimumSize(600, 400)

        self.setWindowTitle("%s (%s)"% (
            _("Postgres Application"), _("OFFLINE")))

        ## Main Menu

        ## "file"

        icon = QtGui.QIcon(":icons/postgresql_elephant.svg")
        self.action_connect = QtGui.QAction(icon, _("Begin Session"), self)
        self.action_connect.setToolTip(_("Start a PostgreSQL session"))

        icon = QtGui.QIcon(":icons/no_postgresql_elephant.svg")
        self.action_disconnect = QtGui.QAction(icon, _("End Session"), self)
        self.action_disconnect.setToolTip(_("End a PostgreSQL session"))

        insertpoint = self.action_quit
        self.menu_file.insertAction(insertpoint, self.action_connect)
        self.menu_file.insertAction(insertpoint,self.action_disconnect)
        self.menu_file.insertSeparator(insertpoint)

        insertpoint = self.action_help
        self.main_toolbar.insertAction(insertpoint, self.action_connect)
        self.main_toolbar.insertAction(insertpoint, self.action_disconnect)
        self.main_toolbar.insertSeparator(insertpoint)

        ####       now load stored settings                                ####
        self.loadSettings()

        self.connection = None

        mock_widget = QtGui.QLabel("postgres app")
        mock_widget.setAlignment(QtCore.Qt.AlignCenter)
        self.setCentralWidget(mock_widget)

        self.action_connect.triggered.connect(self.start_pg_session)
        self.action_disconnect.triggered.connect(self.end_pg_session)

        QtCore.QTimer.singleShot(100, self.setBriefMessageLocation)

    @property
    def known_connections(self):
        '''
        parse the allowed locations for connections.
        '''
        if self._known_connections is None:
            self._known_connections = []
            try:
                settings = QtCore.QSettings()
                conf_dir = str(
                    settings.value("connection_conf_dir").toString())
                #conf_dir = "/etc/openmolar/client-connections"
                LOGGER.debug("checking %s for connection config files")
                for root, dir_, files in os.walk(conf_dir):
                    for file_ in sorted(files):
                        filepath = os.path.join(root, file_)
                        LOGGER.debug("checking %s for config"% filepath)

                        conn_data = ConnectionData()
                        conn_data.get_password = self.get_password
                        conn_data.from_conf_file(filepath)

                        LOGGER.info("loaded connection %s"% conn_data)
                        self._known_connections.append(conn_data)
            except Exception:
                LOGGER.exception("error getting known_connections")

        return self._known_connections

    def get_password(self, prompt):
        '''
        raise a dialog to get a password
        '''
        password, result = QtGui.QInputDialog.getText(self,
        _("password required"), prompt, QtGui.QLineEdit.Password)
        if result is None:
            logging.WARNING("password dialog cancelled by user")
        return unicode(password)

    @property
    def connection_dialog(self):
        if self._connection_dialog is None:
            self._connection_dialog = ConnectDialog(self)
            self._connection_dialog.set_known_connections(
                self.known_connections)

        return self._connection_dialog

    def start_pg_session(self):
        '''
        connect to postgres
        '''
        LOGGER.debug("%s.start_pg_session"% __file__)
        dl = self.connection_dialog
        while True:
            if not dl.exec_():
                return
            self.end_pg_session()
            conn_data = dl.chosen_connection

            self.connection = self.CONN_CLASS(conn_data)
            if self.attempt_connection():
                break

        self._can_connect()

    def attempt_connection(self):
        '''
        attempt to connect (ie. call QSqlDatabase.connect())
        '''
        LOGGER.info(u"%s '%s'"% (_("Attempting connection using data"),
            self.connection.connection_data))

        try:
            self.connection.connect()
            self.connect(QtGui.QApplication.instance(),
                QtCore.SIGNAL("Query Error"), self.advise_dl)
            return True
        except ConnectionError as error:
            self.advise(u"%s<hr />%s"% (
                _("Connection Error"), error), 2)
            LOGGER.exception("Connection Error")
        return False

    def end_pg_session(self):
        '''
        disconnect from postgres server
        (if not connected - pass quietly).
        '''
        if self.connection:
            if self.connection.isOpen():
                self.connection.close()
                self.connection = None
                LOGGER.info("DISCONNECTED")
            self.connection = None
        self._can_connect()

    def _can_connect(self):
        '''
        toggles the connect buttons/menu actions
        '''
        connected = self._connection_status()
        self.action_connect.setEnabled(not connected)
        self.action_disconnect.setEnabled(connected)

    def _connection_status(self):
        '''
        updates the status bar
        (called after connect/disconnect or database specified)
        '''
        if self.has_pg_connection:

            name = self.connection.databaseName()
            host = self.connection.hostName()
            port = self.connection.port()

            message = u"%s '%s' %s %s@%s:%s"% (
                _("Connected to Database"), name,
                _("using"), self.connection.userName(),
                host, port)
            self.advise(message)

            message = message.replace("<br />", "")
            self.status_label.setText(message)

            connection_metadata = "'%s' %s:%s" %(name, host, port)
            result = True
            LOGGER.info(message)
        else:
            self.status_label.setText(_("Not Connected to a database"))
            connection_metadata = _("OFFLINE")
            result = False
        try:
            title_ = unicode(self.windowTitle())
            title_ = re.sub("\(.*\)", "(%s)"% connection_metadata, title_)
            self.setWindowTitle(title_)
        except ValueError as exc:
            LOGGER.debug("unable to alter window title %s"% exc)

        return result

    @property
    def has_pg_connection(self):
        '''
        returns a bool which states if the database connection is open.
        '''
        return self.connection and self.connection.isOpen()

    def get_user_pass(self, dbname):
        '''
        return a tuple of result user, password
        '''
        LOGGER.debug("%s.get_user_pass %s"% (__file__, dbname))
        if dbname == "openmolar_demo":
            return (True, "om_demo", "password")
        dl = UserPasswordDialog(self)
        return dl.exec_(), dl.name, dl.password

    def closeEvent(self, event=None):
        '''
        re-implement the close event of QtGui.QMainWindow, and check the user
        really meant to do this.
        '''
        self.saveSettings()
        self.end_pg_session()

    def preferences_dialog(self):
        if self._preferences_dialog is None:
            dl = self._preferences_dialog = PreferencesDialog(self)

            connections_pref = Preference(_("Database Connections"))

            m_d_widg = ManageDatabasesWidget(self)
            m_d_widg.set_connections(self.known_connections)
            connections_pref.setWidget(m_d_widg)
            dl.insert_preference_dialog(0, connections_pref)

        return self._preferences_dialog

    def show_preferences_dialog(self):
        '''
        user wishes to launch the preferences dialog
        '''
        LOGGER.debug("launching preference dialog")
        self.preferences_dialog().exec_()

def _test():

    app = RestorableApplication("openmolar-test-suite")
    settings = QtCore.QSettings()
    settings.setValue("connection_conf_dir",
        "/etc/openmolar/client-connections")

    mw = PostgresMainWindow()
    mw.show()
    app.exec_()

if __name__ == "__main__":
    import logging
    LOGGER = logging.getLogger()

    import gettext
    gettext.install("openmolar")
    _test()
