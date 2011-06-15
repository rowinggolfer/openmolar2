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
Provides StaticRootsDB class
'''

from PyQt4 import QtSql
from lib_openmolar.common import common_db_orm


TABLENAME = "static_roots"

class RootRecord(common_db_orm.InsertableRecord):
    def __init__(self):
        common_db_orm.InsertableRecord.__init__(self, SETTINGS.database, TABLENAME)

    @property
    def tooth_id(self):
        return self.value('tooth').toInt()[0]

    @property
    def description(self):
        return unicode(self.value('description').toString())


    @property
    def comment(self):
        return unicode(self.value('comment').toString())


class StaticRootsDB(object):
    '''
    class to get static chart information
    '''
    def __init__(self, serialno):
        self.record_list, self.orig_record_list = [], []

        query = '''select tooth, description, has_rct, comment
        from %s where patient_id=?'''% TABLENAME

        q_query = QtSql.QSqlQuery(SETTINGS.database)
        q_query.prepare(query)
        q_query.addBindValue(serialno)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()

            new = RootRecord()
            QtSql.QSqlQuery.__init__(new, record)

            ## make a copy (a marker of database state)
            orig = QtSql.QSqlRecord()
            QtSql.QSqlQuery.__init__(orig, record)

            #self.record_list.append(record)
            self.record_list.append(new)
            self.orig_record_list.append(orig)

    @property
    def records(self):
        '''
        returns a list of all records (type QtSql.QSqlRecords) found
        '''
        return self.record_list

    def is_dirty_record(self, i):
        return self.record_list[i] != self.orig_record_list[i]

    @property
    def isDirty(self):
        if len(self.record_list) != len(self.orig_record_list):
            return True
        is_dirty = False
        for i in range(len(self.record_list)):
            is_dirty = is_dirty or self.is_dirty_record(i)
        return is_dirty

    def commit_changes(self):
        if not self.isDirty:
            return
        for record in self.record_list:
            if not record in self.orig_record_list:
                query, values = record.insert_query
                print query
                q_query = QtSql.QSqlQuery(SETTINGS.database)
                q_query.prepare(query)
                for value in values:
                    q_query.addBindValue(value)
                if not q_query.exec_():
                    print q_query.lastError().text()
                    SETTINGS.database.emit_caught_error(q_query.lastError())

    def add_root_records(self, data_list, patient_id):
        '''
        crown_list is a generator of ToothData types
        '''
        for data in data_list:
            new = RootRecord()
            new.setValue("patient_id", patient_id)
            new.setValue("tooth", data.tooth.ref)
            new.setValue("has_rct", data.has_rct)
            new.setValue("description", data.root_type)
            new.setValue("comment", data.comment)
            new.setValue("checked_by", SETTINGS.user)
            new.remove(new.indexOf('checked_date'))

            self.record_list.append(new)

if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    object = StaticRootsDB(1)
    print len(object.records)
    for record in object.records:
        print record.value("description").toString(),
        print record.value("comment").toString()
