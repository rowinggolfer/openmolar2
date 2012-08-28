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
Provides Perio_BpeDB class
'''

from PyQt4 import QtSql
from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "perio_bpe"

class NewPerioBPERecord(InsertableRecord):
    def __init__(self):
        InsertableRecord.__init__(
            self, SETTINGS.psql_conn, TABLENAME)

    @property
    def comment(self):
        return unicode(self.value('comment').toString())

    def commit(self):
        self.remove(self.indexOf("checked_date"))
        query, values = self.insert_query

        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        for value in values:
            q_query.addBindValue(value)
        if not q_query.exec_():
            print q_query.lastError().text()
            SETTINGS.psql_conn.emit_caught_error(q_query.lastError())


class PerioBpeDB(object):
    '''
    class to get BPE information
    '''
    def __init__(self, patient_id):
        #: the underlying list of QSqlRecords
        self.record_list = []

        query = '''select checked_date, values, comment, checked_by
        from %s where patient_id=? order by checked_date desc'''% TABLENAME

        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        q_query.addBindValue(patient_id)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()
            self.record_list.append(record)

    @property
    def records(self):
        '''
        yields all BPE scores as tuples
        (date (qdate), checked_by (str), values (str), comment (str))
        '''

        for record in self.record_list:
            yield ( record.value("checked_date").toDate(),
                    record.value("checked_by").toString(),
                    record.value("values").toString(),
                    record.value("comment").toString())

    @property
    def current_bpe(self):
        '''
        returns the most recently recorded BPE score
        '''
        if self.record_list == []:
            return None
        current = self.record_list[0]
        return (    current.value("checked_date").toDate(),
                    current.value("checked_by").toString(),
                    current.value("values").toString(),
                    current.value("comment").toString())

if __name__ == "__main__":

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    obj = PerioBpeDB(1)
    bpes = obj.records

    print "%d records"% len(obj.records)

    for record in obj.records:
        print record.value("checked_date").toString(),
        print record.value("checked_by").toString(),
        print record.value("values").toString(),
        print record.value("comments").toString()

    print obj.current_bpe
