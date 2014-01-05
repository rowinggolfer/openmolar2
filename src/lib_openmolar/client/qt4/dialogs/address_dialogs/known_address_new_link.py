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

from PyQt4 import QtGui, QtCore, QtSql
from lib_openmolar.common.qt4.dialogs import BaseDialog

class KnownAddressNewLinkDialog(BaseDialog):
    '''
    we have a known address (ie. a row in the addresses table)
    this dialog is the final step in linking this to the patient
    '''
    def __init__(self, address_record, parent=None):
        super(KnownAddressNewLinkDialog, self).__init__(parent)
        self.address_record = address_record

        self.setWindowTitle("Set Address Link")
        label = QtGui.QLabel(self.address_text, self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        widg = QtGui.QWidget(self)
        self.cat_combo_box = QtGui.QComboBox(widg)
        self.cat_combo_box.addItems(SETTINGS.OM_TYPES["address"].allowed_values)

        form = QtGui.QFormLayout(widg)
        form.addRow(_("Category"), self.cat_combo_box)

        self.insertWidget(label)
        self.insertWidget(widg)

        self.enableApply()

        self.result = (0,"")

    @property
    def address_text(self):
        html = u""
        for i in range(1, self.address_record.count()):
            field_value = self.address_record.value(i).toString()
            if field_value:
                html += u"%s<br />"% field_value
        return html

    def exec_(self):
        if BaseDialog.exec_(self):
            cat = self.cat_combo_box.currentText()
            address_id = self.address_record.value("ix").toInt()[0]
            self.result = (address_id, cat)
            return True

if __name__ == "__main__":



    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    query = '''SELECT ix, addr1, addr2, addr3, city, county, country,
    postal_cd from addresses WHERE ix=1'''

    q_query = QtSql.QSqlQuery(query, cc)
    q_query.first()
    record = q_query.record()

    dl = KnownAddressNewLinkDialog(record)
    if dl.exec_():
        print dl.result
