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

from lib_openmolar.common.datatypes import OMType

from lib_openmolar.common.qt4.dialogs import BaseDialog
from lib_openmolar.common.qt4.widgets import UpperCaseLineEdit


class EditPatientDialog(BaseDialog):
    def __init__(self, patient, parent=None):
        '''
        2 arguments
            1. a patientDB instance
            2. parent widget(optional)
        '''
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Edit Patient"))

        self.patient = patient

        label = QtGui.QLabel(_('Edit the following fields'))
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignCenter)

        widget = QtGui.QWidget()

        self.value_store = {}

        form = QtGui.QFormLayout(widget)
        for editable_field in self.patient.editable_fields:
            field_name = editable_field.fieldname
            display_text = editable_field.readable_fieldname
            field = patient.field(field_name)

            if editable_field.type == None:
                field_type = field.type()
            else:
                field_type = editable_field.type

            if field_type == QtCore.QVariant.Date:
                widg = QtGui.QDateEdit(self)
                widg.setDate(field.value().toDate())
            elif field_type == QtCore.QVariant.String:
                widg = UpperCaseLineEdit(self)
                widg.setText(field.value().toString())
            elif type(field_type) == OMType:
                widg = QtGui.QComboBox(self)
                for val in field_type.allowed_values:
                    widg.addItem(field_type.readable_dict[val], val)
                index = widg.findData(field.value())
                widg.setCurrentIndex(index)
            else:
                widg = QtGui.QLabel("????")

            form.addRow(display_text, widg)
            self.value_store[field_name] = (widg, field_type)

        self.insertWidget(label)
        self.insertWidget(widget)
        form.itemAt(1).widget().setFocus()

        self.set_accept_button_text(_("Apply Changes"))
        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def apply(self):
        for field_name in self.value_store:
            widg, field_type = self.value_store[field_name]
            if field_type == QtCore.QVariant.Date:
                self.patient.setValue(field_name, widg.date())
            elif field_type == QtCore.QVariant.String:
                self.patient.setValue(field_name, widg.text())
            elif type(field_type) == OMType:
                val = widg.itemData(widg.currentIndex())
                self.patient.setValue(field_name, val)
            else:
                print "Whoops!" ## <-shouldn't happen

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

if __name__ == "__main__":

    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    from lib_openmolar.client.db_orm.client_patient import PatientDB
    patient = PatientDB(1)

    dl = EditPatientDialog(patient)
    if dl.exec_():
        dl.apply()
