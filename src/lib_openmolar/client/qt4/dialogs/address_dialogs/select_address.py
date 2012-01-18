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

from PyQt4 import QtGui, QtCore

from lib_openmolar.common.qt4.dialogs import BaseDialog

class AddressSelectionDialog(BaseDialog):
    def __init__(self, address_model, parent=None):
        super(AddressSelectionDialog, self).__init__(parent)

        self.model = address_model

        self.setWindowTitle(_("Final Selection"))
        self.top_label = QtGui.QLabel(
        _("Multiple Matches Found, please choose from the following"))
        self.top_label.setAlignment(QtCore.Qt.AlignCenter)

        self.table_view = QtGui.QTableView(self)
        self.table_view.setModel(self.model)

        self.table_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table_view.setWordWrap(True)
        self.table_view.resizeColumnsToContents()
        self.table_view.horizontalHeader().setStretchLastSection(True)

        self.layout.insertWidget(0, self.top_label)
        self.layout.insertWidget(1, self.table_view)

        self.table_view.selectionModel().currentChanged.connect(self._enable)
        self.table_view.doubleClicked.connect(self._accept)
        self.table_view.selectRow(0)
        self.table_view.setFocus()

        self.set_accept_button_text(_("Link to Selected Address"))

        self.remove_spacer()

    def sizeHint(self):
        return QtCore.QSize(800,300)

    def _enable(self, *args):
        self.enableApply()

    def _accept(self, *args):
        self.accept()

    @property
    def chosen_record(self):
        if self.exec_():
            selected_row = self.table_view.currentIndex().row()
            record = self.model.record(selected_row)
            return record


if __name__ == "__main__":
    from PyQt4 import QtSql
    
    

    app = QtGui.QApplication([])

    model = QtSql.QSqlQueryModel()
    dl = AddressSelectionDialog(model)
    dl.exec_()
