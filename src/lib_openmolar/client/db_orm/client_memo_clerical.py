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

'''
gets/sets a record in the clinical memo table
'''

from PyQt4 import QtCore, QtSql


from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "clerical_memos"

class MemoClericalDB(InsertableRecord):
    def __init__(self, patient_id):
        self.tablename = TABLENAME
        #:
        self.patient_id = patient_id

        #:
        self.exists_in_db = True

        query = 'SELECT * from %s WHERE patient_id = ? limit 1'% TABLENAME
        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        q_query.addBindValue(patient_id)
        q_query.exec_()

        if not q_query.next(): # no memos exist.
            self.exists_in_db = False
        record = q_query.record()
        QtSql.QSqlQuery.__init__(self, record)

        ## make a copy (a marker of database state)
        self.orig = QtSql.QSqlRecord()
        QtSql.QSqlQuery.__init__(self.orig, record)

    @property
    def is_dirty(self):
        return self != self.orig

    @property
    def memo(self):
        return self.value("memo").toString()

    def commit_changes(self):
        if not self.is_dirty:
            return

        self.setValue("checked_by", SETTINGS.user)
        if self.exists_in_db:
            q_query = self._update_query()
        else:
            self.setValue("patient_id", self.patient_id)
            self.setValue("checked_date", QtCore.QDate.currentDate())

            query, values = self.insert_query
            q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
            q_query.prepare(query)
            for value in values:
                q_query.addBindValue(value)

        q_query.exec_()
        if not q_query.lastError().isValid():
            QtSql.QSqlQuery.__init__(self.orig, self) # update self.orig
            return True
        else:
            print q_query.lastError().text()
            SETTINGS.psql_conn.emit_caught_error(q_query.lastError())

    def _update_query(self):
        changes, values = "", []
        for i in range(self.count()):
            if self.field(i) != self.orig.field(i):
                changes += "%s = ?,"% self.field(i).name()
                values.append(self.field(i).value())

        changes = changes.rstrip(",")
        query = "UPDATE %s set %s WHERE patient_id=?"% (TABLENAME, changes)

        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        for value in values:
            q_query.addBindValue(value)

        q_query.addBindValue(self.patient_id)

        return q_query

if __name__ == "__main__":

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    object = MemoClericalDB(1)

    for i in range(object.count()):
        field = object.field(i)
        print u"%s:%s"% (field.name(), field.value().toString())