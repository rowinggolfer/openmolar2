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
from lib_openmolar.admin.qt4gui.classes import LogWidget

class PlainTextDialog(QtGui.QDialog):
    '''
    useful for popping up lists which need to be displayed in fixed width font
    '''
    def __init__(self, message, parent=None):
        super(PlainTextDialog, self).__init__(parent)
        self.setWindowTitle(_("Plain Text Browser"))
        self.setMinimumWidth(800)
        layout = QtGui.QVBoxLayout(self)
        text_browser = LogWidget(self)
        text_browser.clear_button.setText(_("Close"))
        text_browser.clear_button.clicked.disconnect(text_browser.clear)
        text_browser.clear_button.clicked.connect(self.accept)
        text_browser.log(message)
        layout.addWidget(text_browser)

if __name__ == "__main__":
    pass
