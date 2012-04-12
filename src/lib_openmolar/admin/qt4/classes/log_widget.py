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

import logging
import re
import traceback

from PyQt4 import QtCore, QtGui

from lib_openmolar.common.qt4.widgets import Advisor

class LogWidget(QtGui.QFrame, Advisor):
    '''
    provides a text edit with clear, save and print functions
    '''
    def __init__(self, logger=None, parent=None):
        QtGui.QFrame.__init__(self, parent)
        Advisor.__init__(self)

        self.init_logger(logger)

        self.text_browser = QtGui.QTextEdit()
        self.text_browser.setReadOnly(True)
        self.text_browser.viewport().setStyleSheet("background-color:black")
        self.text_browser.setTextColor(QtGui.QColor(QtCore.Qt.white))
        self.text_browser.setFont(QtGui.QFont("courier", 10))
        self.text_browser.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        
        verbosity_box = QtGui.QComboBox(self)
        verbosity_box.addItems([
            _("Verbosity"), "DEBUG (%s)"%_("maximum"),
            "INFO (%s)"%_("default"), "WARNING (%s)"%_("minimum")])
        verbosity_box.currentIndexChanged.connect(self.set_verbosity)

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
        layout.addWidget(verbosity_box)
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
    
        #use the signal/slot mechanism to ensure thread safety.
        self.connect(self, QtCore.SIGNAL("LOG"), self._log)
        self.connect(self, QtCore.SIGNAL("EXC"), self._exc)

        self.dirty = False

    def sizeHint(self):
        return QtCore.QSize(500, 150)

    def log_handler(self, record, dirty=True):
        '''
        append message to the text in the browser
        record has the following attrs..
        'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName',
        'getMessage', 'levelname', 'levelno', 'lineno', 'module', 'msecs',
        'msg', 'name', 'pathname', 'process', 'processName',
        'relativeCreated', 'thread', 'threadName'
        '''
        
        #if record.threadName != "MainThread":
        #    message = "Thread : "
        if record.exc_info:
            self.emit(QtCore.SIGNAL("EXC"), 
            "EXCEPTION:\n%s"% (traceback.format_exc()))
        else:
            message = "%s %s"% (
                record.levelname.ljust(8), record.getMessage())
            self.emit(QtCore.SIGNAL("LOG"), message)
        
        self.dirty = self.dirty or dirty
        
    def _log(self, message):
        self.text_browser.append(message)
        vsb = self.text_browser.verticalScrollBar()
        vsb.setValue(vsb.maximum())
    
    def _exc(self, message):
        self.text_browser.setTextColor(QtGui.QColor(QtCore.Qt.red))
        self._log(message)
        self.text_browser.setTextColor(QtGui.QColor(QtCore.Qt.white))
        
    def set_verbosity(self, level):
        '''
        alters the level of the logger
        '''
        if level == 1: #max
            self.logger.setLevel(logging.DEBUG)
            self.logger.info("Changed verbosity level to DEBUG")
        elif level == 3: #min
            self.logger.setLevel(logging.WARNING)
            self.logger.warning("Changed verbosity level to WARNING")
        else:
            self.logger.setLevel(logging.INFO)
            self.logger.info("Changed verbosity level to INFO")

    def init_logger(self, logger):
        if logger == None:
            logging.basicConfig(level = logging.DEBUG)
            logger = logging.getLogger("test logger")
        self.logger = logger
        handler = logging.StreamHandler()
        handler.emit = self.log_handler
        logger.addHandler(handler)

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

def _test():
    def log_stuff():
        obj.logger.info("random message.."*20)

    def raise_stuff():
        try:
            1/0 # this line will purposefully produce an exception
        except ZeroDivisionError as exc:
            obj.logger.exception(exc)
        
    app = QtGui.QApplication([]) 
    mw = QtGui.QMainWindow()
    obj = LogWidget()

    but = QtGui.QPushButton("send info to the log")
    but.clicked.connect(log_stuff)
    
    err_but = QtGui.QPushButton("raise an exception")
    err_but.clicked.connect(raise_stuff)

    frame = QtGui.QFrame()
    layout = QtGui.QVBoxLayout(frame)
    layout.addWidget(but)
    layout.addWidget(err_but)
    layout.addWidget(obj)

    mw.setCentralWidget(frame)
    mw.show()
    app.exec_()

if __name__ == "__main__":
    import gettext
    gettext.install("")
    _test()
