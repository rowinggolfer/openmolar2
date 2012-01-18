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
Provides StaticCommentsDB class
'''

from PyQt4 import QtSql
from lib_openmolar.common import common_db_orm


TABLENAME = "static_comments"

class CommentRecord(common_db_orm.InsertableRecord):
    def __init__(self):
        common_db_orm.InsertableRecord.__init__(self, SETTINGS.psql_conn, TABLENAME)

    @property
    def tooth_id(self):
        return self.value('tooth').toInt()[0]

    @property
    def text(self):
        return unicode(self.value('comment').toString())


class StaticCommentsDB(object):
    '''
    class to get static chart information
    '''
    def __init__(self, patient_id):
        #:
        self.patient_id = patient_id
        #:
        self.record_list = []
        self._orig_record_list = []

        query = 'select tooth, comment from %s where patient_id=?'% TABLENAME

        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        q_query.addBindValue(patient_id)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()

            new = CommentRecord()
            QtSql.QSqlQuery.__init__(new, record)

            ## make a copy (a marker of database state)
            orig = QtSql.QSqlRecord()
            QtSql.QSqlQuery.__init__(orig, record)

            #self.record_list.append(record)
            self.record_list.append(new)
            self._orig_record_list.append(orig)

    @property
    def records(self):
        '''
        returns a list of all records (type QtSql.QSqlRecords) found
        '''
        return self.record_list

    def is_dirty_record(self, i):
        return self.records[i] != self._orig_record_list[i]

    @property
    def is_dirty(self):
        if len(self.record_list) != len(self._orig_record_list):
            return True
        is_dirty = False
        for i in range(len(self.records)):
            is_dirty = is_dirty or self.is_dirty_record(i)
        return is_dirty

    def commit_changes(self):
        if not self.is_dirty:
            return
        for record in self.records:
            if not record in self._orig_record_list:
                query, values = record.insert_query
                q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
                q_query.prepare(query)
                for value in values:
                    q_query.addBindValue(value)
                if q_query.exec_():
                    self._orig_record_list.append(record)
                else:
                    print q_query.lastError().text()
                    SETTINGS.psql_conn.emit_caught_error(q_query.lastError())

    def add_comment_records(self, data_list):
        '''
        crown_list is a generator of ToothData types
        '''
        for data in data_list:
            new = CommentRecord()
            new.setValue("patient_id", self.patient_id)
            new.setValue("tooth", data.tooth_id)
            new.setValue("comment", data.comment)
            new.setValue("checked_by", SETTINGS.user)
            new.remove(new.indexOf('checked_date'))

            self.record_list.append(new)

            data.in_database = True


if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    obj = StaticCommentsDB(1)
    for record in obj.records:
        print record.tooth_id,
        print record.comment
