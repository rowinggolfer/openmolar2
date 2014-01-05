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

from lib_openmolar.common.qt4.widgets import ClosableTabWidget

from lib_openmolar.common.qt4.postgres.postgres_session_widget import \
    PostgresSessionWidget
from lib_openmolar.admin.qt4.classes import SqlQueryTable
from lib_openmolar.admin.qt4.classes.database_table import (
    DatabaseTableViewer,
    RelationalDatabaseTableViewer)

class AdminSessionWidget(PostgresSessionWidget):
    #:
    query_error = QtCore.pyqtSignal(object)

    #:
    query_sucess = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        self.sql_tools = []
        PostgresSessionWidget.__init__(self, parent)

    def setup_ui(self):
        layout = QtGui.QVBoxLayout(self)
        layout.setMargin(3)
        self.tab_widget = ClosableTabWidget()
        self.tab_widget.setTabsClosable(True)

        action_close = QtGui.QAction(_("Close Tabs"), self)
        self.connect(action_close, QtCore.SIGNAL("triggered()"),
            self.tab_widget.closeAll)

        action_new_table = QtGui.QAction(_("New Table Viewer"), self)
        action_new_table.triggered.connect(self._extra_table)

        action_new_query = QtGui.QAction(_("New Query Tool"), self)
        action_new_query.triggered.connect(self._extra_query)

        menu = QtGui.QMenu(self)
        menu.addAction(action_close)
        menu.addSeparator()
        menu.addAction(action_new_table)
        menu.addAction(action_new_query)

        icon = QtGui.QIcon.fromTheme("preferences-desktop")
        menu_button = QtGui.QToolButton(self)
        menu_button.setIcon(icon)
        menu_button.setText(_("Options"))
        menu_button.setPopupMode(menu_button.InstantPopup)
        menu_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        menu_button.setMenu(menu)

        self.tab_widget.setCornerWidget(menu_button)

        layout.addWidget(self.tab_widget)

        self.add_table()
        self.add_query_editor()

        self.tab_widget.currentChanged.connect(self.tab_selected)


    def update_status(self):
        '''
        let the user know the connection state
        '''
        brief, verbose = self.get_session_status()
        self.tab_widget.parent().setWindowTitle(brief)

    def _add_tool(self, tool):
        icon = QtGui.QIcon.fromTheme("text-x-generic")
        self.tab_widget.addTab(tool, icon, tool.name)
        self.connect(tool, QtCore.SIGNAL("Query Success"), self.emit_sucess)
        self.connect(tool, QtCore.SIGNAL("Query Error"), self.emit_error)

    def emit_sucess(self, message=None):
        LOGGER.debug("query_success %s"% message)
        self.query_sucess.emit(message)

    def emit_error(self, message=None):
        LOGGER.debug("query_error %s"% message)
        self.query_error.emit(message)

    def add_table(self):
        '''
        add a :doc:`RelationalDatabaseTableViewer`
        '''
        table = RelationalDatabaseTableViewer(self)
        self.sql_tools.append(table)
        self._add_tool(table)

    def add_query_editor(self):
        '''
        add a :doc:`SqlQueryTable`
        '''
        query_table = SqlQueryTable()
        self.sql_tools.append(query_table)
        self._add_tool(query_table)

    def _extra_table(self):
        self.add_table()
        self.set_session(self.pg_session)

    def _extra_query(self):
        self.add_query_editor()
        self.set_session(self.pg_session)

    def set_session(self, session):
        LOGGER.debug("AdminSessionWidget.set_session(%s)"% session)
        PostgresSessionWidget.set_session(self, session)
        for tool in self.sql_tools:
            tool.set_connection(session)

        self.tab_widget.parent().setWindowTitle(session.description)

    def tab_selected(self, tab):
        tab = self.tab_widget.currentWidget()
        if (tab and type(tab) == DatabaseTableViewer or
        type(tab) == RelationalDatabaseTableViewer) :
            tab.load_table_choice()

def _test():
    from lib_openmolar.admin.connect import DemoAdminConnection

    app = QtGui.QApplication([])
    session = DemoAdminConnection()
    session.connect()
    psw = AdminSessionWidget()
    psw.set_session(session)
    psw.update_status()
    psw.show()
    app.exec_()

if __name__ == "__main__":
    import logging
    LOGGER = logging.getLogger()

    import gettext
    gettext.install("openmolar")
    _test()
