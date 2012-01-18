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

from lib_openmolar.common.qt4.widgets.upper_case_lineedit import UpperCaseLineEdit
from lib_openmolar.common.qt4.widgets.null_date_edit import NullDateEdit

from lib_openmolar.client.qt4.dialogs.address_dialogs.who_lives_here_dialog \
    import WhoLivesHereDialog

from lib_openmolar.common.datatypes import OMType


class ExistingAddressWidget(QtGui.QWidget):
    '''
    lays out an existing address for editing
    '''
    def __init__(self, address_object, index, parent = None):
        super(ExistingAddressWidget, self).__init__(parent)

        self.address_object = address_object

        self.address = address_object.records[index]
        self.value_store = {}
        self.setupUi()

    def toggle_advanced_ui(self, advanced):
        self.adv_frame.setVisible(advanced)
        self.adjustSize()

    def setupUi(self):
        frame = QtGui.QFrame(self)
        self.adv_frame = QtGui.QFrame(self)
        self.adv_frame.setVisible(False)

        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(frame)
        layout.addWidget(self.adv_frame)

        form = QtGui.QFormLayout(frame)
        form.setMargin(0)
        adv_form = QtGui.QFormLayout(self.adv_frame)

        for editable_field in self.address.editable_fields[0]:
            if editable_field == None: # None value means add a separator
                continue

            field_name = editable_field.fieldname
            display_text = editable_field.readable_fieldname

            field = self.address.field(field_name)

            if editable_field.type == None:
                field_type = field.type()
            else:
                field_type = editable_field.type

            if field_type == QtCore.QVariant.Date:
                if field.name() == 'to_date':
                    widg = NullDateEdit(field.value(), self)
                else:
                    widg = QtGui.QDateEdit()
                    widg.setCalendarPopup(True)
                    widg.setDate(field.value().toDate())

            elif field_type == QtCore.QVariant.String:
                widg = UpperCaseLineEdit()
                widg.setText(field.value().toString())
            elif type(field_type) == OMType:
                widg = QtGui.QComboBox()
                for val in field_type.allowed_values:
                    widg.addItem(field_type.readable_dict[val], val)
                index = widg.findData(field.value())
                widg.setCurrentIndex(index)
            else:
                print "unknown field type", field_name, field_type
                widg = QtGui.QLabel("????")

            if editable_field.advanced:
                label = form.labelForField(widg)
                adv_form.addRow(display_text, widg)
            else:
                form.addRow(display_text, widg)

            self.value_store[field_name] = (widg, field_type)


        shared_with = self.address.value("known_residents").toInt()[0] - 1
        if shared_with > 0:
            if shared_with == 1:
                message =  _("other person shares this address")
            else:
                message =  _("other people share this address")

            label = QtGui.QLabel(u"<b>%s %s</b>"% (shared_with, message))
            label.setAlignment(QtCore.Qt.AlignCenter)

            who_but = QtGui.QPushButton("?")
            who_but.setMaximumWidth(30)

            lay = QtGui.QHBoxLayout()
            lay.addWidget(label)
            lay.addWidget(who_but)
            form.addRow(lay)

            who_but.clicked.connect(self.who_but_clicked)

        icon = QtGui.QIcon(":icons/chain-broken.png")
        de_link_button = QtGui.QPushButton(icon, "unlink address/patient")
        de_link_button.setToolTip(
            _("unlink patient/address"))

        adv_form.addRow(de_link_button)

        de_link_button.clicked.connect(self.de_link)

    def apply(self):
        result, ommisions = self.address.load_values(self.value_store)
        if not result:
            QtGui.QMessageBox.warning(self, "todo - oops", str(ommisions))
        else:
            return result

    def de_link(self):
        if QtGui.QMessageBox.question(self, _("Confirm"),
        _("no longer use this address for this patient?"),
        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Ok) == QtGui.QMessageBox.Ok:
            self.address_object.break_address_link(self.address)
            self.emit(QtCore.SIGNAL("link broken"))

    def who_but_clicked(self):
        address_id = self.address.value("ix").toInt()[0]

        dl = WhoLivesHereDialog(address_id, self.address_object, self)
        dl.exec_()


if __name__ == "__main__":

    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    from lib_openmolar.client.db_orm.client_address import AddressObjects
    address_object = AddressObjects(1)

    obj = ExistingAddressWidget(address_object, 0)
    test_button = QtGui.QPushButton("test_advanced_features")
    test_button.setCheckable(True)
    test_button.clicked.connect(obj.toggle_advanced_ui)


    dl = QtGui.QDialog()
    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(obj)
    layout.addWidget(test_button)


    dl.exec_()
