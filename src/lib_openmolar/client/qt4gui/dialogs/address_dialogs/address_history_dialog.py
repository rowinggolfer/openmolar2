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
from lib_openmolar.common.dialogs import BaseDialog
from lib_openmolar.common import SETTINGS

class AddressHistoryDialog(BaseDialog):
    '''
    we have a known address (ie. a row in the addresses table)
    this dialog is the final step in linking this to the patient
    '''
    def __init__(self, addresses, parent=None):
        super(AddressHistoryDialog, self).__init__(parent)
        self.addresses = addresses

        self.setWindowTitle("Address History")

        self.remove_spacer()

        label = QtGui.QLabel(
            _("The following addresses are linked to this patient"))
        frame = QtGui.QFrame(self)
        self.address_layout = QtGui.QVBoxLayout(frame)

        scroll_area = QtGui.QScrollArea(self)
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)

        self.insertWidget(label)
        self.insertWidget(scroll_area)

        self.load_addresses()

    def load_addresses(self):
        for address in self.addresses:
            widg = AddressHistoryWidget(address)
            self.address_layout.addWidget(widg)

        self.address_layout.addItem(self.spacer)


class AddressHistoryWidget(QtGui.QWidget):
    def __init__(self, address, parent=None):
        QtGui.QWidget.__init__(self, parent)
        label = QtGui.QLabel()
        label.setText(address.details_html())

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(label)

if __name__ == "__main__":

    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    from lib_openmolar.client.db_orm.client_address import AddressObjects
    address_object = AddressObjects(1)

    dl = AddressHistoryDialog(address_object.records)
    dl.exec_()
