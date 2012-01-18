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
This module provides the PatientDB Class
(for client interaction with records in the patients table)
'''

from PyQt4 import QtCore, QtSql

from lib_openmolar.common import common_db_orm

TABLENAME = "teeth_present"

class TeethPresentDB(common_db_orm.InsertableRecord):
    def __init__(self, patient_id):
        common_db_orm.InsertableRecord.__init__(self, SETTINGS.psql_conn,
            TABLENAME)

        #:
        self.patient_id = patient_id
        query = '''SELECT * from %s WHERE patient_id = ?
        order by ix desc limit 1'''% TABLENAME
        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        q_query.addBindValue(patient_id)
        q_query.exec_()
        q_query.next()
        record = q_query.record()
        QtSql.QSqlQuery.__init__(self, record)

        ## make a copy (a marker of database state)
        self.orig = QtSql.QSqlRecord()
        QtSql.QSqlQuery.__init__(self.orig, record)

    @property
    def is_dirty(self):
        return self != self.orig

    def commit_changes(self):

        if not self.is_dirty:
            return
        query = self.insert_query[0]

        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)

        for i in range(self.count()):
            if self.field(i).name() != "ix":
                #values.append(self.field(i).value())

                q_query.addBindValue(self.field(i).value())

        q_query.exec_()
        if not q_query.lastError().isValid():
            QtSql.QSqlQuery.__init__(self.orig, self) # update self.orig
            return True
        else:
            print q_query.lastError().text()
            SETTINGS.psql_conn.emit_caught_error(q_query.lastError())

if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    object = TeethPresentDB(1)

    for i in range(object.count()):
        field = object.field(i)
        print u"%s:%s"% (field.name(), field.value().toString())

    object.setValue("dent_key", 0)
    object.commit_changes()
