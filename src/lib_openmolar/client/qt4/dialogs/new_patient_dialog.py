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

from PyQt4 import QtCore, QtGui, QtSql

from lib_openmolar.common.datatypes import OMTypes

from lib_openmolar.common.qt4.dialogs import ExtendableDialog
from lib_openmolar.common.qt4.widgets.upper_case_lineedit import UpperCaseLineEdit



from lib_openmolar.client.qt4.colours import colours

from lib_openmolar.client.db_orm.client_patient import NewPatientDB

import find_patient_dialog

class NewPatientDialog(ExtendableDialog):
    def __init__(self, parent=None):
        '''
        2 arguments
            1. the database into which the new patient will go.
            2. parent widget(optional)
        '''
        ExtendableDialog.__init__(self, parent)
        self.setWindowTitle(_("New Patient"))
        self.set_advanced_but_text(_("optional fields"))
        label = QtGui.QLabel(
            _('The Following Fields are required to create a New Record'))
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignCenter)

        widget = QtGui.QWidget()
        self.form = QtGui.QFormLayout(widget)

        advanced_widget = QtGui.QWidget()
        self.advanced_form = QtGui.QFormLayout(advanced_widget)

        self.insertWidget(label)
        self.insertWidget(widget)
        self.add_advanced_widget(advanced_widget)

        self.set_check_on_cancel(True)
        self.enableApply()
        self.set_accept_button_text(_("Create New Record"))

        self.patient = NewPatientDB()
        self.patient.setValue("modified_by", SETTINGS.user)
        self.patient.setValue("status", "active")
        self.patient.remove(self.patient.indexOf("time_stamp"))

        self.value_store = {}

        palette = QtGui.QPalette(self.palette())
        brush = QtGui.QBrush(colours.REQUIRED_FIELD)
        palette.setBrush(QtGui.QPalette.Base, brush)

        for editable_field in self.patient.editable_fields:
            field_name = editable_field.fieldname
            display_text = editable_field.readable_fieldname
            field = self.patient.field(field_name)

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

            if editable_field.required:
                widg.setPalette(palette)

            if editable_field.advanced:
                self.advanced_form.addRow(display_text, widg)
            else:
                self.form.addRow(display_text, widg)
            self.value_store[field_name] = (widg, field_type)

        self.form.itemAt(1).widget().setFocus()

    def sizeHint(self):
        return QtCore.QSize(300,300)

    def exec_(self):
        '''
        overwrite the dialog's exec call
        '''
        while True:
            self.show()
            if ExtendableDialog.exec_(self):
                if not self.apply():
                    list_of_ommisions = ""
                    for ommision in self.ommisions:
                        list_of_ommisions += u"<li>%s</li>"% ommision

                    QtGui.QMessageBox.warning(self, _("error"),
                    u"%s<ul>%s</ul>" %(
                    _("incomplete form - the following are required"),
                    list_of_ommisions))
                    continue

                id, result = self.check_is_duplicate()
                if result:
                    self.emit(QtCore.SIGNAL("Load Serial Number"), id)
                    return False
                query, values = self.patient.insert_query
                q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
                q_query.prepare(query + " returning ix")
                for value in values:
                    q_query.addBindValue(value)
                result =  q_query.exec_()
                if result:
                    if q_query.isActive():

                        q_query.next()
                        id = q_query.record().value("ix").toInt()[0]

                        self.emit(QtCore.SIGNAL("Load Serial Number"), id)
                    return True
                else:
                    self.Advise("Query Error" + q_query.lastError().text())
            else:
                return False

    def apply(self):
        '''
        applies the entered data to the new object
        '''

        # step 1.. get the values the user has entered.
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

        # step 2.. see if all fields are completed

        self.ommisions = []
        all_completed = True
        for editable_field in self.patient.editable_fields:
            field_name = editable_field.fieldname
            if (editable_field.required and
            self.patient.value(field_name).toString()) == "":
                all_completed = False
                self.ommisions.append(editable_field.readable_fieldname)

        return all_completed

    def check_is_duplicate(self):
        '''
        is the new patient already on the books?
        search for patients with the same dob.
        '''
        chk_dict = {}
        chk_dict["dob"] = self.patient.value("dob").toDate()
        #chk_dict["sname"] = self.patient.value("last_name").toString()
        #chk_dict["fname"] = self.patient.value("first_name").toString()
        #chk_dict["soundex_sname"] = True
        #chk_dict["soundex_fname"] = True
        matches = SETTINGS.psql_conn.get_matchlist(chk_dict)
        if matches != []:
            dl = ShowMatchDialog(matches, self.parent())
            id = dl.chosen_id
            return (id, bool(id))

        return (None, False)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

class ShowMatchDialog(find_patient_dialog.FinalSelectionDialog):
    def __init__(self, matches, parent=None):
        super(ShowMatchDialog, self).__init__(matches, parent)
        self.setWindowTitle(
        _("Possible Duplicate - matching date of birth check"))
        self.top_label.setText(
        _("Is the new patient one of the following known patients?"))

        self.set_accept_button_text(_("Yes, load the selected Record"))
        self.set_reject_button_text(_("No, Create a new Record now."))


if __name__ == "__main__":



    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import ClientConnection

    cc = ClientConnection()
    cc.connect()

    dl = NewPatientDialog()
    dl.exec_()
