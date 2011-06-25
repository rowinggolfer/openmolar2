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
Provides StaticFillsDB class
'''

from PyQt4 import QtSql
from lib_openmolar.common import common_db_orm

TABLENAME = "perio_pocketing"

class NewPerioPocketingRecord(common_db_orm.InsertableRecord):
    def __init__(self):
        common_db_orm.InsertableRecord.__init__(self, SETTINGS.database, TABLENAME)

    @property
    def comment(self):
        return unicode(self.value('comment').toString())

    def commit(self):
        self.remove(self.indexOf("checked_date"))
        query, values = self.insert_query

        q_query = QtSql.QSqlQuery(SETTINGS.database)
        q_query.prepare(query)
        for value in values:
            q_query.addBindValue(value)
        if not q_query.exec_():
            print q_query.lastError().text()
            SETTINGS.database.emit_caught_error(q_query.lastError())


class PerioPocketingDB(object):
    '''
    class to get static chart information about perio pocketing
    '''
    def __init__(self, patient_id):
        #: the underlying list of QSqlRecords
        self.record_list = []

        query = '''select checked_date, tooth, values, comment, checked_by
        from %s where patient_id=? order by checked_date'''% TABLENAME

        q_query = QtSql.QSqlQuery(SETTINGS.database)
        q_query.prepare(query)
        q_query.addBindValue(patient_id)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()
            self.record_list.append(record)
        self._records = None


    @property
    def records(self):
        '''
        returns a list of all records (type QtSql.QSqlRecords) found
        '''
        if self._records is None:
            self._records = {}
            for record in self.record_list:
                tooth = record.value("tooth").toInt()[0]
                data_values = str(record.value("values").toString())
                pockets = []
                for val in data_values:
                    try:
                        pockets.append(int(val, 16))
                    except ValueError:
                        pockets.append(0)
                self._records[tooth] = tuple(pockets)
        for key in self._records:
            yield (key, self._records[key])

if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    obj = PerioPocketingDB(1)
    bpes = obj.records

    for record in obj.records:
        print record
