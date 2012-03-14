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
from PyQt4 import QtGui, QtCore, QtWebKit

#class DetailsBrowser(QtGui.QTextBrowser):
class DetailsBrowser(QtWebKit.QWebView):
    '''
    this class provides a signal emitting browser for the patient_interface
    '''
    def __init__(self, parent=None):
        QtWebKit.QWebView.__init__(self, parent)

        self.linkClicked.connect(self._link_clicked)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Expanding)
        self.clear()

    def clear(self):
        self.setHtml(_("No Patient Loaded"))

    def emit_edit(self):
        self.emit(QtCore.SIGNAL("Edit Patient Details"))

    def emit_edit_address(self, index):
        self.emit(QtCore.SIGNAL("Edit Patient Address"), index)

    def emit_phone(self):
        self.emit(QtCore.SIGNAL("Edit Patient Phone"))

    def emit_memo(self):
        self.emit(QtCore.SIGNAL("Edit clerical memo"))

    def setHtml(self, html):
        QtWebKit.QWebView.setHtml(self, html)
        self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)

    def _link_clicked(self, url):
        val = url.toString()
        if val == "edit_pt":
            self.emit_edit()
        elif val.startsWith("edit_addy"):
            numbers = re.search("(\d+)", val)
            i = int(numbers.group()) if numbers else -1
            self.emit_edit_address(i)
        elif val.startsWith("edit_memo"):
            self.emit_memo()
        elif val.startsWith("edit_reg_dent"):
            numbers = re.search("(\d+)", val)
            i = int(numbers.group()) if numbers else -1
            print "edit reg dent %s"% numbers
            self.emit_phone()  ##TODO - this is simply to ensure a popup
        elif val.startsWith("edit_reg_hyg"):
            numbers = re.search("(\d+)", val)
            i = int(numbers.group()) if numbers else -1
            print "edit reg dent %s"% numbers
            self.emit_phone()  ##TODO - this is simply to ensure a popup
        elif val == "phone":
            self.emit_phone()  ##TODO - this is simply to ensure a popup
        else:
            print "unhandled link clicked in details Browser"
            print val
            self.emit_phone()  ##TODO - this is simply to ensure a popup


if __name__ == "__main__":
    def sig_catcher(*args):
        print "signal caught", args




    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import DemoClientConnection
    from lib_openmolar.client.db_orm.patient_wrapper import PatientModel


    cc = DemoClientConnection()
    cc.connect()

    patient = PatientModel(1)

    dl = QtGui.QDialog()

    db = DetailsBrowser(dl)

    db.setHtml(patient.details_html())

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(db)

    dl.connect(db, QtCore.SIGNAL('Edit Patient Details'), sig_catcher)
    dl.connect(db, QtCore.SIGNAL('Edit Patient Address'), sig_catcher)
    dl.connect(db, QtCore.SIGNAL('Edit Patient Phone'), sig_catcher)

    dl.exec_()
