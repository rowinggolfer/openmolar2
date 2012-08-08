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

from lib_openmolar.common.datatypes import ConnectionData

from lib_openmolar.common.qt4.widgets import RestorableApplication, Preference

from lib_openmolar.common.qt4.plugin_tools import PlugableMainWindow
    

from connect_dialog import ConnectDialog
from openmolar_database import ConnectionError, OpenmolarDatabase
from manage_databases_widget import ManageDatabasesWidget
from postgres_session_widget import PostgresSessionWidget

from lib_openmolar.common.qt4.dialogs import UserPasswordDialog

class PostgresMainWindow(PlugableMainWindow):
    '''
    A main window with functions to connect to postgres
    '''
    _central_widget = None
    _preferences_dialog = None
    _connection_dialog = None
    _known_session_params = None
    CONN_CLASS = OpenmolarDatabase

    #: True if more than one pg session is allowed (False for client)
    ALLOW_MULTIPLE_SESSIONS = True

    def __init__(self, parent=None):
        PlugableMainWindow.__init__(self, parent)
        self.setMinimumSize(600, 400)

        self.setWindowTitle(_("Postgres Application"))

        ## Main Menu

        ## "file"

        icon = QtGui.QIcon(":icons/postgresql_elephant.svg")
        self.action_connect = QtGui.QAction(icon, _("Begin Session"), self)
        self.action_connect.setToolTip(_("Start a PostgreSQL session"))

        icon = QtGui.QIcon(":icons/no_postgresql_elephant.svg")
        self.action_disconnect = QtGui.QAction(icon, _("End Session(s)"), self)
        self.action_disconnect.setToolTip(_("End all PostgreSQL sessions"))

        insertpoint = self.action_quit
        self.menu_file.insertAction(insertpoint, self.action_connect)
        self.menu_file.insertAction(insertpoint,self.action_disconnect)
        self.menu_file.insertSeparator(insertpoint)

        #:
        self.main_toolbar.insertAction(insertpoint, self.action_connect)
        self.main_toolbar.insertAction(insertpoint, self.action_disconnect)
        #self.addToolBar(self.session_toolbar)

        ####       now load stored settings                                ####
        self.loadSettings()

        self.action_connect.triggered.connect(self.new_pg_session)
        self.action_disconnect.triggered.connect(self.end_pg_sessions)

        QtCore.QTimer.singleShot(100, self.setBriefMessageLocation)

        self.session_widgets = []

        self.setCentralWidget(self.central_widget)

        self.update_session_status()

    @property
    def central_widget(self):
        '''
        should be Overwritten
        the central widget should have functions frequently associated with
        a tab widget.
        namely addTab etc..
        '''
        if self._central_widget is None:
            LOGGER.debug("PostgresMainWindow.. creating central widget")
            self._central_widget = QtGui.QTabWidget()
            self._central_widget.add = self._central_widget.addTab
            self._central_widget.remove = self._central_widget.removeTab
        return self._central_widget

    @property
    def new_session_widget(self):
        '''
        return a widget (of type :doc:`PostgresSessionWidget` )
        single-session widgets should return the existing session widget.
        multi-session clients should return a new widget
        (and keep a reference to it)
        '''
        return PostgresSessionWidget()

    def add_session(self, session):
        '''
        get self.new_session_widget give it the session and to the ui.

        .. note::
            returns whatever self.new_session_widget created so that calling
            functions have a reference to it.

        '''
        widg = self.new_session_widget
        widg.set_session(session)
        self.session_widgets.append(widg)
        self.central_widget.add(widg, widg.pg_session.description)
        return widg

    @property
    def known_session_params(self):
        '''
        parse the allowed locations for connections.
        returns a list of :doc:`ConnectionData`
        '''
        if self._known_session_params is None:
            self._known_session_params = []
            try:
                conf_dir = str(QtCore.QSettings().value(
                    "connection_conf_dir").toString())

                LOGGER.debug(
                    "checking %s for connection config files"% conf_dir)

                for root, dir_, files in os.walk(conf_dir):
                    for file_ in sorted(files):
                        filepath = os.path.join(root, file_)
                        LOGGER.debug("checking %s for config"% filepath)

                        conn_data = ConnectionData()
                        conn_data.get_password = self.get_password
                        conn_data.from_conf_file(filepath)

                        LOGGER.info("loaded connection %s"% conn_data)
                        self._known_session_params.append(conn_data)
            except Exception:
                LOGGER.exception("error getting known_session_params")

        return self._known_session_params

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
                self.known_session_params)

        return self._connection_dialog

    def new_pg_session(self):
        '''
        connect a new postgres session
        '''
        if self.ALLOW_MULTIPLE_SESSIONS or not self.has_pg_connection:
            LOGGER.debug("%s.new_pg_session"% __file__)
            dl = self.connection_dialog
            while True:
                if not dl.exec_():
                    return
                if not self.ALLOW_MULTIPLE_SESSIONS:
                    self.end_pg_sessions()
                conn_data = dl.chosen_connection

                session = self.CONN_CLASS(conn_data)
                try:
                    if self._attempt_connection(session):
                        self.add_session(session)
                except session.SchemaVersionError as error:
                    self.advise(u"%s<hr /><pre>%s</pre>"% (
                        _("Schema is out of date"), error), 2)
                    LOGGER.exception("Schema Version Error") 
                finally:
                    break
        self.update_session_status()

    def _attempt_connection(self, session):
        '''
        attempt to open session (ie call :doc:`OpenmolarDatabase` .connect() )
        '''
        LOGGER.info(u"%s '%s'"% (_("Attempting connection using data"),
            session.connection_data))

        try:
            session.connect()
            self.connect(QtGui.QApplication.instance(),
                QtCore.SIGNAL("Query Error"), self.advise_dl)
            return True
        except ConnectionError as error:
            self.advise(u"%s<hr /><pre>%s</pre>"% (
                _("Connection Error"), error), 2)
            LOGGER.exception("Connection Error")
            
        return False

    def end_pg_sessions(self):
        '''
        disconnect from postgres server
        (if not connected - pass quietly).
        '''
        for widg in self.session_widgets:
            i = self.central_widget.indexOf(widg)
            if widg.is_connected:
                widg.pg_session.close()
                LOGGER.info("DISCONNECTED session %s"% widg.pg_session)
            if i != -1:
                #widg has already been removed?
                self.central_widget.removeTab(i)
        self.session_widgets = []
        self.update_session_status()

    def update_session_status(self):
        '''
        toggles the connect buttons/menu actions,
        updates the sessions displayed.
        '''
        for session_widg in self.session_widgets:
            session_widg.update_status()
        self.action_connect.setEnabled(
            self.ALLOW_MULTIPLE_SESSIONS or not self.has_pg_connection)
        self.action_disconnect.setEnabled(self.session_widgets != [])

    @property
    def has_pg_connection(self):
        '''
        returns a bool which states if an active connection exists.
        '''
        return self.session_widgets != []

    def get_user_pass(self, dbname):
        '''
        return a tuple of (result, user, password)
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
        self.end_pg_sessions()

    def preferences_dialog(self):
        if self._preferences_dialog is None:
            dl = PlugableMainWindow.preferences_dialog(self)

            connections_pref = Preference(_("Database Connections"))

            m_d_widg = ManageDatabasesWidget(self)
            m_d_widg.set_connections(self.known_session_params)
            connections_pref.setWidget(m_d_widg)
            dl.insert_preference_dialog(0, connections_pref)

            self._preferences_dialog = dl

        return self._preferences_dialog

def _test():
    import logging
    import lib_openmolar.client
    LOGGER.setLevel(logging.DEBUG)

    app = RestorableApplication("openmolar-test-suite")
    settings = QtCore.QSettings()
    settings.setValue("connection_conf_dir",
        "/etc/openmolar/client/connections")

    mw = PostgresMainWindow()
    mw.show()
    app.exec_()

if __name__ == "__main__":
    _test()
