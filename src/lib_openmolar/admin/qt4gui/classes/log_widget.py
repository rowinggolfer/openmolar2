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

from PyQt4 import QtCore, QtGui

from lib_openmolar.common.widgets import Advisor

class LogWidget(QtGui.QFrame, Advisor):
    '''
    provides a text edit with clear, save and print functions
    '''
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        Advisor.__init__(self)
        self.text_browser = QtGui.QTextBrowser()
        self.text_browser.setFont(QtGui.QFont("courier"))

        self.clear_button = QtGui.QPushButton()
        icon = QtGui.QIcon.fromTheme("edit-clear")
        self.clear_button.setIcon(icon)
        self.clear_button.setText(_("Clear"))

        save_button = QtGui.QPushButton()
        icon = QtGui.QIcon.fromTheme("document-save")
        save_button.setIcon(icon)
        save_button.setText(_("Save to file"))

        print_button = QtGui.QPushButton()
        icon = QtGui.QIcon.fromTheme("printer")
        print_button.setIcon(icon)
        print_button.setText(_("Print"))

        frame = QtGui.QFrame()
        layout = QtGui.QHBoxLayout(frame)
        layout.setMargin(0)
        spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding)
        layout.addItem(spacer)
        layout.addWidget(self.clear_button)
        layout.addWidget(save_button)
        layout.addWidget(print_button)

        layout = QtGui.QVBoxLayout(self)
        layout.setMargin(3)
        layout.setSpacing(2)
        layout.addWidget(self.text_browser)

        layout.addWidget(frame)

        self.clear_button.clicked.connect(self.clear)
        save_button.clicked.connect(self.save)
        print_button.clicked.connect(self.print_)

        self.dirty = False

    def log(self, message="", dirty=True):
        '''
        append message to the text in the browser
        '''
        self.text_browser.moveCursor(QtGui.QTextCursor.End)
        self.text_browser.insertPlainText(message + "\n")
        self.dirty = self.dirty or dirty

    def clear(self):
        if QtGui.QMessageBox.question(self, _("confirm"),
        _("Clear log text?"), QtGui.QMessageBox.Yes|QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
            self.text_browser.clear()
            self.dirty = False
            self.welcome()

    def welcome(self):
        if self.text_browser.document().toPlainText() == "":
            message = u"%s - %s\n\n"% (_("Welcome to OpenMolar-Admin"),
                QtCore.QDate.currentDate().toString())
            self.text_browser.setPlainText(message)

    def save(self):
        try:
            filepath = QtGui.QFileDialog.getSaveFileName(self,
            _("save log text"),"log.txt",
            _("text files ")+"(*.txt)")
            if filepath != '':
                if not re.match(".*\.txt$", filepath):
                    filepath += ".txt"
                f = open(filepath, "w")
                text = self.text_browser.document().toPlainText()
                f.write(text)
                f.close()
                self.advise(_("Log Saved"))
                self.dirty = False
            else:
                self.advise(_("Not Saved"))
        except Exception, e:
            self.advise(_("Log not saved")+" - %s"% e, 2)

    def print_(self):
        printer = QtGui.QPrinter()
        dl = QtGui.QPrintDialog(printer, self)
        if dl.exec_():
            self.text_browser.print_(printer)


if __name__ == "__main__":
    import gettext
    gettext.install("")

    app = QtGui.QApplication([])
    dl = QtGui.QDialog()

    obj = LogWidget(dl)

    layout = QtGui.QHBoxLayout(dl)
    layout.addWidget(obj)

    dl.exec_()
