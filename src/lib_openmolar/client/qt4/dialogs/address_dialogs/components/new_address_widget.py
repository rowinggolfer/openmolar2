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

from lib_openmolar.client.qt4.dialogs.address_dialogs.find_address_dialog \
    import FindAddressDialog
from lib_openmolar.client.qt4.dialogs.address_dialogs.new_address_dialog \
    import NewAddressDialog
from lib_openmolar.client.qt4.dialogs.address_dialogs.known_address_new_link \
    import KnownAddressNewLinkDialog



class NewAddressWidget(QtGui.QWidget):
    '''
    provides options to provide new address data either by entering a new
    address, or verifying a link
    '''
    def __init__(self, addressDB, parent=None):
        super(NewAddressWidget, self).__init__(parent)
        self.addressDB = addressDB

        new_frame = QtGui.QFrame(self)

        new_but = QtGui.QPushButton(_("Add a new address to the database"))
        link_but = QtGui.QPushButton(_("link to an address already stored"))

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(new_but)
        layout.addWidget(link_but)
        spacer = QtGui.QSpacerItem(0, 0,
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        layout.addItem(spacer)

        self.last_used_address = SETTINGS.last_used_address
        if self.last_used_address:
            last_link_but = QtGui.QPushButton(_("link to this address"))
            label = QtGui.QLabel(self.last_used_address.details_html())
            label.setAlignment(QtCore.Qt.AlignCenter)

            layout.addWidget(label)
            layout.addWidget(last_link_but)
            spacer = QtGui.QSpacerItem(0, 0,
                QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
            layout.addItem(spacer)

            last_link_but.clicked.connect(self.add_last_address)

        link_but.clicked.connect(self.find_known_address)
        new_but.clicked.connect(self.add_new_address)

    def find_known_address(self):
        dl = FindAddressDialog(self)
        address_record, result = dl.exec_()
        if result:
            self.set_linked_address(address_record)

    def set_linked_address(self, address_record):
        dl = KnownAddressNewLinkDialog(address_record, self)
        if dl.exec_():
            address_id, cat = dl.result
            self.addressDB.add_address_link(address_id, cat)
            self.done()

    def add_new_address(self):
        dl = NewAddressDialog(self)
        if dl.exec_():
            address_record = dl.result
            self.set_linked_address(address_record)

    def add_last_address(self):
        self.set_linked_address(self.last_used_address)

    def done(self):
        self.emit(QtCore.SIGNAL("new address entered"))

if __name__ == "__main__":



    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    from lib_openmolar.client.db_orm.client_address import AddressDB
    address_db = AddressDB(1)

    obj = NewAddressWidget(address_db)
    obj.show()

    app.exec_()
