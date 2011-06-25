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

'''
This module provides 2 classes
AddressDialog and AdvancedAddressOptionsWidget
'''


from PyQt4 import QtCore, QtGui

from lib_openmolar.common.dialogs import ExtendableDialog



from lib_openmolar.client.qt4gui.dialogs.address_dialogs.address_history_dialog \
    import AddressHistoryDialog

from lib_openmolar.client.qt4gui.dialogs.address_dialogs.components import (
    ExistingAddressWidget,
    NewAddressWidget)




class AddressDialog(ExtendableDialog):
    def __init__(self, address_obj, chosen=0, parent=None):
        '''
        :param: address_obj (:doc:`AddressObject` )
        :kword: chosen - the chosen index
        :kword: parent widget QtGui.QWidget or None
        '''
        super(AddressDialog, self).__init__(parent)
        self.setWindowTitle(_("Edit Addresses"))
        
        #a pointer to the records stored in the :doc:`AddressObject`
        self.addresses = address_obj.records

        self.value_store_dict = {}

        self.advanced_widg = AdvancedAddressOptionsWidget(self)
        self.add_advanced_widget(self.advanced_widg)


        self.stacked_widget = QtGui.QStackedWidget()
        self.insertWidget(self.stacked_widget)

        self.existing_address_widget = QtGui.QWidget() #see next conditional

        new_addy_widget = NewAddressWidget(addressDB, self)
        self.stacked_widget.addWidget(new_addy_widget)

        if len(self.addresses) == 0:
            self.button_box.hide()
            page = 0

        else:
            self.existing_address_widget = \
                ExistingAddressWidget(addressDB, chosen, self)
            page = 1
        self.stacked_widget.addWidget(self.existing_address_widget)
        self.stacked_widget.setCurrentIndex(page)

        self.connect(new_addy_widget, QtCore.SIGNAL("new address entered"),
            self.new_address_entered)

        self.connect(self.advanced_widg, QtCore.SIGNAL("show history"),
            self.show_history)

        self.connect(self.advanced_widg, QtCore.SIGNAL("show advanced ui"),
            self.advanced_ui)

        self.connect(self.advanced_widg, QtCore.SIGNAL("new address mode"),
            self.show_new_addy_widget)

        self.enableApply()

    def exec_(self):
        while True:
            if ExtendableDialog.exec_(self):
                try:
                    self.existing_address_widget.apply()
                except AttributeError:
                    pass
                break
            else:
                return False
        return True


    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def advanced_ui(self, i):
        self.existing_address_widget.toggle_advanced_ui(i)
        self.more_but.click()
        self.setFixedWidth(self.existing_address_widget.width())

    def show_new_addy_widget(self, i):
        self.stacked_widget.setCurrentIndex(i)

    def new_address_entered(self):
        self.accept()

    def show_history(self):
        self.more_but.click()

        dl = AddressHistoryDialog(self.addresses, self)
        dl.exec_()

class AdvancedAddressOptionsWidget(QtGui.QWidget):
    '''
    the extension for the dialog
    '''
    def __init__(self, parent = None):
        super(AdvancedAddressOptionsWidget, self).__init__(parent)

        self.advanced_cb = QtGui.QCheckBox(_("Allow Advanced Editing"))
        self.advanced_cb.toggled.connect(self.advanced_cb_toggled)

        history_but = QtGui.QPushButton(_("show patient's address history"))
        history_but.clicked.connect(self.history_but_clicked)

        self.new_but = QtGui.QPushButton(_("add another address"))
        self.new_but.setCheckable(True)
        self.new_but.clicked.connect(self.new_but_clicked)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(history_but)
        layout.addWidget(self.new_but)
        layout.addWidget(self.advanced_cb)

    def history_but_clicked(self):
        self.emit(QtCore.SIGNAL("show history"))

    def advanced_cb_toggled(self, i):
        self.emit(QtCore.SIGNAL("show advanced ui"), i)

    def new_but_clicked(self, i):
        if i:
            self.new_but.setText(_("add another address"))
            page=0
        else:
            self.new_but.setText(_("edit selected address"))
            page=1
        self.emit(QtCore.SIGNAL("new address mode"), page)


if __name__ == "__main__":



    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    from lib_openmolar.client.db_orm.client_address import AddressDB
    address_db = AddressDB(cc, 70)

    last_used = AddressDB(cc, 2).records[0]

    SETTINGS.set_last_used_address(last_used)

    dl = AddressDialog(address_db)
    dl.exec_()

    if address_db.is_dirty:
        QtGui.QMessageBox.information(dl, "info", "changes made")
