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

from PyQt4 import QtGui, QtCore, QtSql
from lib_openmolar.common.qt4.dialogs import BaseDialog
from lib_openmolar.common import SETTINGS

class WhoLivesHereDialog(BaseDialog):
    '''
    we have a known address (ie. a row in the addresses table)
    this dialog is the final step in linking this to the patient
    '''
    def __init__(self, address_id, addressDB, parent=None):
        BaseDialog.__init__(self, parent)
        self.address_id = address_id
        self.addressDB = addressDB

        self.setWindowTitle("Family Members")

        present_patients_label = QtGui.QLabel()
        present_patients_label.setAlignment(QtCore.Qt.AlignCenter)

        past_patients_label = QtGui.QLabel()
        past_patients_label.setAlignment(QtCore.Qt.AlignCenter)

        present_label = QtGui.QLabel(
            _("The following patients are currently linked to this address"))

        past_label = QtGui.QLabel(
        _("The following patients are historically linked to this address"))

        sa1 = QtGui.QScrollArea()
        sa1.setWidget(present_patients_label)
        sa1.setWidgetResizable(True)

        sa2 = QtGui.QScrollArea()
        sa2.setWidget(past_patients_label)
        sa2.setWidgetResizable(True)

        self.insertWidget(present_label)
        self.insertWidget(sa1)

        self.insertWidget(past_label)
        self.insertWidget(sa2)

        present_list, past_list = \
            self.addressDB.who_else_lives_here(self.address_id)

        lab_text = ""
        for patient in present_list:
            lab_text += u"%s<br />"% patient
        present_patients_label.setText(lab_text)

        if lab_text == "":
            present_label.hide()
            sa1.hide()

        lab_text = ""
        for patient in past_list:
            lab_text += u"%s<br />"% patient
        past_patients_label.setText(lab_text)

        if lab_text == "":
            past_label.hide()
            sa2.hide()


if __name__ == "__main__":
    
    

    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    from lib_openmolar.client import db_orm
    address_db = db_orm.AddressObjects(1)

    address = address_db.records[0]
    address_id = address.value("ix").toInt()[0]

    dl = WhoLivesHereDialog(address_id, address_db)
    dl.exec_()
