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

from PyQt4 import QtGui

class ProgressWidget(QtGui.QWidget):
    '''
    A progressbar with a label.
    '''
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self)
        self.progress_bar = QtGui.QProgressBar()
        self.label = QtGui.QLabel()
        self.label.setMinimumWidth(150)

        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)

        self.value = self.progress_bar.value
        self.setValue = self.progress_bar.setValue
        self.setText = self.label.setText

if __name__ == "__main__":
    app = QtGui.QApplication([])
    obj = ProgressWidget()
    obj.setText("hello world")
    obj.setValue(10)
    obj.show()
    app.exec_()