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

from PyQt4 import QtCore, QtGui

from lib_openmolar.common.qt4.widgets.closeable_tab_widget \
    import ClosableTabWidget
from lib_openmolar.admin.qt4.classes.known_server_widget \
    import KnownServerWidget

class AdminTabWidget(ClosableTabWidget):
    '''
    a minor re-implementation of the closeabletabwidget from openmolar common
    uses a toolbutton as the right widget, and has some custom signals
    '''
    def __init__(self, parent=None):
        super(AdminTabWidget, self).__init__(parent)

        action_close = QtGui.QAction(_("Close Tabs"), self)
        action_close.triggered.connect(self.closeAll)

        action_new_table = QtGui.QAction(_("New Table Viewer"), self)
        action_new_table.triggered.connect(self.new_table)

        action_new_query = QtGui.QAction(_("New Query Tool"), self)
        action_new_query.triggered.connect(self.new_query)

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

        self.setCornerWidget(menu_button)

        self.currentChanged.connect(self._tab_changed)

        self.known_server_widget = KnownServerWidget()
        self.addTab(self.known_server_widget, _("Known Servers"))

        self.toggle_tabbar()

    def closeAll(self):
        '''
        re-implement the base class method
        '''
        result = self.count() <= 1
        if self.count() > 1:
            result = ClosableTabWidget.closeAll(self, _("Disconnect and"))
            if result:
                self.addTab(self.known_server_widget, _("Known Servers"))
                LOGGER.debug("emitting end_pg_session signal")
                self.emit(QtCore.SIGNAL("end_pg_session"))
        self.toggle_tabbar()
        return result

    def _tab_changed(self, i):
        try:
            ## if the current widget is a query tool, the query history
            ## may have been updated by another instance
            self.widget(i).get_history()
        except AttributeError:
            ## fail quietly!
            pass

    def new_query(self):
        self.emit(QtCore.SIGNAL("new query tab"))

    def new_table(self):
        self.emit(QtCore.SIGNAL("new table tab"))

    def addTab(self, *args):
        ClosableTabWidget.addTab(self, *args)
        self.toggle_tabbar()

    def removeTab(self, i):
        ClosableTabWidget.removeTab(self, i)
        self.toggle_tabbar()

    def toggle_tabbar(self):
        pass
        #self.tabBar().setVisible(self.count()>1)


def _test():
    import gettext
    gettext.install("")

    app = QtGui.QApplication([])
    mw = QtGui.QMainWindow()

    atw = AdminTabWidget()

    label1 = QtGui.QLabel("Placeholder1")
    label2 = QtGui.QLabel("Placeholder2")
    atw.addTab(label1, "one")
    atw.addTab(label2, "two")

    mw.setCentralWidget(atw)
    mw.show()
    app.exec_()

if __name__ == "__main__":
    _test()