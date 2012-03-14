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
provides a lineEdit with a sounds like checkbox
'''

from PyQt4 import QtGui, QtCore
from lib_openmolar.client import qrc_resources

class SoundexLineEdit(QtGui.QWidget):
    def __init__(self, parent=None):
        super(SoundexLineEdit, self).__init__(parent)

        self.line_edit = QtGui.QLineEdit(self)

        icon = QtGui.QIcon(':icons/soundex.svg')
        self.cb = QtGui.QCheckBox(self)
        self.cb.setIcon(icon)

        self.cb.setToolTip(_("check to search for a similar sounding name"))

        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.cb)

        ## give this class selected attributes from the enclosed widgets

        self.cursorPositionChanged = self.line_edit.cursorPositionChanged
        self.text = self.line_edit.text
        self.setText = self.line_edit.setText
        self.setFocus = self.line_edit.setFocus
        self.editingFinished = self.line_edit.editingFinished
        self.setCompleter = self.line_edit.setCompleter

        self.isChecked = self.cb.isChecked
        self.setChecked = self.cb.setChecked
        self.cb.hide()

    def show_soundex(self, visible):
        self.cb.setVisible(visible)

if __name__ == "__main__":

    app = QtGui.QApplication([])
    sw = SoundexLineEdit()
    sw.show_soundex(True)
    sw.show()
    app.exec_()
