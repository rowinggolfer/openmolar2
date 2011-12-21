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

from lib_openmolar.common.dialogs import BaseDialog

class Dialog(BaseDialog):
    def __init__(self, addresses, parent=None):
        '''
        2 arguments
            1. a list of addressDB instances
            2. parent widget(optional)
        '''
        super(Dialog, self).__init__(parent)
        self.setWindowTitle(_("Address Logic"))

        self.setMinimumWidth(500)
        self.enableApply(True)
        self.addresses = addresses

        header_label = QtGui.QLabel("<b>here are your changes</b>")
        label = QtGui.QLabel(addresses.changes_html())

        header_label.setAlignment(QtCore.Qt.AlignCenter)
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.insertWidget(header_label)
        self.insertWidget(label)


if __name__ == "__main__":



    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    from lib_openmolar.client.db_orm.client_address import AddressDB
    addresses = AddressDB(1)

    addresses.records[0].setValue('addr1', "The Gables")


    dl = Dialog(addresses)
    if dl.exec_():
        QtGui.QMessageBox.information(dl, "info", "dialog accepted")