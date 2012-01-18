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

class NullDateEdit(QtGui.QWidget):
    '''
    a simple button / date edit widget, which handles a NULL type in the db
    '''
    def __init__(self, q_variant, parent=None):
        super(NullDateEdit, self).__init__(parent)

        self.q_variant = q_variant

        self.but = QtGui.QPushButton(_('n/a'), self)
        self.date_edit = QtGui.QDateEdit(self)

        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setEnabled(False)

        self.but.clicked.connect(self.enable_date)

        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.but)
        layout.addWidget(self.date_edit)

    def enable_date(self):
        self.date_edit.setEnabled(not self.date_edit.isEnabled())
        but_text = (_('n/a'),_('set as'))[self.date_edit.isEnabled()]
        self.but.setText(but_text)

    def date(self):
        if self.date_edit.isEnabled():
            return self.date_edit.date()
        else:
            return self.q_variant


if __name__ == "__main__":
    import gettext
    gettext.install("")

    date1 = QtCore.QVariant()
    date2 = QtCore.QVariant(QtCore.QDate(1969,12,9))

    app = QtGui.QApplication([])
    object1 = NullDateEdit(date1)
    object2 = NullDateEdit(date2)

    dl = QtGui.QDialog()
    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(object1)
    layout.addWidget(object2)
    dl.exec_()
