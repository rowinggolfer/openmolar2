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

'''
provides a widget for seting the current users and "mode" which determines
whether to default to the surgery or reception page on load.
'''

from PyQt4 import QtGui, QtCore


class StatusBarWidget(QtGui.QWidget):
    '''
    a layout of comboBoxes for seting the current users
    and "mode" which determines
    whether to default to the surgery or reception page on load
    emits signals
    -user1 changed (int)
    -user2 changed (int)
    -mode changed (int)
    '''
    def __init__(self, parent=None):
        super(StatusBarWidget, self).__init__(parent)

        self.user1_combo_box = QtGui.QComboBox(self)
        self.user1_combo_box.addItems(["USER1","-"])

        self.user2_combo_box = QtGui.QComboBox(self)
        self.user2_combo_box.addItems(["USER2","-"])
        self.user2_combo_box.setCurrentIndex(1)

        self.mode_combo_box = QtGui.QComboBox(self)
        self.mode_combo_box.addItems([_("Reception Mode"), _("Surgery Mode")])

        sepline = QtGui.QFrame(self)
        sepline.setFrameShape(QtGui.QFrame.VLine)
        sepline.setFrameShadow(QtGui.QFrame.Sunken)

        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)

        layout.addWidget(self.user1_combo_box)
        layout.addWidget(self.user2_combo_box)
        layout.addWidget(sepline)
        layout.addWidget(self.mode_combo_box)

        mode = SETTINGS.PERSISTANT_SETTINGS.get("mode", 0)
        self.mode_combo_box.setCurrentIndex(mode)

        self.user1_combo_box.currentIndexChanged.connect(self.emit_user1)
        self.user2_combo_box.currentIndexChanged.connect(self.emit_user2)
        self.mode_combo_box.currentIndexChanged.connect(self.emit_mode)

    def set_mode(self, mode):
        self.mode_combo_box.setCurrentIndex(mode)

    def emit_mode(self, cb_index):
        '''
        is 0 if reception mode, 1 if surgery mode
        '''
        SETTINGS.PERSISTANT_SETTINGS["mode"] = cb_index
        self.emit(QtCore.SIGNAL("mode changed"), cb_index)

    def set_users(self, users):
        self.user1_combo_box.clear()
        self.user1_combo_box.addItems(users.abbrv_name_list)

        self.user2_combo_box.clear()
        self.user2_combo_box.addItems(["-"] + users.abbrv_name_list)

    def emit_user1(self, cb_index):
        self.emit(QtCore.SIGNAL("user1 changed"), cb_index)

    def emit_user2(self, cb_index):
        self.emit(QtCore.SIGNAL("user2 changed"), cb_index)


if __name__ == "__main__":
    
    

    app = QtGui.QApplication([])
    sw = StatusBarWidget()
    sw.show()
    app.exec_()
