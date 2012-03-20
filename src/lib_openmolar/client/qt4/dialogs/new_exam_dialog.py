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

from lib_openmolar.common.qt4.dialogs import BaseDialog
from lib_openmolar.common.db_orm import TreatmentItem

class NewExamDialog(BaseDialog):
    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)

        self.setWindowTitle(_("Perform an Examination"))

        gb1 = QtGui.QGroupBox(_("Type"))
        layout = QtGui.QVBoxLayout(gb1)

        self.radio_buttons = []
        for exam_code in SETTINGS.PROCEDURE_CODES.exam_codes:
            rb = QtGui.QRadioButton(exam_code.description)
            rb.proc_code = exam_code
            self.radio_buttons.append(rb)
            layout.addWidget(rb)

        try:
            self.radio_buttons[0].setChecked(True)
        except IndexError: #shouldn't happen!
            pass

        self.date_edit = QtGui.QDateEdit()
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.date_edit.setCalendarPopup(True)

        self.dent_cb = QtGui.QComboBox()

        practitioners = SETTINGS.practitioners

        try:
            index = practitioners.index(
                SETTINGS.current_practitioner)
        except ValueError:
            index = -1

        self.dent_cb.setModel(practitioners.dentists_model)
        self.dent_cb.setCurrentIndex(index)

        gb2 = QtGui.QGroupBox(_("Date"))
        layout = QtGui.QVBoxLayout(gb2)
        layout.addWidget(self.date_edit)

        gb3 = QtGui.QGroupBox(_("Dentist"))
        layout = QtGui.QVBoxLayout(gb3)
        layout.addWidget(self.dent_cb)

        self.insertWidget(gb1)
        self.insertWidget(gb2)
        self.insertWidget(gb3)

        self.enableApply(True)

    def exec_(self):
        if BaseDialog.exec_(self):
            if self.dent_cb.currentIndex() == -1:
                QtGui.QMessageBox.warning(self, _("error"),
                    _("no dentist selected"))
                return self.exec_()
            else:
                QtGui.QApplication.instance().emit(
                    QtCore.SIGNAL("treatment item generated"),
                    self.treatment_item)
                return True
        return False

    @property
    def chosen_practitioner(self):
        index = self.dent_cb.model().index(self.dent_cb.currentIndex())
        practitioner = self.dent_cb.model().data(index, QtCore.Qt.UserRole)
        return practitioner

    @property
    def proc_code(self):
        for rb in self.radio_buttons:
            if rb.isChecked():
                return rb.proc_code

    @property
    def treatment_item(self):
        ti = TreatmentItem(self.proc_code)
        practitioner = self.chosen_practitioner
        ti.set_px_clinician(practitioner.id)
        ti.set_tx_clinician(practitioner.id)
        ti.set_cmp_date(self.date)
        return ti

    @property
    def date(self):
        return self.date_edit.date()

if __name__ == "__main__":

    app = QtGui.QApplication([])
    from lib_openmolar.client.connect import DemoClientConnection

    cc = DemoClientConnection()
    cc.connect()

    dl = NewExamDialog()
    if dl.exec_():
        print dl.chosen_practitioner.full_name
        print dl.proc_code
        print dl.date

        print dl.treatment_item