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


from PyQt4 import QtCore, QtGui, QtWebKit
from lib_openmolar.client.messages import messages



class NotesPage(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.patient = None

        self.notes_browser = QtWebKit.QWebView(self)
        self.notes_browser.setHtml(messages.welcome_html(
            self.notes_browser.width()))

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.notes_browser)

        self.is_loaded = False

    def sizeHint(self):
        return QtCore.QSize(400,400)

    def clear(self):
        self.notes_browser.setHtml(messages.welcome_html(
            self.notes_browser.width()))
        self.is_loaded = False

    def minimumSizeHint(self):
        return QtCore.QSize(300,300)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def update_patient(self):
        if not self.patient:
            return

    def load_patient(self):
        patient = SETTINGS.current_patient
        if patient and not self.is_loaded:
            self.notes_browser.setHtml(patient.notes_summary_html)
            self.is_loaded = True

class _TestDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(_TestDialog, self).__init__(parent)

        self.page = NotesPage(self)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.page)

if __name__ == "__main__":


    app = QtGui.QApplication([])
    dl = _TestDialog()
    dl.exec_()
