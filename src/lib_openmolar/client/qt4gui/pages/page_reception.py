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
from lib_openmolar.client.qt4gui.client_widgets import NotesWidget

from lib_openmolar.client.db_orm.table_models.patient_diary_model import \
    PatientDiaryModel

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

        self.action_new_appointment = QtGui.QAction(icon, "New Appointment", self)
        self.menu_bar.addAction(self.action_new_appointment)

        self.appointment_model = PatientDiaryModel()

        appointment_table = QtGui.QTableView()
        appointment_table.setModel(self.appointment_model)


        right_widget =  QtGui.QLabel("Placeholder", self)
        right_widget.setMinimumWidth(100)
        right_widget.setMaximumWidth(150)

        layout = QtGui.QGridLayout(self)
        layout.setMargin(3)
        layout.setSpacing(3)
        layout.addWidget(self.notes_widget, 0, 0)
        layout.addWidget(right_widget, 0, 1)
        layout.addWidget(appointment_table, 1, 0, 1, 2)
        layout.addWidget(self.menu_bar, 2, 0, 1, 2)

        self.connect_signals()

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def connect_signals(self):
        self.action_payment.triggered.connect(self.payment_action)
        self.action_new_appointment.triggered.connect(self.new_appointment_action)

    def clear(self):
        self.notes_widget.clear()
        self.appointment_model.set_patient(0)

    def load_patient(self):
        patient = SETTINGS.current_patient
        self.notes_widget.load_patient()
        self.appointment_model.set_patient(SETTINGS.current_patient.patient_id)

    def payment_action(self):
        print "todo payment"
        self.Advise("take payment")

    def new_appointment_action(self):
        self.emit(QtCore.SIGNAL("db notify"), "todays_book_changed")
        self.Advise("new appointment")

    def send_save_request(self):
        print "todo save clerical note"
        self.emit(QtCore.SIGNAL("Save Requested"))


if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    app = QtGui.QApplication([])

    cc = ClientConnection()
    cc.connect()

    dl = QtGui.QDialog()
    dl.setMinimumSize(400,200)
    layout = QtGui.QVBoxLayout(dl)

    csw = ReceptionPage(dl)
    layout.addWidget(csw)
    dl.exec_()