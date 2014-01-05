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

from lib_openmolar.client.db_orm.table_models.patient_diary_model import \
    PatientDiaryModel

from pt_diary_control_panel import PtDiaryControlPanel
from appt_prefs_dialog import ApptPrefsDialog
from new_appt_dialog import NewApptDialog

class PtDiaryWidget(QtGui.QWidget):
    '''
    A widget to display a patients appointments.
    '''
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        #:
        self.model = PatientDiaryModel()
        #:
        self.tree_view = QtGui.QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setAlternatingRowColors(True)

        #:
        self.memo_line_edit = QtGui.QLineEdit()
        #:
        self.appt_prefs_button = QtGui.QPushButton(_(u"Recall Settings"))

        #:
        self.control_panel = PtDiaryControlPanel()

        layout = QtGui.QGridLayout(self)
        layout.addWidget(self.memo_line_edit,0,0)
        layout.addWidget(self.appt_prefs_button,0,1)

        layout.addWidget(self.tree_view,1,0)
        layout.addWidget(self.control_panel,1,1)

        self.appt_prefs_button.clicked.connect(
            self.raise_appt_prefs_dialog)

        self.control_panel.new_signal.connect(self.raise_new_appt_dialog)
        self.control_panel.modify_signal.connect(self.raise_modify_appt_dialog)
        self.control_panel.cancel_signal.connect(self.raise_cancel_appt_dialog)

    def clear(self):
        self.model.clear()

    def load_patient(self):
        LOGGER.debug("PtDiaryWidget.load_patient")
        self.model.set_patient(SETTINGS.current_patient.patient_id)

    #@property
    def selected_appointment(self):
        index = self.tree_view.currentIndex()
        if index.isValid():
            appt = self.model.data(index, role = QtCore.Qt.UserRole)
            LOGGER.debug(appt)
            return appt
        return None

    def raise_appt_prefs_dialog(self):
        dl = ApptPrefsDialog(self)
        dl.exec_()

    def raise_new_appt_dialog(self):
        dl = NewApptDialog(self)
        if dl.exec_():
            print "insert new appointment"
            ix = self.model.insert_appointment(
                SETTINGS.current_patient.patient_id,
                dl.trt1,
                dl.trt2,
                dl.length,
                dl.memo,
                dl.selected_clinician_id
                )
            self.model.refresh()
            if dl.schedule_now:
                print "and schedule appointment where ix='%s' now"% ix

    def raise_modify_appt_dialog(self):
        appt = self.selected_appointment()
        if appt is None:
            return
        dl = NewApptDialog(self)
        dl.set_appt_params(appt)
        if dl.exec_():
            print "modify appointment", appt
            result = self.model.modify_appointment(
                appt.apptix,
                dl.trt1,
                dl.trt2,
                dl.length,
                dl.memo,
                dl.selected_clinician_id
                )
            self.model.refresh()
            if not result:
                raise IOError ("unable to modify appointment")
            if dl.schedule_now:
                print "and schedule appointment where ix='%s' now"% ix

    def raise_cancel_appt_dialog(self):
        appt = self.selected_appointment()
        if appt is None:
            pass
        elif not appt.is_unscheduled:
            QtGui.QMessageBox.information(self, _("Information"),
            _("unable to cancel as appointment is scheduled"))
        elif QtGui.QMessageBox.question(self, _("Confirm"),
        u"%s %s"% (_("delete appt"), appt),
        QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Ok:
            self.model.remove_appointment(appt.apptix)
            self.model.refresh()

if __name__ == "__main__":

    from lib_openmolar.client.connect import DemoClientConnection
    from lib_openmolar.client.db_orm import PatientModel

    from lib_openmolar.common.qt4.widgets import SignallingApplication
    app = SignallingApplication("test_application")

    cc = DemoClientConnection()
    cc.connect()

    mw = QtGui.QMainWindow()
    mw.setMinimumSize(600,200)

    pt_diary_widget = PtDiaryWidget()
    pt = PatientModel(1)
    SETTINGS.set_current_patient(pt)

    pt_diary_widget.load_patient()

    mw.setCentralWidget(pt_diary_widget)
    mw.show()
    app.exec_()
