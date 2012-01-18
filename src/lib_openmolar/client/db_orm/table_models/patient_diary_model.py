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


from PyQt4 import QtGui, QtSql

class PatientDiaryModel(QtSql.QSqlQueryModel):
    def __init__(self):
        QtSql.QSqlQueryModel.__init__(self)

    def set_patient(self, patient_id):
        query = '''select start, finish, clinician_type, clinician_spec,
        reason1, reason2, length, parent, period, comment
        from diary_patients join diary_appointments
        on appt_ix = diary_appointments.ix where patient=?'''
        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        q_query.addBindValue(patient_id)
        q_query.exec_()
        self.setQuery(q_query)

if __name__ == "__main__":
    from PyQt4 import QtGui
    from lib_openmolar.client.connect import ClientConnection
    app = QtGui.QApplication([])

    cc = ClientConnection()
    cc.connect()

    model = PatientDiaryModel()
    model.set_patient(1)

    dl = QtGui.QTableView()
    dl.setModel(model)
    dl.show()
    app.exec_()
