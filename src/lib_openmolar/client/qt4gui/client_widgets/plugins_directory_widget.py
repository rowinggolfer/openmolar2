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


from PyQt4 import QtGui, QtCore

class PluginsDirectoryWidget(QtGui.QWidget):
    '''
    a widget, added at runtime to the preferences dialog,
    configures the use of plugins
    '''
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.label = QtGui.QLabel()
        self._update_label()
        button = QtGui.QPushButton(_("add a directory"))

        setting = SETTINGS.PERSISTANT_SETTINGS.get("compile_plugins", False)
        compile_naked_checkbox = QtGui.QCheckBox("%s"% (
            _("compile naked plugins found in these directories")))

        compile_naked_checkbox.setChecked(setting)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(button)
        layout.addStretch()
        layout.addWidget(compile_naked_checkbox)

        compile_naked_checkbox.toggled.connect(self.toggle_compilation)
        button.clicked.connect(self.add_directory)

    def _update_label(self):
        '''
        updates the label showing which directories are used
        '''
        message = u"%s"% _("Directories where Plugins Reside")
        if len(SETTINGS.PLUGIN_DIRS) == 0:
            message += "<br />None"
        else:
            message += "<ul>"
            for p_d in SETTINGS.PLUGIN_DIRS:
                message += "<li>%s</li>"% p_d
            message += "</ul>"

        self.label.setText(message)


    def toggle_compilation(self, arg):
        if arg:
            QtGui.QMessageBox.warning(self, _("are you sure"),
            u"%s %s<hr />%s"% (
            _("allowing unsigned code to run is a security risk"),
            _("but can be useful for plugin developers."),
    _("Only enable this feature if you are sure you know what you are doing")
        ))


        SETTINGS.PERSISTANT_SETTINGS["compile_plugins"] = arg

    def add_directory(self):
        new_dir = QtGui.QFileDialog.getExistingDirectory()
        if new_dir == "":
            return
        SETTINGS.PLUGIN_DIRS.append(new_dir)
        self._update_label()

if __name__ == "__main__":
    app = QtGui.QApplication([])
    w = PluginsDirectoryWidget()
    w.show()
    app.exec_()
