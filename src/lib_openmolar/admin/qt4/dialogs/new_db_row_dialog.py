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

from lib_openmolar.common.qt4.dialogs import BaseDialog

class DefaultLineEdit(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self._le = QtGui.QLineEdit()
        self._cb = QtGui.QCheckBox("auto")

        layout = QtGui.QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setMargin(0)
        layout.addWidget(self._le)
        layout.addWidget(self._cb)

        self.text = self._le.text
        self.isChecked = self._cb.isChecked

class NewRowDialog(BaseDialog):
    def __init__(self, tablemodel, parent=None):
        BaseDialog.__init__(self, parent)
        self.model = tablemodel
        self.setWindowTitle(_("New Row"))

        label = QtGui.QLabel(u"%s %s"% (
            _("New Row for table"), self.model.tableName()))

        self.insertWidget(label)

        frame = QtGui.QFrame()

        layout = QtGui.QFormLayout(frame)

        record = self.model.record()
        self.inputs = []
        for i in range(record.count()):
            input_ = DefaultLineEdit()
            self.inputs.append(input_)
            layout.addRow(record.fieldName(i), input_)

        self.enableApply()


        self.scroll_area = QtGui.QScrollArea(self)
        self.scroll_area.setWidget(frame)
        self.scroll_area.setWidgetResizable(True)
        self.insertWidget(self.scroll_area)

        self.dirty = True
        self.set_check_on_cancel(True)

    def sizeHint(self):
        return QtCore.QSize(500, 500)

    @property
    def record(self):
        new_record = self.model.record()
        new_record.clearValues()
        removals = []
        for i in range(new_record.count()):
            input_ = self.inputs[i]
            if input_.isChecked():
                removals.append(i)
                #new_record.setGenerated(i, False)
            else:
                new_record.setValue(i, input_.text())

        for row in removals:
            new_record.remove(row)

        print new_record.count()
        for i in range(new_record.count()):
            print new_record.value(i).toString()

        return new_record

if __name__ == "__main__":
    import gettext
    gettext.install("")

    app = QtGui.QApplication([])

    from lib_openmolar.admin.connect import DemoAdminConnection
    from lib_openmolar.admin.qt4.classes import MyModel
    sc = DemoAdminConnection()
    sc.connect()

    model = MyModel(db=sc)
    model.setTable("diary_calendar")
    while True:
        dl = NewRowDialog(model)
        if dl.exec_():
            print dl.record
        else:
            break
