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

class ClosableTabWidget(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(ClosableTabWidget, self).__init__(parent)
        self.setTabsClosable(True)
        self.connect(self, QtCore.SIGNAL("tabCloseRequested (int)"),
                                                    self.removeTab)

        closeAll_but = QtGui.QPushButton(_("Close All"), self)
        self.connect(closeAll_but, QtCore.SIGNAL("clicked()"), self.closeAll)
        self.setCornerWidget(closeAll_but)

        self.message_close = _("Close Tab")
        self.message_close_all = _("Close All Tabs?")

    def sizeHint(self):
        return QtCore.QSize(400,300)

    def closeAllWithoutQuestion(self):
        for i in range(self.count()):
            widg = self.widget(0)
            QtGui.QTabWidget.removeTab(self, 0)
            self.emit(QtCore.SIGNAL("Widget Removed"), widg)
        return True

    def closeAll(self, message=""):
        message += u" %s"% self.message_close_all
        if self.count() == 0:
            return True
        if QtGui.QMessageBox.question(self, "Confirm", message,
        QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
            return self.closeAllWithoutQuestion()

    def removeTab(self, i):
        if QtGui.QMessageBox.question(self, "Confirm",
        u"%s '%s'?"% (self.message_close, self.tabText(i)),
        QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
            widg = self.widget(i)
            QtGui.QTabWidget.removeTab(self, i)
            self.emit(QtCore.SIGNAL("Widget Removed"), widg)

if __name__ == "__main__":
    import gettext
    gettext.install("")

    app = QtGui.QApplication([])

    label1 = QtGui.QLabel("hello")
    label2 = QtGui.QLabel("world")

    object = ClosableTabWidget()
    object.addTab(label1, "tab one")
    object.addTab(label2, "tab two")

    object.show()
    app.exec_()
