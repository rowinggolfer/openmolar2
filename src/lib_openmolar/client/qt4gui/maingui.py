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

import cPickle
import logging
import sys
from PyQt4 import QtGui, QtCore

from lib_openmolar.common.connect import (
    ConnectionError,
    ConnectionsPreferenceWidget,
    ConnectDialog)

from lib_openmolar.client.connect import ClientConnection

from lib_openmolar.common.widgets import (
    RestorableApplication,
    BaseMainWindow,
    Preference,
    PreferencesDialog)

from lib_openmolar.client.qt4gui import client_widgets
from lib_openmolar.client.qt4gui.interfaces import PatientInterface
from lib_openmolar.client.qt4gui.interfaces import DiaryInterface

class ClientMainWindow(BaseMainWindow):
    _preferences_dialog = None
    def __init__(self, parent=None):
        BaseMainWindow.__init__(self, parent)

        self.setWindowIcon(QtGui.QIcon(":icons/openmolar.png"))
        self.setWindowTitle(_("OpenMolar - YOUR dental database application"))
        self.setMinimumSize(700,400)

        # initiate the connection.
        # A pointer to this object is set up at SETTINGS.database
        ClientConnection()

        self.system_font = self.font()
        self.loadSettings()

        ## add the patient page
        self.patient_interface = PatientInterface(self)
        self.diary_interface = DiaryInterface(self)

        icon = QtGui.QIcon(':icons/database.png')
        self.action_patient = QtGui.QAction(icon, _("Patient Database"), self)

        icon = QtGui.QIcon.fromTheme("x-office-calendar",
            QtGui.QIcon(':icons/vcalendar.png'))
        self.action_diary = QtGui.QAction(icon, _("Diary"), self)

        insertpoint = self.action_help
        self.main_toolbar.insertAction(insertpoint, self.action_patient)
        self.main_toolbar.insertAction(insertpoint, self.action_diary)

        self.stacked_widget = QtGui.QStackedWidget(self)
        self.stacked_widget.addWidget(self.patient_interface)
        self.stacked_widget.addWidget(self.diary_interface)

        self.setCentralWidget(self.stacked_widget)

        self.status_widget = client_widgets.StatusBarWidget()
        self.statusbar.addPermanentWidget(self.status_widget)

        icon = QtGui.QIcon.fromTheme("network-wired")
        self.action_connect = QtGui.QAction(icon, _("Connect"), self)
        self.action_connect.setToolTip(_("Connect to a Server"))
        insertpoint = self.action_quit
        self.menu_file.insertAction(insertpoint, self.action_connect)
        self.menu_file.insertSeparator(insertpoint)

        self.connect_signals()

        QtCore.QTimer.singleShot(100, self.choose_connection)

        SETTINGS.mainui = self
        SETTINGS.load_plugins()

    @property
    def is_dirty(self):
        return self.patient_interface.is_dirty

    def connect_server(self):
        '''
        connect to a server
        '''
        try:
            SETTINGS.database.connect()

            self.connect(QtGui.QApplication.instance(),
            QtCore.SIGNAL("db error"), self.advise_dl)

            self.connect(QtGui.QApplication.instance(),
            QtCore.SIGNAL("db notification"), self.advise)

            if SETTINGS.database.isOpen():
                message = u"%s<br /><b>%s</b><br />%s <b>%s</b>"% (
                _("sucessfully connected to"),
                SETTINGS.database.databaseName(), _("on server"),
                SETTINGS.database.hostName())
                self.advise(message)
                QtGui.QApplication.instance().emit(
                    QtCore.SIGNAL("db_connected"))
                self.diary_interface.refresh()
                self.set_users()
            else:
                raise ConnectionError("whoops")
        except ConnectionError as error:
            self.advise(u"%s<hr />%s"% (
                _("Connection Error"), error), 2)

    def set_users(self):
        self.status_widget.set_users()

    def user1_changed(self, user):
        SETTINGS.set_user1(user)

    def user2_changed(self, user):
        SETTINGS.set_user2(user)

    def disconnect_server(self, shutting_down=False):
        '''
        disconnect from server
        (if not connected - pass quietly).
        '''
        if SETTINGS.database and SETTINGS.database.isOpen():
            SETTINGS.database.close()

    def choose_connection(self):
        '''
        catches signal when user hits the connect action
        '''
        self.disconnect_server()
        connections = SETTINGS.connections
        dl = ConnectDialog(connections, self)

        if len(connections) != 1:
            if not dl.exec_():
                self.advise(_("working offline!"), 1)
                return
            if (not dl.chosen_connection.is_default and
            QtGui.QMessageBox.warning(self, _("confirm"),
            u"%s<br />%s"% (_("WARNING - this is NOT your default database."),
            _("only connect if you know what you are doing")),
            QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
            QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Cancel):
                self.choose_connection()
                return

        SETTINGS.database.from_connection_data(dl.chosen_connection)

        SETTINGS.set_connections(dl.known_connections)
        self.connect_server()

    def connect_signals(self):
        self.action_patient.triggered.connect(self.page_changer)
        self.action_diary.triggered.connect(self.page_changer)

        self.connect(self.patient_interface, QtCore.SIGNAL("Advise"),
            self.advise)

        self.connect(self.patient_interface, QtCore.SIGNAL("Patient Loaded"),
            self._patient_loaded)

        self.connect(self.patient_interface, QtCore.SIGNAL("Show Fee Widget"),
            self.add_dock_widget)

        self.connect(self.diary_interface, QtCore.SIGNAL("Advise"),
            self.advise)

        self.connect(self.status_widget, QtCore.SIGNAL("mode changed"),
            self.patient_interface.apply_mode)

        self.connect(self.status_widget, QtCore.SIGNAL("user1 changed"),
            self.user1_changed)

        self.connect(self.status_widget, QtCore.SIGNAL("user2 changed"),
            self.user2_changed)

        self.action_connect.triggered.connect(self.choose_connection)

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

        SETTINGS.PLUGIN_DIRS = qsettings.value(
            "plugin_dirs").toStringList()

    def saveSettings(self):
        BaseMainWindow.saveSettings(self)
        qsettings = QtCore.QSettings()

        #Qt settings

        # SETTINGS is a python dict of non qt-specific settings.
        # unfortunately.. QVariant.toPyObject can't recreate a dictionary
        # so best to pickle this
        pickled_dict = cPickle.dumps(SETTINGS.PERSISTANT_SETTINGS)
        qsettings.setValue("settings_dict", pickled_dict)
        qsettings.setValue("plugin_dirs", SETTINGS.PLUGIN_DIRS)

    def closeEvent(self, event=None):
        '''
        re-implement the close event of QtGui.QMainWindow, and check the user
        really meant to do this.
        '''
        self.is_dirty
        if (QtGui.QMessageBox.question(self, _("Confirm"),
        _("Quit Application?"),
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.No):
            event.ignore()
        else:
            self.saveSettings()
            self.disconnect_server(shutting_down=True)

    def page_changer(self):
        sender = self.sender()
        if sender == self.action_patient:
            i = 0
        elif sender == self.action_diary:
            i = 1
        self.stacked_widget.setCurrentIndex(i)

    def _patient_loaded(self, patient):
        '''
        updates the taskbar
        '''
        if patient:
            message = u"%s <b>%s</b>"% (_("editing"), patient.full_name)
        else:
            message = _("No Patient Loaded")
        self.status_label.setText(message)

    @property
    def preferences_dialog(self):
        if self._preferences_dialog is None:
            dl = self._preferences_dialog = PreferencesDialog(self)
            plugin_icon = QtGui.QIcon(":icons/plugins.png")

            plugins_pref = Preference(_("Plugins"))
            plugins_pref.setIcon(plugin_icon)
            pl_widg = client_widgets.PluginOptionsWidget(self)
            plugins_pref.setWidget(pl_widg)
            dl.insert_preference_dialog(0, plugins_pref)

            plugin_icon = QtGui.QIcon(":icons/plugins.png")
            plugins_dir_pref = Preference(_("Plugin Directories"))
            plugins_dir_pref.setIcon(plugin_icon)
            pl_dir_widg = client_widgets.PluginsDirectoryWidget(self)
            plugins_dir_pref.setWidget(pl_dir_widg)
            dl.insert_preference_dialog(0, plugins_dir_pref)

            connections_pref = Preference(_("Database Connections"))
            dl.cp_widg = ConnectionsPreferenceWidget(
                SETTINGS.connections, self)
            connections_pref.setWidget(dl.cp_widg)
            dl.insert_preference_dialog(0, connections_pref)

        return self._preferences_dialog

    def show_preferences_dialog(self):
        self.preferences_dialog.exec_()
        SETTINGS.set_connections(self.preferences_dialog.cp_widg.connections)

    def add_dock_widget(self, dw):
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dw)

def main():
    '''
    main entry point for lib_openmolar.client
    '''
    if not "-v" in sys.argv:
        logging.basicConfig(level = logging.info)

    app = RestorableApplication("openmolar-client")
    ui = ClientMainWindow()
    ui.show()
    app.exec_()
    app = None

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)

    sys.exit(main())
