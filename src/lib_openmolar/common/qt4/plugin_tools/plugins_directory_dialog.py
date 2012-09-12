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
from lib_openmolar.common.qt4.dialogs import ExtendableDialog

class _directory_model(QtCore.QAbstractTableModel):
    advanced = False
    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.icon = QtGui.QIcon.fromTheme("folder")

    def data(self, index, role=QtCore.Qt.DisplayRole):
        dirname = SETTINGS.PLUGIN_DIRS[index.row()]
        if index.column() == 0:
            if role == QtCore.Qt.DisplayRole:
                return dirname
            if role == QtCore.Qt.DecorationRole:
                return self.icon
        if index.column() == 1:
            if dirname != SETTINGS.PLUGIN_DIRS[-1]:
                return None
            if role == QtCore.Qt.DisplayRole:
                return _("allow")
            if role == QtCore.Qt.CheckStateRole:
                if SETTINGS.ALLOW_NAKED_PLUGINS:
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked

    def headerData(self, index, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Vertical:
            return
        if role == QtCore.Qt.DisplayRole:
            if index == 0:
                return _("Directory")
            elif index == 1:
                return _("Naked Plugins")

    def rowCount(self, index):
        return len(SETTINGS.PLUGIN_DIRS)

    def columnCount(self, index):
        return 2 if self.advanced else 1

class _TableView(QtGui.QTableView):
    '''
    a clickable table view allowing editing of the directories
    '''
    updated = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtGui.QTableView.__init__(self, parent)

        self.clicked.connect(self.handle_click)

    def handle_click(self, index):
        if index.column() == 1:
            dirname = SETTINGS.PLUGIN_DIRS[index.row()]
            if dirname == SETTINGS.PLUGIN_DIRS[-1]:
                self.toggle_naked(dirname)

    def toggle_naked(self, dirname):
        if not SETTINGS.ALLOW_NAKED_PLUGINS:
            SETTINGS.ALLOW_NAKED_PLUGINS = (
            QtGui.QMessageBox.warning(self, _("are you sure"),
                u"%s %s<hr />%s"% (
                _("allowing unsigned code to run is a security risk"),
                _("but can be useful for plugin developers."),
    _("Only enable this feature if you are sure you know what you are doing")
            ), QtGui.QMessageBox.Cancel|QtGui.QMessageBox.Ok,
            QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Ok)

        else:
            SETTINGS.ALLOW_NAKED_PLUGINS = False
        self.updated.emit()

class PluginsDirectoryDialog(ExtendableDialog):
    '''
    a widget, added at runtime to the preferences dialog,
    configures the use of plugins
    '''
    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent)

        self.label = QtGui.QLabel()

        self.model = _directory_model()

        list_view = _TableView()

        self.insertWidget(self.label)
        self.insertWidget(list_view)

        self.apply_but.hide()
        self.set_reject_button_text(_("Close"))

        self._update()
        list_view.setModel(self.model)
        list_view.updated.connect(self._update)

        label = QtGui.QLabel(_("Naked Plugins management Enabled"))
        self.add_advanced_widget(label)
        self.more_but.toggled.connect(self.toggle_naked)

    def _update(self):
        '''
        updates the label showing which directories are used
        '''
        if len(SETTINGS.PLUGIN_DIRS) == 0:
            message = _("No plugin Directories set")
        else:
            message = _("Directories where Plugins Reside")

        self.model.reset()
        self.label.setText(message)

    def sizeHint(self):
        return QtCore.QSize(400,400)

    def toggle_naked(self, value):
        self.model.advanced = value
        self._update()

def _test():
    from lib_openmolar import client

    app = QtGui.QApplication([])
    dl = PluginsDirectoryDialog()
    dl.exec_()

if __name__ == "__main__":
    _test()
