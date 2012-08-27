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

import os
import re
import sys
from xmlrpclib import Fault as ServerFault
from PyQt4 import QtGui, QtCore

from lib_openmolar.common.connect import ProxyClient, ProxyUser

from lib_openmolar.common.datatypes import ConnectionData
from lib_openmolar.common.qt4.widgets import RestorableApplication

from lib_openmolar.admin import qrc_resources

from lib_openmolar.admin.connect import AdminConnection

from lib_openmolar.admin.db_tools.proxy_manager import ProxyManager

from lib_openmolar.common.qt4.dialogs import *
from lib_openmolar.admin.qt4.dialogs import *

from lib_openmolar.admin.qt4.classes import (
    AdminTabWidget,
    LogWidget,
    AdminSessionWidget)

from lib_openmolar.common.qt4.postgres.postgres_mainwindow import \
    PostgresMainWindow

##TODO for windows version... this will need to be tweaked.
settings_dir = os.path.join(
    os.getenv("HOME"), ".openmolar2", "admin", "connections")

if not os.path.isdir(settings_dir):
    os.makedirs(settings_dir)

CONNECTION_CONFDIRS = [settings_dir, "/etc/openmolar/admin/connections"]

def require_session(func):
    '''
    a decorator function around methods that require a database session
    '''
    def sessionf(self):
        if not self.has_pg_connection:
            self.advise(_("Please start a session to perform this action"),1)
            return None
        return func(self)

    return sessionf


