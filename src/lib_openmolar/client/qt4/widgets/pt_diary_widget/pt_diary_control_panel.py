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

from PyQt4 import QtCore, QtGui

class PtDiaryControlPanel(QtGui.QWidget):
    '''
    buttons to set the
    '''
    find_signal = QtCore.pyqtSignal()
    schedule_signal = QtCore.pyqtSignal()
    cancel_signal = QtCore.pyqtSignal()
    modify_signal = QtCore.pyqtSignal()
    print_signal = QtCore.pyqtSignal()
    new_signal = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        #:
        self.shortcuts_button = QtGui.QPushButton(_("Appointment shortcuts"))
        #:
        self.new_button = QtGui.QPushButton(_("New"))
        #:
        self.cancel_button = QtGui.QPushButton(_("Cancel"))
        #:
        self.modify_button = QtGui.QPushButton(_("Modify"))
        #:
        self.schedule_button = QtGui.QPushButton(_("Schedule"))
        #:
        self.print_button = QtGui.QPushButton(_("Print Card"))
        #:
        self.find_button = QtGui.QPushButton(_("Show in Book"))


        layout = QtGui.QGridLayout(self)
        layout.setMargin(1)
        layout.addWidget(self.shortcuts_button,0,0,1,3)
        layout.addWidget(self.new_button,1,0)
        layout.addWidget(self.cancel_button,1,1)
        layout.addWidget(self.schedule_button,1,2)
        layout.addWidget(self.print_button,2,0)
        layout.addWidget(self.modify_button,2,1)
        layout.addWidget(self.find_button,2,2)

        self.find_button.clicked.connect(self.find_signal.emit)
        self.new_button.clicked.connect(self.new_signal.emit)
        self.cancel_button.clicked.connect(self.cancel_signal.emit)
        self.modify_button.clicked.connect(self.modify_signal.emit)
        self.schedule_button.clicked.connect(self.schedule_signal.emit)
        self.print_button.clicked.connect(self.print_signal.emit)

        self.shortcuts_button.clicked.connect(self.show_shortcuts_dialog)

    def show_shortcuts_dialog(self):
        QtGui.QMessageBox.information(self, "advise", "show shortcuts")


if __name__ == "__main__":
    from lib_openmolar import client
    app = QtGui.QApplication([])

    mw = QtGui.QMainWindow()

    pt_diary_control_panel = PtDiaryControlPanel()
    mw.setCentralWidget(pt_diary_control_panel)

    mw.show()
    app.exec_()
