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


from PyQt4 import QtCore, QtGui, QtSql


class HistoryPage(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.model = QtSql.QSqlQueryModel(self)

        history_table = QtGui.QTableView()
        history_table.setModel(self.model)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(history_table)

        self.clear()
        self.connect_signals()

    def sizeHint(self):
        return QtCore.QSize(400,400)

    def minimumSizeHint(self):
        return QtCore.QSize(300,300)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def connect_signals(self, connect=True):
        pass

    def clear(self):
        self.model.clear()

    def load_patient(self):
        patient = SETTINGS.current_patient
        if patient is None:
            return
        query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        query.prepare('''
select description, om_code, completed,  tx_date, tx_clinician, tooth,
surfaces, material, comment
from treatments left join procedure_codes on
treatments.om_code = procedure_codes.code
left join treatment_teeth on treatment_teeth.treatment_id = treatments.ix
left join treatment_fills on treatment_fills.tooth_tx_id = treatment_teeth.ix
where patient_id=? order by tx_date, comment
        ''')
        query.addBindValue(patient.patient_id)
        query.exec_()
        self.model.setQuery(query)

if __name__ == "__main__":

    from lib_openmolar.client.connect import DemoClientConnection
    app = QtGui.QApplication([])

    cc = DemoClientConnection()
    cc.connect()
    hp = HistoryPage()

    dl = QtGui.QDialog()
    dl.setMinimumSize(400,200)
    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(hp)
    dl.exec_()
