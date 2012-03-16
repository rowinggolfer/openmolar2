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

from lib_openmolar.common.qt4.dialogs import PluginsDirectoryDialog

class PluginOptionsWidget(QtGui.QWidget):
    '''
    a widget to display and manage plugins
    '''
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        frame_left = QtGui.QFrame()
        frame_left.setFrameShape(QtGui.QFrame.StyledPanel)
        frame_right = QtGui.QFrame()

        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(frame_left)
        layout.addWidget(frame_right)

        label = QtGui.QLabel(_("Installed Plugins - check to Activate"))
        self.listwidget = QtGui.QListWidget(self)

        icon1 = QtGui.QIcon.fromTheme("help-about", QtGui.QIcon(""))
        icon2 = QtGui.QIcon.fromTheme("preferences-desktop", QtGui.QIcon(""))

        self.about_button = QtGui.QPushButton(icon1, _("&About Plugin"), self)
        self.about_button.setEnabled(False)

        self.config_button = QtGui.QPushButton(icon2, _("&Configure Plugin"),
            self)
        self.config_button.setEnabled(False)

        spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Minimum)

        butframe = QtGui.QFrame(self)
        hlayout = QtGui.QHBoxLayout(butframe)
        hlayout.addItem(spacer)
        hlayout.addWidget(self.about_button)
        hlayout.addWidget(self.config_button)

        layout = QtGui.QVBoxLayout(frame_left)
        layout.addWidget(label)
        layout.addWidget(self.listwidget)
        layout.addWidget(butframe)

        icon1 = QtGui.QIcon.fromTheme("applications-internet",
            QtGui.QIcon(":icons/applications-internet.png"))

        icon2 = QtGui.QIcon.fromTheme("system-file-manager")

        self.web_button = QtGui.QPushButton(icon1, _("Get Plugins online"),
            self)

        self.add_button = QtGui.QPushButton(icon2, _("Add &Plugins"), self)

        dir_button = QtGui.QPushButton(icon2, _("Plugin directories"))
        dir_button.clicked.connect(self.show_directory_dialog)

        layout = QtGui.QVBoxLayout(frame_right)
        layout.addWidget(self.web_button)
        layout.addWidget(self.add_button)
        layout.addStretch()
        layout.addWidget(dir_button)

        self.show_plugins()

    def show_plugins(self):

        self.listwidget.clear()
        for plugin in SETTINGS.plugins:
            item = QtGui.QListWidgetItem(self.listwidget)
            label = QtGui.QLabel()
            item.setText(plugin.name)
            item.setToolTip("<b>" + plugin.name + "</b><br />" +
                plugin.description)
            item.setIcon(plugin.icon)
            if plugin.is_active:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

    def show_directory_dialog(self):
        dl = PluginsDirectoryDialog(self)
        dl.exec_()

def _test():
    import __builtin__
    import gettext
    gettext.install("")

    class MockSettings(object):
        plugins = []
        PLUGIN_DIRS = ["/home/neil/openmolar/hg_openmolar/plugins/client",]

    __builtin__.SETTINGS = MockSettings()

    app = QtGui.QApplication([])
    w = PluginOptionsWidget()
    w.show()
    app.exec_()

if __name__ == "__main__":
    _test()