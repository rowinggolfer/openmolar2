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

from PyQt4 import QtGui

class UpperCaseLineEdit(QtGui.QLineEdit):
    '''
    A custom line edit that accepts only BLOCK LETTERS, regardless of
    caps lock and/or shift key.
    After experimentation, I found the least confusing way of presenting this
    to the user was to apply the change at the focusOutEvent.
    '''
    def __init__(self, parent=None):
        super(UpperCaseLineEdit,self).__init__(parent)

    def focusOutEvent(self, event):
        '''
        convert the text to upper case, and pass the signal on to the
        base widget
        '''
        self.setText(self.text().toUpper())
        QtGui.QLineEdit.focusOutEvent(self, event)

if __name__ == "__main__":
    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    object = UpperCaseLineEdit(dl)
    object2 = UpperCaseLineEdit(dl)

    layout = QtGui.QHBoxLayout(dl)
    layout.addWidget(object)
    layout.addWidget(object2)

    dl.exec_()