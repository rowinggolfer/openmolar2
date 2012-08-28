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

class StaticShortcutsFrame(QtGui.QWidget):
    '''
    provides buttons for common static chart editing by mouse
    '''
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.tm_button = QtGui.QPushButton(_("TM"))
        self.tm_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tm_button.setToolTip(_(u"tooth missing"))

        self.at_button = QtGui.QPushButton(_("AT"))
        self.at_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.at_button.setToolTip(_(u"denture tooth"))

        self.rt_button = QtGui.QPushButton(_("RT"))
        self.rt_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.rt_button.setToolTip(_(u"root treated"))

        layout = QtGui.QGridLayout(self)
        layout.setMargin(0)
        layout.setSpacing(2)
        layout.addWidget(self.tm_button,0,0)
        layout.addWidget(self.at_button,0,1)
        layout.addWidget(self.rt_button,0,2)

        self.rt_button.clicked.connect(self.emit_shortcut)
        self.at_button.clicked.connect(self.emit_shortcut)
        self.tm_button.clicked.connect(self.emit_shortcut)

    def sizeHint(self):
        return QtCore.QSize(200,60)

    def emit_shortcut(self):
        sender = self.sender()
        if sender == self.rt_button:
            shortcut = "RT"
        elif sender == self.at_button:
            shortcut = "AT"
        elif sender == self.tm_button:
            shortcut = "TM"
        self.emit(QtCore.SIGNAL("Shortcut"), shortcut)

if __name__ == "__main__":

    from lib_openmolar import client

    def sig_catcher(*args):
        print args

    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    layout = QtGui.QVBoxLayout(dl)
    obj2 = StaticShortcutsFrame(dl)

    dl.connect(obj2, QtCore.SIGNAL('Shortcut'), sig_catcher)

    layout.addWidget(obj2)

    dl.exec_()
