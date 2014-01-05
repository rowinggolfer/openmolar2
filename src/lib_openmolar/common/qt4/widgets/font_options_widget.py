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

from PyQt4 import QtGui, QtCore

class FontOptionsWidget(QtGui.QWidget):
    '''
    a widget, added at runtime to the preferences dialog,
    standard fonts dialog
    '''
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        try:
            self.systemFont = parent.system_font
            self.initialFont = parent.font()
        except AttributeError:
            font = QtGui.QApplication.instance().font()
            self.systemFont = font
            self.initialFont = font

        self.fontdialog = QtGui.QFontDialog()
        self.fontdialog.setCurrentFont(self.initialFont)
        self.fontdialog.setOption(self.fontdialog.NoButtons)

        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.addButton(buttonBox.Apply)
        self.resetBut = buttonBox.addButton(_("Reset to Original Font"),
            buttonBox.RejectRole)
        self.systemBut = buttonBox.addButton(_("Use System Font"),
            buttonBox.ResetRole)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.fontdialog)

        layout.addWidget(buttonBox)

        self.connect(buttonBox, QtCore.SIGNAL("clicked (QAbstractButton *)"),
            self.apply)

    def apply(self, but):
        if but == self.resetBut:
            self.fontdialog.setCurrentFont(self.initialFont)
        elif but == self.systemBut:
            self.fontdialog.setCurrentFont(self.systemFont)
        QtGui.QApplication.instance().setFont(self.fontdialog.currentFont())

def _test():
    app = QtGui.QApplication([])
    widg = FontOptionsWidget()
    widg.show()
    app.exec_()

if __name__ == "__main__":
    import gettext
    gettext.install("")
    _test()
