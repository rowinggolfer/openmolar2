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


from PyQt4 import QtCore, QtGui, QtWebKit
from lib_openmolar.client.messages import messages
from lib_openmolar.client.qt4.widgets import NotesWidget
from lib_openmolar.client.qt4.widgets import PtDiaryWidget

class ReceptionPage(QtGui.QWidget):
    def __init__(self, parent = None):
        super(ReceptionPage, self).__init__(parent)

        self.notes_widget = NotesWidget(self)
        self.notes_widget.set_type(NotesWidget.RECEPTION)

        self.menu_bar = QtGui.QToolBar()
        self.menu_bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        ## TODO placeholder icon
        icon = QtGui.QIcon.fromTheme("dialog-question")
        self.action_payment = QtGui.QAction(icon, "Take Payment", self)
        self.menu_bar.addAction(self.action_payment)

        right_widget =  QtGui.QLabel("Placeholder", self)
        right_widget.setMinimumWidth(100)
        right_widget.setMaximumWidth(150)

        self.pt_diary_widget = PtDiaryWidget()

        layout = QtGui.QGridLayout(self)
        layout.setMargin(3)
        layout.setSpacing(3)
        layout.addWidget(self.notes_widget, 0, 0)
        layout.addWidget(right_widget, 0, 1)
        layout.addWidget(self.pt_diary_widget, 1, 0, 1, 2)
        layout.addWidget(self.menu_bar, 2, 0, 1, 2)

        self.connect_signals()

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def connect_signals(self):
        self.action_payment.triggered.connect(self.payment_action)

    def clear(self):
        self.notes_widget.clear()
        self.pt_diary_widget.clear()

    def load_patient(self):
        patient = SETTINGS.current_patient
        self.notes_widget.load_patient()
        self.pt_diary_widget.load_patient()

    def payment_action(self):
        print "todo payment"
        self.Advise("take payment")

    def send_save_request(self):
        print "todo save clerical note"
        self.emit(QtCore.SIGNAL("Save Requested"))

if __name__ == "__main__":

    from lib_openmolar.client.connect import DemoClientConnection
    from lib_openmolar.client.db_orm import PatientModel

    app = QtGui.QApplication([])

    cc = DemoClientConnection()
    cc.connect()
    pt = PatientModel(1)
    SETTINGS.set_current_patient(pt)

    mw = QtGui.QMainWindow()
    mw.setMinimumSize(400,200)

    page_widget = ReceptionPage()
    mw.setCentralWidget(page_widget)
    mw.show()
    page_widget.load_patient()

    app.exec_()
