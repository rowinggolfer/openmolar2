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
        _("New Appointment for Patient"), name))

        self.patient_label.setAlignment(QtCore.Qt.AlignCenter)

        frame =  QtGui.QFrame()
        layout = QtGui.QFormLayout(frame)

        self.clinician_combobox = QtGui.QComboBox()
        self.clinician_combobox.setModel(SETTINGS.practitioners.model)
        self.length_combobox = QtGui.QComboBox()
        self.length_combobox.addItems(self.LENGTH_LIST)
        self.trt1_combobox = QtGui.QComboBox()
        self.trt1_combobox.setEditable(True)
        self.trt1_combobox.addItems(
            SETTINGS.TEXT_FIELDS.get('trt1',"").split(","))
        self.trt2_combobox = QtGui.QComboBox()
        self.trt2_combobox.addItems([""] +
            SETTINGS.TEXT_FIELDS.get('trt2',"").split(","))
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

    @property
    def LENGTH_LIST(self):
        str = '15 mins,20 mins,30 mins,40 mins,45 mins,1 hour,75 mins,90 mins,other'
        str = str.replace("mins", _("mins")).replace("hour", _("hour"))
        str = str.replace("other", _("other"))

        return str.split(",")

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def apply(self):
        LOGGER.debug("NewApptDialog.apply")

    def _schedule_now(self):
        self.schedule_now = True

    def enableApply(self, enable=True):
        '''
        call this to enable the apply button (which is disabled by default)
        '''
        BaseDialog.enableApply(self, enable)
        self.schedule_now_button.setEnabled(enable)

    @property
    def chosen_practitioner(self):
        index = self.clinician_combobox.model().index(
            self.clinician_combobox.currentIndex())

        practitioner =  self.clinician_combobox.model().data(
            index, QtCore.Qt.UserRole)

        return practitioner.id

    @property
    def trt1(self):
        return self.trt1_combobox.currentText()

    @property
    def trt2(self):
        return self.trt2_combobox.currentText()

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
        return self.memo_lineedit.text()

if __name__ == "__main__":
    app = QtGui.QApplication([])
    from lib_openmolar.client.connect import DemoClientConnection

    cc = DemoClientConnection()
    cc.connect()

    dl = NewApptDialog()
    if dl.exec_():
        dl.apply()
    LOGGER.debug("schedule now = %s"% dl.schedule_now)
    print dl.chosen_practitioner
    print dl.trt1
    print dl.trt2
    print dl.length
    print dl.memo