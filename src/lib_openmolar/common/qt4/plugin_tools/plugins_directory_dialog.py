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
        self.delete_icon = QtGui.QIcon(":icons/eraser.png")

    def data(self, index, role=QtCore.Qt.DisplayRole):
        dirname = SETTINGS.PLUGIN_DIRS[index.row()]
        if index.column() == 0:
            if role == QtCore.Qt.DisplayRole:
                return dirname
            if role == QtCore.Qt.DecorationRole:
                return self.icon
        if index.column() == 1:
            if role == QtCore.Qt.DecorationRole:
                return self.delete_icon
        if index.column() == 2:
            if role == QtCore.Qt.DisplayRole:
                return _("allow")
            if role == QtCore.Qt.CheckStateRole:
                if dirname in SETTINGS.NAKED_PLUGIN_DIRS:
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
                return _("Remove")
            elif index == 2:
                return _("Naked Plugins")

    def rowCount(self, index):
        return len(SETTINGS.PLUGIN_DIRS)

    def columnCount(self, index):
        return 3 if self.advanced else 2

class _TableView(QtGui.QTableView):
    '''
    a clickable table view allowing editing of the directories
    '''
    updated = QtCore.pyqtSignal()
    warning_given = False
    def __init__(self, parent=None):
        QtGui.QTableView.__init__(self, parent)

        self.clicked.connect(self.handle_click)

    def handle_click(self, index):
        dirname = SETTINGS.PLUGIN_DIRS[index.row()]
        if index.column() == 1:
            self.confirm_delete(dirname)
        if index.column() == 2:
            self.toggle_naked(dirname)

    def confirm_delete(self, dirname):
        if QtGui.QMessageBox.question(self, _("confirm"),
        u"%s<br /><b>%s</b> ?" %(
        _("no longer load plugins from directory") , dirname),
        QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Ok) == QtGui.QMessageBox.Ok:
            for s_list in (SETTINGS.PLUGIN_DIRS, SETTINGS.NAKED_PLUGIN_DIRS):
                try:
                    s_list.remove(dirname)
                except ValueError:
                    pass
        self.updated.emit()

    def toggle_naked(self, dirname):
        if dirname not in SETTINGS.NAKED_PLUGIN_DIRS:
            if not self.warning_given:
                QtGui.QMessageBox.warning(self, _("are you sure"),
                u"%s %s<hr />%s"% (
                _("allowing unsigned code to run is a security risk"),
                _("but can be useful for plugin developers."),
    _("Only enable this feature if you are sure you know what you are doing")
            ))
                self.warning_given = True
                return
            SETTINGS.NAKED_PLUGIN_DIRS.append(dirname)
        else:
            SETTINGS.NAKED_PLUGIN_DIRS.remove(dirname)
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

        button = QtGui.QPushButton(_("add a directory"))
        list_view = _TableView()

        self.insertWidget(self.label)
        self.insertWidget(list_view)
        self.insertWidget(button)
        button.clicked.connect(self.add_directory)

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

    def add_directory(self):
        new_dir = QtGui.QFileDialog.getExistingDirectory()
        if new_dir == "":
            return
        SETTINGS.PLUGIN_DIRS.append(new_dir)
        self._update()

    def sizeHint(self):
        return QtCore.QSize(400,400)

    def toggle_naked(self, value):
        self.model.advanced = value
        self._update()

def _test():
    from lib_openmolar import client
    SETTINGS.PLUGIN_DIRS = ["../../../../../plugins/client"]

    app = QtGui.QApplication([])
    dl = PluginsDirectoryDialog()
    dl.exec_()

if __name__ == "__main__":
    _test()