class AdminMainWindow(PostgresMainWindow, ProxyManager):
    '''
    This class is the core application.
    '''
    log = LOGGER

    CONN_CLASS = AdminConnection
    CONNECTION_CONFDIRS = CONNECTION_CONFDIRS

    def __init__(self, parent=None):
        PostgresMainWindow.__init__(self, parent)
        self.setMinimumSize(600, 400)

        self.setWindowTitle("Openmolar Admin")
        self.setWindowIcon(QtGui.QIcon(":icons/openmolar-server.png"))

        ## Main Menu

        ## "file"

        icon = QtGui.QIcon.fromTheme("network-wired")
        self.action_omconnect = QtGui.QAction(icon,
            "OM %s"% _("Connect"), self)
        self.action_omconnect.setToolTip(
                                _("Connect (to an openmolar server)"))
        icon = QtGui.QIcon.fromTheme("network-error")
        self.action_omdisconnect = QtGui.QAction(icon,
            "OM %s"% _("Disconnect"), self)
        self.action_omdisconnect.setToolTip(
            _("Disconnect (from an openmolar server)"))

        insertpoint = self.action_connect
        self.menu_file.insertAction(insertpoint, self.action_omconnect)
        self.menu_file.insertAction(insertpoint,self.action_omdisconnect)
        self.menu_file.insertSeparator(insertpoint)

        insertpoint = self.action_connect
        self.main_toolbar.insertAction(insertpoint, self.action_omconnect)
        self.main_toolbar.insertAction(insertpoint, self.action_omdisconnect)

        ## "Database Tools"
        self.menu_database = QtGui.QMenu(_("&Database Tools"), self)
        self.insertMenu_(self.menu_database)

        icon = QtGui.QIcon.fromTheme("contact-new")
        self.action_new_database = QtGui.QAction(icon,
            _("New Openmolar Database"), self)

        icon = QtGui.QIcon(":icons/database.png")
        self.action_populate_demo = QtGui.QAction(icon,
            _("Populate database with demo data"), self)

        self.menu_database.addAction(self.action_new_database)
        self.menu_database.addAction(self.action_populate_demo)

        self.database_toolbar = QtGui.QToolBar(self)
        self.database_toolbar.setObjectName("Database Toolbar")
        self.database_toolbar.toggleViewAction().setText(
            _("Database Toolbar"))
        self.database_toolbar.addAction(self.action_new_database)
        self.database_toolbar.addAction(self.action_populate_demo)
        self.insertToolBar(self.help_toolbar, self.database_toolbar)

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

        self.pg_sessions = []

        self.end_pg_sessions()
        self.connect_signals()
        self.show()

        QtCore.QTimer.singleShot(100, self.setBriefMessageLocation)
        QtCore.QTimer.singleShot(1000, self._init_proxies)

        SETTINGS.main_ui = self
        SETTINGS.load_plugins("admin")
        SETTINGS.activate_plugins()
        
    def connect_signals(self):
        '''
        set up signals/slots
        '''

        ##some old style connects are used to ensure argument (bool=0)
        ##is not passed to the slot

        self.action_omconnect.triggered.connect(self.om_connect)
        self.action_omdisconnect.triggered.connect(self.om_disconnect)

        self.action_show_log.triggered.connect(self.show_log)

        self.action_new_database.triggered.connect(self.create_new_database)
        self.action_populate_demo.triggered.connect(self.populate_demo)
        
        self.connect(self.central_widget, QtCore.SIGNAL("end_pg_sessions"),
            self.end_pg_sessions)

        self.known_server_widget.shortcut_clicked.connect(self.manage_shortcut)
        self.known_server_widget.server_changed.connect(self.set_proxy_index)

    @property
    def central_widget(self):
        '''
        overwrite the property of the Base Class
        '''
        if self._central_widget is None:
            LOGGER.debug("AdminMainWindow.. creating central widget")
            self._central_widget = AdminTabWidget(self)
            self.known_server_widget = self._central_widget.known_server_widget

            self._central_widget.add = self._central_widget.addTab
            self._central_widget.remove = self._central_widget.removeTab

        return self._central_widget

    @property
    def new_session_widget(self):
        '''
        overwrite the property of the Base Class
        '''
        admin_session_widget = AdminSessionWidget(self)
        admin_session_widget.query_error.connect(self.advise_dl)
        admin_session_widget.query_sucess.connect(self.advise)

        return admin_session_widget

    def _init_proxies(self):
        '''
        called at startup, and by the om_connect action
        '''
        self.wait()
        self.advise(_("Initiating OMServer connections"))
        self.advise(u"%s....."% _("Please wait"))
        ProxyManager._init_proxies(self)
        self.known_server_widget.clear()
        for client in self.proxy_clients:
            self.known_server_widget.add_proxy_client(client)
        self.known_server_widget.setEnabled(True)
        self.wait(False)
        self.advise(u"....%s"% _("Done!"))
        
    def om_disconnect(self):
        ProxyManager.om_disconnect(self)
        self.known_server_widget.clear()
        self.known_server_widget.setEnabled(False)
    
    def show_log(self):
        '''
        toggle the state of the log dock window
        '''
        if self.action_show_log.isChecked():
            self.log_dock_widget.show()
        else:
            self.log_dock_widget.hide()

    def end_pg_sessions(self, shutting_down=False):
        '''
        overwrite baseclass function
        '''
        if shutting_down or (
        self.has_pg_connection and self.central_widget.closeAll()):
            PostgresMainWindow.end_pg_sessions(self)
        else:
            if self.central_widget.closeAll():
                PostgresMainWindow.end_pg_sessions(self)
        self.update_session_status()
    
    def create_new_database(self):
        '''
        raise a dialog, then create a database with the chosen name
        '''
        dl = NewDatabaseDialog(self)
        if not dl.exec_() or dl.database_name == "":
            self.display_proxy_message()
            return
        dbname = dl.database_name
        try:
            ProxyManager.create_database(self, dbname)
        except ProxyClient.PermissionError as exc:
            self.advise(exc.message, 2)

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

    @property
    def chosen_pg_session(self):
        if len(self.session_widgets) == 1:
            i = 0
        else:
            i = self.central_widget.currentIndex()-1

        pg_session = self.session_widgets[i].pg_session
        return pg_session

    @require_session
    def populate_demo(self):
        '''
        catches signal when user hits the demo action
        '''
        pg_session = self.chosen_pg_session
        LOGGER.info("calling populate demo on session %s"% pg_session)
        dl = PopulateDemoDialog(pg_session, self)
        if not dl.exec_():
            self.advise(_("Demo data population was abandoned"), 1)

    def manage_db(self, dbname):
        '''
        raise a dialog, and provide database management tools
        '''
        dl = ManageDatabaseDialog(dbname, self.selected_client , self)
        dl.waiting.connect(self.wait)
        dl.function_completed.connect(self.display_proxy_message)
        dl.exec_()
            
    def manage_pg_users(self, dbname):
        '''
        raise a dialog, and provide database management tools
        '''
        dl = ManagePGUsersDialog(dbname, self.selected_client , self)
        dl.waiting.connect(self.wait)
        dl.function_completed.connect(self.display_proxy_message)
        dl.exec_()
                    
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
            self.end_pg_sessions(shutting_down=True)

    @property
    def confirmDataOverwrite(self):
        '''
        check that the user is prepared to lose any changes
        '''
        return self.get_confirm(u"<p>%s<br />%s</p>"% (
        _("this action will overwrite any current data stored"),
        _("proceed?")))

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

    def show_about(self):
        '''
        raise a dialog showing version info etc.
        '''
        ABOUT_TEXT = "<p>%s</p><pre>%s\n%s</pre><p>%s<br />%s</p>"% ( _('''
This application provides tools to manage and configure your database server
and can set up either a demo openmolar database, or a
customised database for a specific dental practice situation.'''),
_("Version"), SETTINGS.VERSION,
"<a href='http://www.openmolar.com'>www.openmolar.com</a>",
'Neil Wallace - rowinggolfer@googlemail.com')
        self.advise(ABOUT_TEXT, 1)

    def show_help(self):
        '''
        todo - this is the same as show_about
        '''
        self.show_about()

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
            user = ProxyUser(name, psword)
            client = self.selected_client
            LOGGER.debug("switch user of %s to %s"% (client, user))
            client.set_user(user)
            return True
        return False

    def display_proxy_message(self):
        '''
        display the proxy message.
        overwrites :doc:`ProxyManager` function
        '''
        LOGGER.info("Server Procedure completed")
        if self.selected_client:
            self.known_server_widget.set_html(self.selected_client.html)

    def manage_shortcut(self, url):
        '''
        the admin browser
        (which commonly contains messages from the openmolar_server)
        is connected to this slot.
        when a url is clicked it finds it's way here for management.
        unrecognised signals are send to the user via the notification.
        '''
        LOGGER.debug("manage_shortcut %s"% url)
        if url == 'Retry_230_connection':
            self.advise(_("retrying connection"))
            try:
                self.selected_client.connect()
            except ProxyClient.ConnectionError as ex:
                self.advise(ex.message, 2)
            self.display_proxy_message()
        elif url == "install_demo":
            LOGGER.debug("Install demo called via shortcut")
            self.create_demo_database()
        elif re.match("manage_.*", url):
            dbname = re.match("manage_(.*)", url).groups()[0]
            self.manage_db(dbname)
        elif re.match("user_manage_.*", url):
            dbname = re.match("user_manage_(.*)", url).groups()[0]
            self.manage_pg_users(dbname)
        elif url == 'add_pg_user':
            self.add_pg_user()
        elif url == 'drop_pg_user':
            self.remove_pg_user()            
        else:
            if not self.message_link(url):
                self.advise(
                "%s<hr />%s"% (_("Shortcut not found"), url), 2)
    
    def add_pg_user(self):
        '''
        raise a dialog and get a username and password to add as a postgres 
        user
        '''
        dl = NewUserPasswordDialog(self)
        dl.set_label_text(
          _("Please enter a username and password for the new postgres user")
            )
        
        result, user, password = dl.getValues()        
        if result:
            self.add_postgres_user(user, password)
    
    def remove_pg_user(self):
        '''
        ask for confirmation, then remove the user
        '''
        dl = DropPGUserDialog(self.selected_client , self)
        
        if dl.exec_():
            self.display_proxy_message()
    
    def message_link(self, url_text):
        LOGGER.debug("message_link function with text %s"%url_text)
        message = self.selected_client.message_link(url_text)
        if not message:
            return False
        self.known_server_widget.set_html(message)
        return True


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
