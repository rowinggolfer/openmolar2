#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
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
from PyQt4 import QtGui, QtCore

from lib_openmolar.common.qt4.dialogs import BaseDialog

class GetLengthDialog(BaseDialog):
    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        frame = QtGui.QFrame()
        layout = QtGui.QFormLayout(frame)

        self.hours_spinbox = QtGui.QSpinBox()
        self.hours_spinbox.setRange(0,24)

        self.minutes_spinbox = QtGui.QSpinBox()
        self.minutes_spinbox.setRange(0,55)
        self.minutes_spinbox.setSingleStep(5)

        layout.addRow(_("Hours"), self.hours_spinbox)
        layout.addRow(_("Minutes"), self.minutes_spinbox)
        message = _("Please specify the appointment length")

        self.setWindowTitle(message)
        self.insertWidget(QtGui.QLabel(message))
        self.insertWidget(frame)
        self.enableApply()

    def sizehint(self):
        return QtCore.QSize(200, 200)

    @property
    def length_text(self):
        hours = self.hours_spinbox.value()
        mins = self.minutes_spinbox.value()
        retval = ""
        if hours != 0:
            retval = u"%s %s "% (hours, _("hours"))
        if retval == "" or mins != 0:
            retval += u"%s %s"% (mins, _("minutes"))

        return retval

class NewApptDialog(BaseDialog):
    schedule_now = False
    def __init__(self, parent=None):
        self.schedule_now_button = QtGui.QPushButton(_("Schedule Now"))

        BaseDialog.__init__(self, parent)
        patient = SETTINGS.current_patient
        try:
            name = patient.full_name
            self.enableApply()
        except AttributeError:
            LOGGER.warning("NewApptDialog - called with no patient loaded")
            name = _("NO PATIENT LOADED")

        self.patient_label = QtGui.QLabel("%s<br /><b>%s</b>"% (
        _("Appointment for Patient"), name))

        self.patient_label.setAlignment(QtCore.Qt.AlignCenter)

        frame =  QtGui.QFrame()
        layout = QtGui.QFormLayout(frame)

        self.clinician_combobox = QtGui.QComboBox()
        self.clinician_combobox.setModel(SETTINGS.practitioners.model)
        self.length_combobox = QtGui.QComboBox()
        self.populate_length_combobox()
        self.trt1_combobox = QtGui.QComboBox()
        self.trt1_combobox.setEditable(True)
        self.populate_trt1_combobox()
        self.trt2_combobox = QtGui.QComboBox()
        self.populate_trt2_combobox()
        self.trt2_combobox.setCurrentIndex(-1)
        self.memo_lineedit = QtGui.QLineEdit()

        layout.addRow(_("Appointment with"), self.clinician_combobox)
        layout.addRow(_("Length"), self.length_combobox)
        layout.addRow(_("Reason 1"), self.trt1_combobox)
        layout.addRow(_("Reason 2 (optional)"), self.trt2_combobox)
        layout.addRow(_("Memo (optional)"), self.memo_lineedit)

        self.insertWidget(self.patient_label)
        self.insertWidget(frame)

        self.button_box.addButton(self.schedule_now_button,
            self.button_box.HelpRole)
        self.schedule_now_button.clicked.connect(self._schedule_now)

        self.length_combobox.currentIndexChanged.connect(self.check_length)

    @property
    def LENGTH_LIST(self):
        str = '15 mins,10 mins,20 mins,30 mins,40 mins,45 mins,' +\
              '1 hour,75 mins,90 mins,2 hours'
        str = str.replace("mins", _("mins")).replace("hour", _("hour"))
        str = u'%s,%s'% (str, _("other"))

        return str.split(",")

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def populate_trt1_combobox(self, extra_item=None):
        self.trt1_combobox.clear()
        fields = SETTINGS.TEXT_FIELDS.get('trt1',"").split(",")
        if extra_item:
            fields = [extra_item] + fields
        self.trt1_combobox.addItems(fields)

    def populate_trt2_combobox(self, extra_item=None):
        self.trt2_combobox.clear()
        fields = SETTINGS.TEXT_FIELDS.get('trt2',"").split(",")
        if extra_item:
            fields = [extra_item] + fields
        self.trt2_combobox.addItems(fields)

    def populate_length_combobox(self, extra_item=None):
        self.length_combobox.clear()
        fields = self.LENGTH_LIST
        if extra_item:
            fields = [extra_item] + fields
        self.length_combobox.addItems(fields)

    def set_appt_params(self, appointment):
        '''
        load the dialog with known values from the appointment
        (used when modifying an appointment, as opposed to a blank canvas)
        '''
        self.populate_trt1_combobox(appointment.trt1)
        if appointment.trt2:
            self.populate_trt2_combobox(appointment.trt2)
        self.memo_lineedit.setText(appointment.memo)
        self.populate_length_combobox(appointment.length_text)

    def apply(self):
        LOGGER.debug("NewApptDialog.apply")

    def _schedule_now(self):
        self.schedule_now = True
        self.accept()

    def enableApply(self, enable=True):
        '''
        call this to enable the apply button (which is disabled by default)
        '''
        BaseDialog.enableApply(self, enable)
        self.schedule_now_button.setEnabled(enable)

    def check_length(self, i):
        '''
        length combobox has been adjusted, if "other" length is chosen,
        append user values to the list
        '''
        if self.length_combobox.currentText() == _("other"):
            dl = GetLengthDialog(self)
            if dl.exec_():
                self.populate_length_combobox(dl.length_text)

            self.length_combobox.setCurrentIndex(0)

    @property
    def selected_clinician(self):
        '''
        the practitioner chosen by the user.
        '''
        index = self.clinician_combobox.model().index(
            self.clinician_combobox.currentIndex())

        practitioner =  self.clinician_combobox.model().data(
            index, QtCore.Qt.UserRole)

        return practitioner

    @property
    def selected_clinician_id(self):
        return self.selected_clinician.id

    @property
    def trt1(self):
        return unicode(self.trt1_combobox.currentText())

    @property
    def trt2(self):
        return unicode(self.trt2_combobox.currentText())

    @property
    def length(self):
        string = unicode(self.length_combobox.currentText())
        digits = re.findall("\d+", string)

        if len(digits) == 2:
            return int(digits[0])*60 + int(digits[1])
        elif len(digits) == 1:
            if re.search(_("hour"), string):
                return int(digits[0])*60
            return int(digits[0])

        return 0

    @property
    def memo(self):
        return unicode(self.memo_lineedit.text())

if __name__ == "__main__":
    app = QtGui.QApplication([])
    from lib_openmolar.client.connect import DemoClientConnection

    cc = DemoClientConnection()
    cc.connect()

    dl = NewApptDialog()
    if dl.exec_():
        dl.apply()
    LOGGER.debug("schedule now = %s"% dl.schedule_now)
    print dl.selected_clinician_id
    print dl.trt1
    print dl.trt2
    print dl.length
    print dl.memo