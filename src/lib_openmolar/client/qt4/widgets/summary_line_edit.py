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
provides a lineEdit with an attention grabbing look
'''

from PyQt4 import QtGui, QtCore
from lib_openmolar.client.qt4.colours import colours

class SummaryLineEdit(QtGui.QLineEdit):
    '''
    a line edit which is in a prominent place on both Reception and
    clinical pages.
    '''
    def __init__(self, parent=None):
        super(SummaryLineEdit, self).__init__(parent)

        palette = QtGui.QPalette(self.palette())

        ###################################################
        ##   tried a yellow background.. didn't like it! ##
        ###################################################
        #brush = QtGui.QBrush(colours.REQUIRED_FIELD)
        #palette.setBrush(QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(colours.BOLD_TEXT)
        palette.setBrush(QtGui.QPalette.Text, brush)
        self.setPalette(palette)

        font = QtGui.QFont(self.font())
        font.setBold(True)
        font.setItalic(True)
        font.setPointSize(font.pointSize()+2)
        self.setFont(font)

    def clear(self):
        self.setText("")


if __name__ == "__main__":
    
    

    app = QtGui.QApplication([])
    sw = SummaryLineEdit()
    sw.show()
    app.exec_()
