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

import re
from PyQt4 import QtGui, QtCore

class ChartLineEdit(QtGui.QLineEdit):
    '''
    A custom line edit that accepts only BLOCK LETTERS
    and is self aware when verification is needed
    override the keypress event for up and down arrow keys.
    '''
    def __init__(self, parent=None):
        super(ChartLineEdit, self).__init__(parent)

    def clear(self):
        '''
        clears the text
        '''
        self.setText("")

    @property
    def trimmed_text(self):
        return self.text().trimmed()

    def keyPressEvent(self, event):
        '''
        overrides QWidget's keypressEvent
        '''
        if event.key() == QtCore.Qt.Key_Space:
            self.emit(QtCore.SIGNAL("Navigate"), "stay")
        elif event.key() in (
            QtCore.Qt.Key_Down,
            QtCore.Qt.Key_Return):
                self.emit(QtCore.SIGNAL("Navigate"), "next")
        elif event.key() == QtCore.Qt.Key_Up:
            self.emit(QtCore.SIGNAL("Navigate"), "prev")
        else:
            inputT = event.text().toAscii()
            if re.match("[a-z]", inputT):
                #-- catch and overwrite any lower case
                event = QtGui.QKeyEvent(event.type(), event.key(),
                event.modifiers(), event.text().toUpper())
            QtGui.QLineEdit.keyPressEvent(self,event)

if __name__ == "__main__":

    def sig_catcher(*args):
        print "signal caught", args

    app = QtGui.QApplication([])
    object = ChartLineEdit()
    app.connect(object, QtCore.SIGNAL("Navigate"), sig_catcher)

    object.show()
    app.exec_()