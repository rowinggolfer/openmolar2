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

import datetime
import cPickle
import logging
import re
import sys
import pickle
from xmlrpclib import Fault as ServerFault
from PyQt4 import QtGui, QtCore

from lib_openmolar.common import SETTINGS

from lib_openmolar.common.connect import (
    ProxyUser,
    ConnectionError,
    ConnectionsPreferenceWidget,
    ConnectDialog,
    OpenmolarConnection,
    OpenmolarConnectionError)

from lib_openmolar.admin import qrc_resources

from lib_openmolar.common.widgets import (
    RestorableApplication,
    Advisor,
    BaseMainWindow,
    Preference,
    PreferencesDialog)

from lib_openmolar.common.dialogs import (
    NewUserPasswordDialog, UserPasswordDialog)

from lib_openmolar.admin.connect import AdminConnection

from lib_openmolar.admin.db_tools.proxy_manager import (
    ProxyManager, PermissionError)

from lib_openmolar.admin.qt4gui.dialogs import *

from lib_openmolar.admin.qt4gui.classes import (
    SqlQueryTable,
    AdminTabWidget,
    LogWidget)

from lib_openmolar.admin.qt4gui.classes.database_table import (
    DatabaseTableViewer,
    RelationalDatabaseTableViewer)

class AdminMainWindow(BaseMainWindow, ProxyManager):
    '''
    This class is the core application.
    '''
    _preferences_dialog = None
    log = LOGGER

    def __init__(self, parent=None):
        BaseMainWindow.__init__(self, parent)
        self.setMinimumSize(600, 400)
        self.dirty = False
        self.setWindowTitle("Openmolar Admin")
        self.setWindowIcon(QtGui.QIcon(":icons/openmolar-server.png"))

        ## Main Menu

        ## "file"

        icon = QtGui.QIcon.fromTheme("network-wired")
        self.action_omconnect = QtGui.QAction(icon,
            "OM %s"% _("Connect"), self)
        self.action_omconnect.setToolTip(_("Connect (to an openmolar server)"))

        icon = QtGui.QIcon.fromTheme("network-error")
        self.action_omdisconnect = QtGui.QAction(icon,
            "OM %s"% _("Disconnect"), self)
        self.action_omdisconnect.setToolTip(
            _("Disconnect (from an openmolar server)"))

        icon = QtGui.QIcon(":icons/postgresql_elephant.svg")
        self.action_connect = QtGui.QAction(icon, _("Begin Session"), self)
        self.action_connect.setToolTip(_("Start a PostgreSQL session"))

        icon = QtGui.QIcon(":icons/no_postgresql_elephant.svg")
        self.action_disconnect = QtGui.QAction(icon, _("End Session"), self)
        self.action_disconnect.setToolTip(_("End a PostgreSQL session"))

        insertpoint = self.action_quit
        self.menu_file.insertAction(insertpoint, self.action_omconnect)
        self.menu_file.insertAction(insertpoint,self.action_omdisconnect)
        self.menu_file.insertSeparator(insertpoint)
        self.menu_file.insertAction(insertpoint, self.action_connect)
        self.menu_file.insertAction(insertpoint,self.action_disconnect)
        self.menu_file.insertSeparator(insertpoint)

        insertpoint = self.action_help
        self.main_toolbar.insertAction(insertpoint, self.action_omconnect)
        self.main_toolbar.insertAction(insertpoint,self.action_omdisconnect)
        self.main_toolbar.insertSeparator(insertpoint)
        self.main_toolbar.insertAction(insertpoint, self.action_connect)
        self.main_toolbar.insertAction(insertpoint, self.action_disconnect)
        self.main_toolbar.insertSeparator(insertpoint)

        ## "Database Tools"

        self.menu_database = QtGui.QMenu(_("&Database Tools"), self)
        self.insertMenu_(self.menu_database)

        icon = QtGui.QIcon.fromTheme("contact-new")
        self.action_new_database = QtGui.QAction(icon,
            _("New Openmolar Database"), self)

        self.action_populate_demo = QtGui.QAction(icon,
            _("Populate database with demo data"), self)

        self.menu_database.addAction(self.action_new_database)
        self.menu_database.addAction(self.action_populate_demo)

        tb_database = QtGui.QToolButton(self)
        icon = QtGui.QIcon(":icons/database.png")
        tb_database.setIcon(icon)
        tb_database.setText(_("Database Tools"))
        tb_database.setToolTip(_("A variety of database tools"))
        tb_database.setPopupMode(tb_database.InstantPopup)
        tb_database.setMenu(self.menu_database)

        self.insertToolBarWidget(tb_database, True)

        self.log_widget = LogWidget(LOGGER, self.parent())
        self.log_widget.welcome()
        self.log_dock_widget = QtGui.QDockWidget(_("Log"), self)
        self.log_dock_widget.setObjectName("LogWidget") #for save state!
        self.log_dock_widget.setWidget(self.log_widget)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
            self.log_dock_widget)

        self.action_show_log = self.log_dock_widget.toggleViewAction()
        insertpoint = self.action_show_statusbar
        self.menu_view.insertAction(insertpoint, self.action_show_log)

        #take a note of this before restoring settings
        self.system_font = self.font()

        ####       now load stored settings                                ####
        self.loadSettings()
        tb_database.setToolButtonStyle(self.main_toolbar.toolButtonStyle())

        self.connection = None
        self.tabs = []

        self.tab_widget = AdminTabWidget(self)
        self.browser = self.tab_widget.browser
        self.setCentralWidget(self.tab_widget)

        self.end_pg_session()
        self.connect_signals()
        self.show()

        QtCore.QTimer.singleShot(100, self.setBriefMessageLocation)
        QtCore.QTimer.singleShot(100, self._init_proxy_message)

    def connect_signals(self):
        '''
        set up signals/slots
        '''

        ##some old style connects are used to ensure argument (bool=0)
        ##is not passed to the slot

        self.action_omconnect.triggered.connect(self.om_connect)
        self.action_omdisconnect.triggered.connect(self.om_disconnect)

        self.action_connect.triggered.connect(self.choose_connection)
        self.action_disconnect.triggered.connect(self.end_pg_session)

        self.action_show_log.triggered.connect(self.show_log)

        self.action_new_database.triggered.connect(self.create_new_database)
        self.action_populate_demo.triggered.connect(self.populate_demo)

        self.connect(self.tab_widget, QtCore.SIGNAL("Widget Removed"),
            self.remove_tab)
        self.connect(self.tab_widget, QtCore.SIGNAL("new query tab"),
            self.add_query_editor)
        self.connect(self.tab_widget, QtCore.SIGNAL("new table tab"),
            self.add_table_tab)

        self.tab_widget.currentChanged.connect(self.tab_widget_selected)

        self.browser.shortcut_clicked.connect(self.manage_shortcut)

    def _init_proxy_message(self):
        '''
        called only at startup
        '''
        self.init_proxy()
        self.display_proxy_message()

    def display_proxy_message(self):
        '''
        attempt to connect to the server controller at startup
        '''
        self.wait()
        try:
            message = self.proxy_message
            self.browser.setHtml(message)
        finally:
            self.wait(False)

    def switch_server_user(self):
        self.advise("we need to up your permissions for this",1)
        return False

    def tab_widget_selected(self, i=-1):
        tab = self.tab_widget.currentWidget()
        if (tab and type(tab) == DatabaseTableViewer or
        type(tab) == RelationalDatabaseTableViewer) :
            tab.load_table_choice()

    def show_log(self):
        '''
        toggle the state of the log dock window
        '''
        if self.action_show_log.isChecked():
            self.log_dock_widget.show()
        else:
            self.log_dock_widget.hide()

    def start_pg_session(self):
        '''
        connect to a server
        '''
        try:
            self.connection.connect()
            self.connect(QtGui.QApplication.instance(),
                QtCore.SIGNAL("Query Error"), self.advise_dl)

            self.addViews()

        except ConnectionError as error:
            self.advise(u"%s<hr />%s"% (
                _("Connection Error"), error), 2)
            LOGGER.exception("Connection Error")
        self._can_connect()

    def end_pg_session(self, shutting_down=False):
        '''
        disconnect from server
        (if not connected - pass quietly).
        '''
        if self.connection:
            if (self.connection.isOpen() and (
            shutting_down or self.tab_widget.closeAll())):
                self.connection.close()
                self.connection = None
                LOGGER.info("DISCONNECTED")
            self.connection = None
        else:
            self.tab_widget.closeAll()
        self._can_connect()

    def addViews(self):
        self.tab_widget.closeAllWithoutQuestion()
        self.tab_widget.addTab(self.browser, _("Messages"))
        self.add_table_tab()
        self.add_query_editor()
        self.tab_widget.setCurrentIndex(1)

    def add_table_tab(self):
        if self.connection and self.connection.isOpen():
            ## add a relational database table
            ##todo - find out if this class is better for my needs!
            #table = DatabaseTableViewer(self.connection)
            widg = RelationalDatabaseTableViewer(self.connection, self.tab_widget)
            self.connect(widg, QtCore.SIGNAL("Query Success"), self.advise)
            self.connect(widg, QtCore.SIGNAL("Query Error"), self.advise_dl)
            self.tabs.append(widg)
            icon = QtGui.QIcon.fromTheme("text-x-generic")
            self.tab_widget.addTab(widg, icon, _("Table (Relational)"))

    def add_query_editor(self):
        if self.connection and self.connection.isOpen():
            ## add a query table
            widg = SqlQueryTable(self.connection)
            self.connect(widg, QtCore.SIGNAL("Query Success"), self.advise)
            self.connect(widg, QtCore.SIGNAL("Query Error"), self.advise_dl)
            self.tabs.append(widg)
            icon = QtGui.QIcon.fromTheme("text-x-generic")
            self.tab_widget.addTab(widg, icon, _("Query Tool"))

    def remove_tab(self, tab):
        if tab in self.tabs:
            tab.deleteLater()
            self.tabs.remove(tab)

    def choose_connection(self):
        '''
        catches signal when user hits the connect action
        '''
        LOGGER.debug("%s.choose_connection called"% __file__)
        connections = SETTINGS.connections
        dl = ConnectDialog(connections, self)
        while True:
            if not dl.exec_():
                return
            self.end_pg_session()
            connection = dl.chosen_connection

            self.connection = AdminConnection(
                    host = connection.host,
                    user = connection.username,
                    passwd = connection.password,
                    port = connection.port,
                    db_name = connection.db_name)

            if connection.password == "":
                pass_used = "NO"
            else:
                pass_used = "*" * len(connection.password)

            LOGGER.info(u"%s '%s' %s %s %s %s %s %s"% (
            _("Attempting connection as"), connection.username,
            _("to the host"), connection.host, _("port"), connection.port,
            _("Using password"), pass_used))

            SETTINGS.set_connections(dl.known_connections)
            self.start_pg_session()

            if self.connection.isOpen():
                return True
            else:
                break
        return False

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
        if self.connection and self.connection.isOpen():
            username = self.connection.userName()
            host = self.connection.hostName()
            port = self.connection.port()
            database = self.connection.databaseName()
            message = (u"%s <b>'%s'</b> %s <b>'%s:%s'</b><br /><i> "% (
            _("Connected as"), username, _("to host server"),
            host, port))
            if not database:
                message += u"%s</i>"% _("No Database Selected")
            else:
                message += u"%s '%s'</i>"% (_("Using Database"), database)
            #self.tab_widget_selected() #update widgets.
            self.advise(message)
            message = message.replace("<br />", "")
            self.status_label.setText(message)
            message = re.compile('<.*?>').sub(" ", message)
            LOGGER.info(message)
            return True
        else:
            self.status_label.setText(_("Not Connected to a database"))
            return False

    def has_connection(self):
        '''
        checks the connection to db.. if not present prompts user to get one
        '''
        if self.connection and self.connection.isOpen():
            return True
        self.advise(_("database connection required to continue"), 1)
        return self.choose_connection()

    def has_database(self):
        '''
        checks if a database has been selected yet..
        if not present prompts user to get one
        '''
        if not self.has_connection():
            return (None, False)
        if self.connection.databaseName():
            return (unicode(self.connection.databaseName()), True)
        self.advise(_("A Database must be selected to continue"), 1)
        return self.select_database()

    def get_user_pass(self, dbname):
        '''
        return a tuple of result user, password
        '''
        LOGGER.debug("%s.get_user_pass %s"% (__file__, dbname))
        if dbname == "openmolar_demo":
            return (True, "om_demo", "password")
        dl = UserPasswordDialog(self)
        return dl.exec_(), dl.name, dl.password

    def use_proxy_connection(self, dbname):
        '''
        user has clicked on a link requesting a session on dbname
        '''
        result, user, passwd = self.get_user_pass(dbname)
        if not result:
            return
        self.connection = AdminConnection(
            host = AD_SETTINGS.server_location,
            user = user,
            passwd = passwd,
            port = 5432,
            db_name = dbname)
        self.start_pg_session()


    def select_database(self, reason=""):
        '''
        allow the user to choose a database
        '''
        if not self.has_connection():
            return
        if not reason:
            reason = _("Select a Database")
        databases = self.connection.get_available_databases()
        if databases:
            dl = QtGui.QInputDialog(self)
            dl.setOption(dl.UseListViewForComboBoxItems)
            dl.setComboBoxItems(databases)
            dl.setLabelText(reason)
            dl.setWindowTitle(_("Choice"))
            if dl.exec_():
                chosen = unicode(dl.textValue().toAscii())
                if self.connection.databaseName() != chosen:
                    self.connection.close()
                    self.connection.setDatabaseName(chosen)
                    self.connection.connect()
                    self._connection_status()
                return (chosen, True)
        else:
            self.advise(_("No Databases found"),2)
        return ("", False)

    def create_new_database(self):
        '''
        raise a dialog, then create a database with the chosen name
        '''
        dl = NewDatabaseDialog(self)
        if not dl.exec_() or dl.database_name == "":
            self.display_proxy_message()
            return
        dbname = dl.database_name
        ProxyManager.create_database(self, dbname)

    def create_demo_database(self):
        '''
        initiates the demo database
        '''
        LOGGER.info("creating demo database")
        result = ProxyManager.create_demo_database(self)
        LOGGER.info(result)
        if (result and
        QtGui.QMessageBox.question(self, _("Confirm"),
        u"%s"% _("Populate with demo data now?"),
        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Ok) == QtGui.QMessageBox.Ok):
            self.populate_demo()

        self.display_proxy_message()

    def set_permissions(self, database):
        '''
        alters permissions on a known database
        '''
        dl = NewUserPasswordDialog(self)
        result, user, password = dl.getValues()
        message = "TODO - enable set_permissions for %s, %s"% (user, "****")
        self.advise(message, 1)
        if result:
            LOGGER.info(message)

    def populate_demo(self):
        '''
        catches signal when user hits the demo action
        '''
        if not self.has_connection():
            return

        dl = PopulateDemoDialog(self.connection, self)
        if not dl.exec_():
            self.advise("Demo data population was abandoned", 1)
        self.addViews()

    def manage_db(self, dbname):
        '''
        raise a dialog, and provide database management tools
        '''
        dl = ManageDatabaseDialog(dbname, self)
        if dl.exec_():
            if dl.manage_users:
                self.advise("manage users")
            elif dl.drop_db:
                self.advise(u"%s %s"%(_("dropping database"), dbname))
                self.drop_db(dbname)

    def closeEvent(self, event=None):
        '''
        re-implement the close event of QtGui.QMainWindow, and check the user
        really meant to do this.
        '''
        if (self.log_widget.dirty and
        QtGui.QMessageBox.question(self, _("Confirm"),
        _("You have unsaved log changes - Quit Application?"),
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.No):
            event.ignore()
        else:
            self.saveSettings()
            self.end_pg_session(shutting_down=True)

    @property
    def confirmDataOverwrite(self):
        '''
        check that the user is prepared to lose any changes
        '''
        result = QtGui.QMessageBox.question(self, _("confirm"),
        "<p>%s<br />%s</p>"% (
        _("this action will overwrite any current data stored"),
        _("proceed?")),
        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Ok )
        return result == QtGui.QMessageBox.Ok

    def save_template(self):
        '''
        save the template, so it can be re-used in future
        '''
        try:
            filepath = QtGui.QFileDialog.getSaveFileName(self,
            _("save template file"),"",
            _("openmolar template files ")+"(*.om_xml)")
            if filepath != '':
                if not re.match(".*\.om_xml$", filepath):
                    filepath += ".om_xml"
                f = open(filepath, "w")
                f.write(self.template.toxml())
                f.close()
                self.advise(_("Template Saved"), 1)
            else:
                self.advise(_("operation cancelled"), 1)
        except Exception, e:
            self.advise(_("Template not saved")+" - %s"% e, 2)

    def load_template(self):
        '''
        change the default template for a new database
        '''
        if not self.confirmDataOverwrite:
            return
        filename = QtGui.QFileDialog.getOpenFileName(self,
        _("load an existing template file"),"",
        _("openmolar template files")+" (*.om_xml)")

        if filename != '':
            try:
                self.template = minidom.parse(str(filename))
                self.advise(_("template loaded sucessfully"),1)
            except Exception, e:
                self.advise(_("error parsing template file")+" - %s"% e, 2)
        else:
            self.advise(_("operation cancelled"), 1)

    def loadSettings(self):
        BaseMainWindow.loadSettings(self)
        qsettings = QtCore.QSettings()

        #python dict of settings
        dict_ = str(qsettings.value("settings_dict").toString())
        if dict_:
            try:
                AD_SETTINGS.PERSISTANT_SETTINGS = cPickle.loads(dict_)
            except Exception as e:
                LOGGER.exception(
                    "exception caught loading python settings...")

    def saveSettings(self):
        BaseMainWindow.saveSettings(self)
        qsettings = QtCore.QSettings()

        # AD_SETTINGS.PERSISTANT_SETTINGS is a python dict of non qt-specific settings.
        # unfortunately.. QVariant.toPyObject can't recreate a dictionary
        # so best to pickle this
        pickled_dict = cPickle.dumps(AD_SETTINGS.PERSISTANT_SETTINGS)
        qsettings.setValue("settings_dict", pickled_dict)

    def show_about(self):
        '''
        raise a dialog showing version info etc.
        '''
        ABOUT_TEXT = "<p>%s</p><pre>%s\n%s</pre><p>%s<br />%s</p>"% ( _('''
This application provides tools to manage and configure your database server
and can set up either a demo openmolar database, or a
customised database for a specific dental practice situation.'''),
_("Version"), AD_SETTINGS.VERSION,
"<a href='http://www.openmolar.com'>www.openmolar.com</a>",
'Neil Wallace - rowinggolfer@googlemail.com')
        self.advise(ABOUT_TEXT, 1)

    def show_help(self):
        '''
        todo - this is the same as show_about
        '''
        self.show_about()

    @property
    def preferences_dialog(self):
        if self._preferences_dialog is None:
            dl = self._preferences_dialog = PreferencesDialog(self)

            connections_pref = Preference(_("Database Connections"))
            dl.cp_widg = ConnectionsPreferenceWidget(
                SETTINGS.connections, self)
            connections_pref.setWidget(dl.cp_widg)
            dl.insert_preference_dialog(0, connections_pref)

        return self._preferences_dialog

    def show_preferences_dialog(self):
        self.preferences_dialog.exec_()
        SETTINGS.set_connections(self.preferences_dialog.cp_widg.connections)

    def switch_server_user(self):
        '''
        to change the user of the proxy up to admin
        overwrites :doc:`ProxyManager` function
        '''
        LOGGER.debug("switch_server_user called")
        self.advise("we need to up your permissions for this", 1)
        dl = UserPasswordDialog(self)
        dl.set_name("admin")
        if dl.exec_():
            name = dl.name
            psword = dl.password
            AD_SETTINGS.proxy_user = ProxyUser(name, psword)

            #force reload of server at next use
            self._proxy_server = None
            return True
        return False

    def manage_shortcut(self, url):
        '''
        the admin browser
        (which commonly contains messages from the openmolar_server)
        is connected to this slot.
        when a url is clicked it finds it's way here for management.
        unrecognised signals are send to the user via the notification.
        '''
        try:
            if url == "init_proxy":
                LOGGER.debug("User shortcut - Re-try openmolar_server connection")
                self.om_connect()
            elif url == "install_demo":
                LOGGER.debug("Install demo called via shortcut")
                self.create_demo_database()
            elif re.match("connect_.*", url):
                dbname = re.match("connect_(.*)", url).groups()[0]
                self.advise("start session on database %s"% dbname)
                self.use_proxy_connection(dbname)
            elif re.match("manage_.*", url):
                dbname = re.match("manage_(.*)", url).groups()[0]
                self.manage_db(dbname)
            else:
                self.advise("%s<hr />%s"% (_("Shortcut not found"), url), 2)
        except PermissionError as exc:
            self.advise("%s<hr />%s" %(_("Permission denied"), exc), 2)

def main():

    app = RestorableApplication("openmolar-admin")
    ui = AdminMainWindow()
    ui.show()
    app.exec_()
    app = None

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")
    sys.exit(main())
