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

from lib_openmolar.client.qt4gui import client_widgets


class ChartsPage(QtGui.QWidget):
    def __init__(self, parent = None):
        super(ChartsPage, self).__init__(parent)

        self.patient = None
        self.static = client_widgets.ChartWidgetStatic(None, self)

        #: a pointer to the :doc:`ChartDataModel` of the static chart
        self.static_chart_model = self.static.chart_data_model

        self.tx_pl_model = SETTINGS.treatment_model.tooth_tx_plan_model
        self.treatment = client_widgets.ChartWidgetTreatment(
            self.tx_pl_model, self)

        tx_model = SETTINGS.treatment_model.tooth_tx_cmp_model
        self.completed = client_widgets.ChartWidgetCompleted(tx_model, self)

        self.tooth_data_editor = client_widgets.ToothDataEditor(self)

        right_widget = QtGui.QWidget(self)
        right_widget.setFixedWidth(150)
        layout = QtGui.QVBoxLayout(right_widget)
        layout.addWidget(self.tooth_data_editor)

        layout = QtGui.QGridLayout(self)
        layout.setMargin(3)
        layout.setSpacing(4)
        layout.addWidget(self.static,0,0)
        layout.addWidget(self.treatment,1,0)
        layout.addWidget(self.completed,2,0)
        layout.addWidget(right_widget,0,1,3,1)
        self.connect_signals()

    def sizeHint(self):
        return QtCore.QSize(400,400)

    def minimumSizeHint(self):
        return QtCore.QSize(300,300)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def _call_fee_widget(self):
        '''
        the "procedure codes" button has been pressed, emit a signal
        '''
        self.emit(QtCore.SIGNAL("Show Fee Widget"))

    def connect_signals(self, connect=True):
        for chart in (self.static, self.treatment, self.completed):
            self.connect(chart, QtCore.SIGNAL("current tooth changed"),
                self.current_tooth_changed)

            self.connect(chart, QtCore.SIGNAL("key_press"),
                self.tooth_data_editor.keyPressEvent)

        self.connect(self.static, QtCore.SIGNAL("teeth present changed"),
            self.known_teeth_changed)

        self.connect(self.tooth_data_editor, QtCore.SIGNAL("Advise"),
            self.Advise)

        self.connect(self.tooth_data_editor, QtCore.SIGNAL("Show Fee Widget"),
            self._call_fee_widget)

        self.connect(self.tooth_data_editor, QtCore.SIGNAL("add treatment"),
            self._add_treatment)


    def _add_treatment(self, prop, plan_or_cmp):
        self.emit(QtCore.SIGNAL("add treatment"), prop, plan_or_cmp)

    def known_teeth_changed(self, key):
        '''
        handles a signal from the static chart (or summary chart)
        that the teeth present has changed
        '''
        self.treatment.set_known_teeth(key)
        self.completed.set_known_teeth(key)
        if self.sender() != self.static: #summary chart sent signal
            self.static.set_known_teeth(key)
        else:
            self.emit(QtCore.SIGNAL("teeth present changed"), key)

        self.emit(QtCore.SIGNAL("update patient teeth present"), key)

    def sync_static(self):
        '''
        connected to a signal from the summary page, helps keep summary
        and static on the same page
        '''
        sending_chart = self.sender()
        tooth = sending_chart.current_tooth
        if tooth is not None:
            self.static.set_current_tooth(tooth.tooth_id)
        self.current_tooth_changed(self.static)

    def current_tooth_changed(self, sending_chart=None):
        '''
        ensures the same tooth is selected on all charts, and the editor
        '''
        if not sending_chart:
            sending_chart = self.sender()
        tooth = sending_chart.current_tooth

        #check to see if editing is incomplete
        if not self.tooth_data_editor.setTooth(tooth):
            #editing still ongoing
            previous_tooth = self.tooth_data_editor.current_tooth

            sending_chart.clear_selection()
            sending_chart.set_current_tooth(previous_tooth)
            return

        for chart in (self.static, self.treatment, self.completed):
            if chart != sending_chart:
                chart.clear_selection()
                chart.set_current_tooth(None)
                chart.update()

        if sending_chart in (self.treatment, self.completed):
            self.emit(QtCore.SIGNAL("clear summary chart selection"))

    def clear(self):
        self.patient = None
        for chart in (self.static, self.completed, self.treatment):
            chart.clear()
        self.tooth_data_editor.clear()

    def load_patient(self):
        patient = SETTINGS.current_patient
        self.patient = patient
        for chart in (self.static, self.completed, self.treatment):
            chart.set_known_teeth(patient.dent_key)

        self.static_chart_model.add_data(patient.static_chart_data)
        self.static_chart_model.add_perio_records(patient.perio_data)


    def update_patient(self):
        '''
        push any edits into the db_orm
        '''
        if not self.patient:
            return

        new_fillings = self.static.chart_data_model.get_new_fillings()
        self.patient["static_fills"].add_filling_records(new_fillings)

        new_crowns = self.static.chart_data_model.get_new_crowns()
        self.patient["static_crowns"].add_crown_records(new_crowns)

        new_roots = self.static.chart_data_model.get_new_roots()
        self.patient["static_roots"].add_root_records(new_roots)

        new_comments = self.static.chart_data_model.get_new_comments()
        self.patient["static_comments"].add_comment_records(new_comments)

if __name__ == "__main__":

    def sig_catcher(*args):
        print "signal caught", args

    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    layout = QtGui.QVBoxLayout(dl)

    obj = ChartsPage(dl)
    dl.connect(obj, QtCore.SIGNAL("add treatment"), sig_catcher)
    layout.addWidget(obj)

    dl.exec_()