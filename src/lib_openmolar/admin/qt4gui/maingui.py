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
import re
import sys
from PyQt4 import QtGui, QtCore

if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.abspath("../../../../"))

from lib_openmolar.common.connect import (
    ConnectionError,
    ConnectionsPreferenceWidget,
    ConnectDialog)

from lib_openmolar.common import SETTINGS

from lib_openmolar.admin import qrc_resources

from lib_openmolar.common.widgets import (
    RestorableApplication,
    Advisor,
    BaseMainWindow,
    Preference,
    PreferencesDialog)

from lib_openmolar.common.dialogs import (
    NewUserPasswordDialog)

from lib_openmolar.admin.connect import AdminConnection

from lib_openmolar.admin.qt4gui.dialogs import (
    NoDatabaseDialog,
    NewDatabaseDialog,
    PopulateDemoDialog,
    PlainTextDialog,
    NewRowDialog)

from lib_openmolar.admin.qt4gui.classes import (
    SqlQueryTable,
    AdminTabWidget,
    LogWidget)

from lib_openmolar.admin.qt4gui.classes.database_table import (
    DatabaseTableViewer,
    RelationalDatabaseTableViewer)

class AdminMainWindow(BaseMainWindow):
    '''
    This class is the core application.
    '''
    def __init__(self, parent=None):
        super(AdminMainWindow, self).__init__(parent)
        self.setMinimumSize(600, 400)
        self.dirty = False
        self.setWindowTitle("Openmolar Admin")
        self.setWindowIcon(QtGui.QIcon(":icons/openmolar-server.png"))

        ## Main Menu

        ## "file"
        icon = QtGui.QIcon.fromTheme("network-wired")
        self.action_connect = QtGui.QAction(icon, _("Connect"), self)
        self.action_connect.setToolTip(_("Connect to a Server"))

        icon = QtGui.QIcon.fromTheme("network-error")
        self.action_disconnect = QtGui.QAction(icon, _("Disconnect"), self)
        self.action_disconnect.setToolTip(_("Disconnect from Server"))

        insertpoint = self.action_quit
        self.menu_file.insertAction(insertpoint, self.action_connect)
        self.menu_file.insertAction(insertpoint,self.action_disconnect)
        self.menu_file.insertSeparator(insertpoint)

        insertpoint = self.action_help
        self.main_toolbar.insertAction(insertpoint, self.action_connect)
        self.main_toolbar.insertAction(insertpoint, self.action_disconnect)
        self.main_toolbar.insertSeparator(insertpoint)

        ## "Database Tools"

        self.menu_database = QtGui.QMenu(_("&Database Tools"), self)
        self.insertMenu_(self.menu_database)

        icon = QtGui.QIcon.fromTheme("edit-find")
        self.action_list_databases = QtGui.QAction(icon,
            _("List Available Databases"), self)

        icon = QtGui.QIcon.fromTheme("edit-select-all")
        self.action_select_database = QtGui.QAction(icon,
            _("Select a Database"), self)

        icon = QtGui.QIcon.fromTheme("accessories-text-editor")
        self.action_show_tables = QtGui.QAction(icon,
            _("Show Database Tables"), self)
        self.action_show_schema = QtGui.QAction(icon,
            _("Show Database schema"), self)

        self.menu_database.addAction(self.action_list_databases)
        self.menu_database.addAction(self.action_select_database)
        self.menu_database.addSeparator()
        self.menu_database.addAction(self.action_show_tables)
        self.menu_database.addAction(self.action_show_schema)

        ## "Openmolar Specific Tools"

        self.menu_openmolar = QtGui.QMenu(_("&OpenMolar Tools"), self)
        self.insertMenu_(self.menu_openmolar)

        icon = QtGui.QIcon.fromTheme("contact-new")
        self.action_new_database = QtGui.QAction(icon,
            _("New Openmolar Database"), self)

        self.action_new_schema = QtGui.QAction(icon,
            _("Install the basic (empty) schema into current database"), self)

        self.action_populate_demo = QtGui.QAction(icon,
            _("Populate database with demo data"), self)

        self.menu_openmolar.addAction(self.action_new_database)
        self.menu_openmolar.addAction(self.action_new_schema)
        self.menu_openmolar.addAction(self.action_populate_demo)

        tb_database = QtGui.QToolButton(self)
        icon = QtGui.QIcon(":icons/database.png")
        tb_database.setIcon(icon)
        tb_database.setText(_("Database Tools"))
        tb_database.setToolTip(_("A variety of database tools"))
        tb_database.setPopupMode(tb_database.InstantPopup)
        tb_database.setMenu(self.menu_database)

        self.insertToolBarWidget(tb_database, True)

        tb_openmolar = QtGui.QToolButton(self)
        icon = QtGui.QIcon(":icons/openmolar-server.png")
        tb_openmolar.setIcon(icon)
        tb_openmolar.setText(_("&OpenMolar Tools"))
        tb_openmolar.setToolTip(
            _("Tools to install/manage your openmolar database(s)"))
        tb_openmolar.setPopupMode(tb_openmolar.InstantPopup)
        tb_openmolar.setMenu(self.menu_openmolar)

        self.insertToolBarWidget(tb_openmolar, True)

        self.log_widget = LogWidget(self.parent())
        self.log_widget.welcome()
        self.log_dock_widget = QtGui.QDockWidget(_("Log"), self)
        self.log_dock_widget.setObjectName("LogWidget") #for save state!
        self.log_dock_widget.setWidget(self.log_widget)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
            self.log_dock_widget)

        self.action_show_log = self.log_dock_widget.toggleViewAction()
        insertpoint = self.action_show_statusbar
        self.menu_view.insertAction(insertpoint, self.action_show_log)

        self.tab_widget = AdminTabWidget(self)

        self.setCentralWidget(self.tab_widget)

        #take a note of this before restoring settings
        self.system_font = self.font()

        ####       now load stored settings                                ####
        self.loadSettings()
        tb_database.setToolButtonStyle(self.main_toolbar.toolButtonStyle())
        tb_openmolar.setToolButtonStyle(self.main_toolbar.toolButtonStyle())

        self.connection = None
        self.tabs = []
        self.disconnect_server()

        self.connect_signals()
        self.show()
        self.setBriefMessageLocation()

    def connect_signals(self):
        '''
        set up signals/slots
        '''

        ##some old style connects are used to ensure argument (bool=0)
        ##is not passed to the slot

        self.action_connect.triggered.connect(self.choose_connection)
        self.action_disconnect.triggered.connect(self.disconnect_server)

        self.action_show_log.triggered.connect(self.show_log)
        self.action_list_databases.triggered.connect(self.show_databases)
        self.action_show_tables.triggered.connect(self.show_tables)
        self.action_show_schema.triggered.connect(self.show_schema)

        self.connect(self.action_select_database,
            QtCore.SIGNAL("triggered()"), self.select_database)

        self.action_new_database.triggered.connect(self.new_database)
        self.action_new_schema.triggered.connect(self.layout_new_schema)
        self.action_populate_demo.triggered.connect(self.populate_demo)

        self.connect(self.tab_widget, QtCore.SIGNAL("Widget Removed"),
            self.remove_tab)
        self.connect(self.tab_widget, QtCore.SIGNAL("new query tab"),
            self.add_query_editor)
        self.connect(self.tab_widget, QtCore.SIGNAL("new table tab"),
            self.add_table_tab)

        self.tab_widget.currentChanged.connect(self.tab_widget_selected)

    def tab_widget_selected(self, i=-1):
        tab = self.tab_widget.currentWidget()
        if (tab and type(tab) == DatabaseTableViewer or
        type(tab) == RelationalDatabaseTableViewer) :
            tab.load_table_choice()

    def log(self, message="", timestamp=False):
        '''
        pass a message onto the logger
        '''
        if timestamp:
            stamp = u"%-12s"% QtCore.QTime.currentTime().toString()
        else:
            stamp = " "*12
            message = message.replace("\n", "\n %s"%stamp)
        self.log_widget.log(u"%s %s"% (stamp, message))

    def show_log(self):
        '''
        toggle the state of the log dock window
        '''
        if self.action_show_log.isChecked():
            self.log_dock_widget.show()
        else:
            self.log_dock_widget.hide()

    def connect_server(self):
        '''
        connect to a server
        '''
        try:
            self.connection.connect()
            self.connect(QtGui.QApplication.instance(),
                QtCore.SIGNAL("Query Error"), self.advise_dl)

            self.addViews()

            if len(self.connection.tables()) == 0:
                self.setup_wizard()
            if self.connection.has_all_empty_tables:
                self.populate_wizard()


        except ConnectionError as error:
            self.advise(u"%s<hr />%s"% (
                _("Connection Error"), error), 2)
            self.log("ERROR %s"%error, True)

    def disconnect_server(self, shutting_down=False):
        '''
        disconnect from server
        (if not connected - pass quietly).
        '''
        if self.connection:
            if (self.connection.isOpen() and (
            shutting_down or self.tab_widget.closeAll(_("Disconnect and")))):
                self.connection.close()
                self.connection = None
                self.log(_("DISCONNECTED"), True)
            self.connection = None
        else:
            self.tab_widget.closeAll()
        self._can_connect()

    def addViews(self):
        self.tab_widget.closeAllWithoutQuestion()
        self.add_table_tab()
        self.add_query_editor()

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
        tab.deleteLater()
        self.tabs.remove(tab)

    def choose_connection(self):
        '''
        catches signal when user hits the connect action
        '''
        connections = SETTINGS.connections
        dl = ConnectDialog(connections, self)
        while True:
            if not dl.exec_():
                return
            self.disconnect_server()
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

            self.log(u"%s '%s' %s %s %s %s %s %s"% (
            _("Attempting connection as"), connection.username,
            _("to the host"), connection.host, _("port"), connection.port,
            _("Using password"), pass_used), True)

            SETTINGS.set_connections(dl.known_connections)
            self.connect_server()

            self._can_connect()

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
            self.log(message, True)
            return True
        else:
            self.status_label.setText(_("Not Connected to a Server"))
            return False

    def has_connection(self):
        '''
        checks the connection to db.. if not present prompts user to get one
        '''
        if self.connection and self.connection.isOpen():
            return True
        self.advise(_("database connection required to continue"), 1)
        return self.choose_connection()

    def show_databases(self):
        '''
        show a message box and log which databases are available with the
        current connection and user privileges
        '''
        if not self.has_connection():
            return
        self.wait()
        databases = self.connection.get_available_databases()
        self.log()
        self.log(_("Polling for databases"),True)
        if databases:
            message = u'''<body>List of Databases on the current server<br />
            %s<hr /><ul>'''% self.connection.get_server_version()
            for database in databases:
                message += u"<li>%s</li>"% database
                self.log("- %s"% database)
            message += "</ul></body>"
        else:
            message = _('No databases found')
            self.log(_("None Found"))
        self.wait(False)
        self.advise(message, 1)
        self.log()

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

    def show_tables(self):
        '''
        asks user to choose a database, then shows the tables therein
        '''
        chosen, result = self.has_database()
        if result:
            header_line = u"%s Database %s %s: %s"% ("="*12, chosen,
                _("has the following tables"), "="*12)
            self.log(header_line)
            self.wait()
            table_list = u""
            for table in self.connection.get_available_tables():
                self.log(table)
                table_list += "<li>%s</li>"% table
            self.log(("=" * len(header_line)) + "\n")
            self.advise(u"%s <hr /><ul>%s</ul>"% (header_line, table_list), 1)
        self.wait(False)

    def show_schema(self):
        '''
        popup the schema for a database
        '''
        if self.has_database()[1]:
            self.wait()
            schema = self.connection.get_db_schema()
            self.log(schema)
            dl = PlainTextDialog(schema, self)
            self.wait(False)
            dl.exec_()

    def new_database(self):
        '''
        creates a new db
        '''
        dl = NoDatabaseDialog(self)
        dl.exec_()

    def layout_new_schema(self):
        if not self.has_connection():
            return
        dl = NewDatabaseDialog(self.connection, self.log, self)
        self.connect(dl, QtCore.SIGNAL("Advise"), self.advise)
        if dl.exec_():
            self.addViews()

    def set_permissions(self, database):
        '''
        alters permissions on a known database
        '''
        dl = NewUserPasswordDialog(self)
        result, user, password = dl.getValues()
        message = "TODO - enable set_permissions for %s, %s"% (user, "****")
        self.advise(message, 1)
        if result:
            self.log(message)

    def populate_demo(self):
        '''
        catches signal when user hits the demo action
        '''
        if not self.has_connection():
            return

        if not (self.connection.databaseName().endsWith("_demo") or
        self.connection.databaseName().endsWith("_test")):
            self.advise(
            _("database name must end with '_demo' or '_test' to proceed"), 1)
            return

        dl = PopulateDemoDialog(self.connection, self.log, self)
        if not dl.exec_():
            self.advise("Demo data population was abandoned", 1)
        self.addViews()

    def manage_users(self):
        '''
        adds permission for a user to connect to a database
        '''
        self.advise("TODO - manage users", 1)

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
            self.disconnect_server(shutting_down=True)

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
                SETTINGS.PERSISTANT_SETTINGS = cPickle.loads(dict_)
            except Exception as e:
                print "exception caught loading python settings...", e

    def saveSettings(self):
        BaseMainWindow.saveSettings(self)
        qsettings = QtCore.QSettings()

        # SETTINGS.PERSISTANT_SETTINGS is a python dict of non qt-specific settings.
        # unfortunately.. QVariant.toPyObject can't recreate a dictionary
        # so best to pickle this
        pickled_dict = cPickle.dumps(SETTINGS.PERSISTANT_SETTINGS)
        qsettings.setValue("settings_dict", pickled_dict)

    def show_about(self):
        ABOUT_TEXT = ('<p>' + _('''
This application provides tools to manage and configure your database server
and can set up either a demo openmolar database, or a
customised database for a specific dental practice situation.''') +
'''<br /><br /><a href='https://launchpad.net/openmolar'>
https://launchpad.net/openmolar</a><br />
Neil Wallace - rowinggolfer@googlemail.com</p>''')
        self.advise(ABOUT_TEXT, 1)

    def show_help(self):
        HELP_TEXT = '''<a href='https://launchpad.net/openmolar'>
https://launchpad.net/openmolar</a><br />
Neil Wallace - rowinggolfer@googlemail.com'''
        self.advise(HELP_TEXT, 1)

    def show_preferences_dialog(self):
        dl = PreferencesDialog(self)

        connections_pref = Preference(_("Database Connections"))

        cp_widg = ConnectionsPreferenceWidget(SETTINGS.connections, self)
        connections_pref.setWidget(cp_widg)
        dl.insert_preference_dialog(0, connections_pref)

        dl.exec_()

        SETTINGS.set_connections(cp_widg.connections)

    def setup_wizard(self):
        '''
        we arrive here if there are no tables found in the loaded database
        '''
        if (self.connection.databaseName().startsWith("openmolar") and
        QtGui.QMessageBox.question(self, _("Question"),
        u"%s <b>%s</b><br />%s<hr />%s"% (
        _("You are connected to a database named"),
        self.connection.databaseName(),
        _("This database contains no tables."),
_("Would you like to install the openmolar schema into this database now?")),
        QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes):
            self.layout_new_schema()

    def populate_wizard(self):
        '''
        we arrive here if ALL tables found in the loaded database are empty
        '''
        if (self.connection.databaseName().startsWith("openmolar") and
        QtGui.QMessageBox.question(self, _("Question"),
        u"%s <b>%s</b><br />%s<hr />%s"% (
        _("You are connected to a database named"),
        self.connection.databaseName(),
        _("All tables are empty."),
        "populate now?") ,
        QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes):
            self.populate_demo()

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
