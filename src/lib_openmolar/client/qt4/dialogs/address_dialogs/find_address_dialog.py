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

from lib_openmolar.common.qt4.widgets.upper_case_lineedit import UpperCaseLineEdit
from lib_openmolar.common.qt4.dialogs import BaseDialog


from lib_openmolar.client.qt4.dialogs.address_dialogs.select_address \
    import AddressSelectionDialog


class FindAddressDialog(BaseDialog):
    def __init__(self,  parent=None):
        super(FindAddressDialog, self).__init__(parent)

        self.setWindowTitle(_("Address Finder"))

        top_widg = QtGui.QWidget(self)
        form = QtGui.QFormLayout(top_widg)
        self.index_spin_box = QtGui.QSpinBox(top_widg)
        form.addRow(_("Address index"), self.index_spin_box)

        label = QtGui.QLabel(_('or search with the following values'))
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.set_accept_button_text(_("Search Now"))

        self.search_form = QtGui.QWidget()
        self.address_le = UpperCaseLineEdit()
        self.city_le = UpperCaseLineEdit()
        self.country_le = UpperCaseLineEdit()
        self.pcde_le = UpperCaseLineEdit()

        form = QtGui.QFormLayout(self.search_form)
        form.addRow(_("Address includes"), self.address_le)
        form.addRow(_("Town/City"), self.city_le)
        form.addRow(_("Country"), self.country_le)
        form.addRow(_("Post Code"), self.pcde_le)

        self.insertWidget(top_widg)
        self.insertWidget(label)
        self.insertWidget(self.search_form)
        self.result_record = None
        self.search_values = {}
        self._connect_signals()

    def _connect_signals(self):
        self.index_spin_box.valueChanged.connect(self._check)
        self.address_le.cursorPositionChanged.connect(self._check)
        self.city_le.cursorPositionChanged.connect(self._check)
        self.country_le.cursorPositionChanged.connect(self._check)
        self.pcde_le.cursorPositionChanged.connect(self._check)

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    @property
    def index_value(self):
        return self.index_spin_box.value()

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def _check(self, *args):
        enable = (self.index_spin_box.value() !=0 or
            self.address_le.text() != "" or self.city_le.text() != ""
            or self.country_le.text() != "" or self.pcde_le.text() != "")

        self.enableApply(enable)
        self.search_form.setEnabled(self.index_value == 0)

    def exec_(self):
        self.clear()
        if BaseDialog.exec_(self):
            self.apply()
        if self.result_record:
            return (self.result_record, True)
        else:
            return (None, False)

    def clear(self):
        for le in (self.address_le, self.pcde_le):
            le.setText("")
        self.result_record = None
        self.address_le.setFocus()
        self._check()

    def apply(self):
        if self.index_value != 0:
            self.search_values["address_id"] = self.index_value
        self.search_values["addr1"] = self.address_le.text()
        self.search_values["postal_cd"] = self.pcde_le.text()
        self.search_values["city"] = self.city_le.text()
        self.search_values["country"] = self.country_le.text()

        model = SETTINGS.psql_conn.get_address_matchmodel(self.search_values)

        match_no = model.rowCount()
        if not match_no:
            self.Advise(_("no match found"), 1)
        else:
            if match_no > 1:
                dl = AddressSelectionDialog(model, self.parent())
                self.result_record = dl.chosen_record
            else:
                self.result_record = model.record(0)



if __name__ == "__main__":



    def sig_catcher(*args):
        print args

    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    dl = FindAddressDialog()
    dl.connect(dl, QtCore.SIGNAL("Serial Number"), sig_catcher)
    print dl.exec_()
