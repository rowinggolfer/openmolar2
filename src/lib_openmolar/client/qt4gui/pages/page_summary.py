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

'''
Summary Page
============
Clinical summary page which is added to the patient interface

'''

from PyQt4 import QtCore, QtGui, QtWebKit

from lib_openmolar.client.qt4gui.client_widgets import *

from lib_openmolar.client.qt4gui.dialogs import (
    NewExamDialog, HygTreatmentDialog, XrayTreatmentDialog)

class SummaryPage(QtGui.QWidget):
    def __init__(self, chart_data_model, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.summary_chart = ChartWidgetSummary(chart_data_model, self)
        self.summary_chart.setMaximumHeight(220)

        self.summary_line_edit = SummaryLineEdit(self)

        self.notes_widget = NotesWidget(self)
        self.notes_widget.set_type(NotesWidget.CLINICAL)

        self.bpe_widget = BPEWidget()
        self.bpe_widget.setFocusPolicy(QtCore.Qt.NoFocus)

        self.treatment_summary = QtWebKit.QWebView(self)
        self.treatment_summary.setHtml("Treatment<br />Plan")
        self.treatment_summary.setMaximumWidth(150)

        self.menu_bar = QtGui.QToolBar(self)
        self.menu_bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        ## TODO placeholder icon
        icon = QtGui.QIcon.fromTheme("dialog-question")
        self.action_exam = QtGui.QAction(icon, _("Perform Exam"), self)
        self.menu_bar.addAction(self.action_exam)

        self.action_hygienist = QtGui.QAction(icon, "Hygienist Shortcuts", self)
        self.menu_bar.addAction(self.action_hygienist)

        self.action_xray = QtGui.QAction(icon, "X-ray Shortcuts", self)
        self.menu_bar.addAction(self.action_xray)

        self.menu_bar.addSeparator()
        self.action_fee = QtGui.QAction(icon, _("Show Fee Widget"), self)
        self.menu_bar.addAction(self.action_fee)

        middle_widget = QtGui.QWidget(self)
        middle_layout = QtGui.QVBoxLayout(middle_widget)
        middle_layout.setMargin(0)
        middle_layout.addWidget(self.summary_line_edit)
        middle_layout.addWidget(self.notes_widget)

        right_widget = QtGui.QWidget(self)
        right_layout = QtGui.QVBoxLayout(right_widget)
        right_layout.setMargin(0)
        right_layout.addWidget(self.bpe_widget)
        right_layout.addWidget(self.treatment_summary)

        layout = QtGui.QGridLayout(self)
        layout.setMargin(3)
        layout.setSpacing(3)
        layout.addWidget(self.summary_chart, 0, 0, 1, 2)
        layout.addWidget(middle_widget, 1, 0)
        layout.addWidget(right_widget, 1, 1)
        layout.addWidget(self.menu_bar, 2,0, 2, 1)

        layout.setRowStretch(0,3)
        layout.setRowStretch(1,3)
        layout.setRowStretch(2,0)

        self.set_enabled(False)
        self.connect_signals()

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def connect_signals(self):
        self.action_exam.triggered.connect(self.perform_exam)
        self.action_hygienist.triggered.connect(self.perform_hygienist)
        self.action_xray.triggered.connect(self.perform_xray)
        self.action_fee.triggered.connect(self._call_fee_widget)

        self.summary_line_edit.textEdited.connect(self.summary_updated)

    def clear(self):
        self.notes_widget.clear()
        self.treatment_summary.setHtml("")
        self.summary_chart.clear()
        self.summary_line_edit.clear()
        self.bpe_widget.clear()
        self.set_enabled(False)

    def set_enabled(self, enabled=True):
        self.action_exam.setEnabled(enabled)
        self.action_hygienist.setEnabled(enabled)
        self.action_xray.setEnabled(enabled)

    def _call_fee_widget(self):
        '''
        the "procedure codes" button has been pressed, emit a signal
        '''
        if __name__ == "__main__":
            print "calling fee widget"
        self.emit(QtCore.SIGNAL("Show Fee Widget"))

    def sync_static(self):
        '''
        connected to a signal from the charts page, helps keep summary
        and static on the same page
        '''
        sending_chart = self.sender()
        tooth = sending_chart.current_tooth
        if tooth is not None:
            self.summary_chart.set_current_tooth(tooth.tooth_id)

    def clear_static(self):
        '''
        connected to a signal from the charts page,
        treatment or completed chart have the input
        '''
        self.summary_chart.clear_selection()
        self.summary_chart.set_current_tooth(None)

    def load_patient(self):
        patient = SETTINGS.current_patient
        self.notes_widget.load_patient()
        self.treatment_summary.setHtml(patient.treatment_summary_html)

        self.summary_chart.set_known_teeth(patient.dent_key)
        self.summary_line_edit.setText(patient.clinical_memo)

        self.bpe_widget.set_values(patient.current_bpe)
        self.set_enabled()

        #NOTE - as the summary chart is a view of the static charts model..
        #restorations are not added here.

    def perform_exam(self):
        dl = NewExamDialog(self)
        if dl.exec_():
            message = "%s performed by %s"% (dl.proc_code,
                dl.chosen_practitioner.full_name)
            self.Advise(message)

    def perform_hygienist(self):
        dl = HygTreatmentDialog(self)
        if dl.exec_():
            message = "%s performed by %s"% (dl.proc_code,
                dl.chosen_practitioner.full_name)
            self.Advise(message)

    def perform_xray(self):
        dl = XrayTreatmentDialog(self)
        if dl.exec_():
            items = 0
            for code in dl.proc_codes:
                QtGui.QApplication.instance().emit(
                    QtCore.SIGNAL("proc code selected"), code)

                items += 1
            if items:
                self.Advise(u"%d %s"% (items, _("treatment items performed")))

    def summary_updated(self, text):
        self.emit(QtCore.SIGNAL("clinical_memo_changed"), text)


if __name__ == "__main__":
    from lib_openmolar.client.qt4gui.client_widgets.chart_widgets import ChartDataModel
    model = ChartDataModel()

    app = QtGui.QApplication([])
    from lib_openmolar.client.connect import ClientConnection

    cc = ClientConnection()
    cc.connect()

    dl = QtGui.QDialog()
    dl.setMinimumSize(400,200)
    layout = QtGui.QVBoxLayout(dl)

    csw = SummaryPage(model, dl)
    layout.addWidget(csw)
    dl.exec_()