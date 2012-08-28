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

from lib_openmolar.common.qt4.dialogs import BaseDialog



class XrayTreatmentDialog(BaseDialog):
    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)

        self.setWindowTitle(_("Radiographic Treatments"))

        frame = QtGui.QFrame()
        layout = QtGui.QFormLayout(frame)

        self.spin_boxes = []
        for code in SETTINGS.PROCEDURE_CODES.xray_codes:
            sb = QtGui.QSpinBox()
            sb.proc_code = code
            self.spin_boxes.append(sb)

            layout.addRow(code.description, sb)

        self.insertWidget(frame)

        self.enableApply(True)

    @property
    def proc_codes(self):
        for sb in self.spin_boxes:
            for i in range(sb.value()):
                yield sb.proc_code

    @property
    def date(self):
        return self.date_edit.date()

if __name__ == "__main__":



    app = QtGui.QApplication([])
    from lib_openmolar.client.connect import DemoClientConnection

    cc = DemoClientConnection()
    cc.connect()

    dl = XrayTreatmentDialog()
    if dl.exec_():
        print dl.proc_codes
