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
Provides a SchemaGenerator and DemoGenerator for the diary sessions
'''
from random import randint

from lib_openmolar.admin import table_schema
from lib_openmolar.common import common_db_orm


SCHEMA = '''
ix SERIAL NOT NULL,
practice_id INTEGER NOT NULL REFERENCES practices(ix),
start TIMESTAMP (0) WITH TIME ZONE NOT NULL,
finish TIMESTAMP WITH TIME ZONE NOT NULL,
comments VARCHAR(240),
CONSTRAINT pk_diary_sessions UNIQUE (ix)
'''

TABLENAME = "diary_sessions"

from PyQt4 import QtSql, QtCore

class SchemaGenerator(table_schema.TableSchema):
    '''
    A custom object which lays out the schema for the table.
    '''
    def __init__(self):
        table_schema.TableSchema.__init__(self, TABLENAME, SCHEMA)

class DemoGenerator(object):
    def __init__(self, database=None):
        q_query= QtSql.QSqlQuery(
            "select book_start, book_end from diary_settings", database)
        if q_query.first():
            self.book_start = q_query.value(0).toDate()
            self.book_end = q_query.value(1).toDate()
        else:
            self.book_start = QtCore.QDate.currentDate().addMonths(-12)
            self.book_end = QtCore.QDate.currentDate().addMonths(24)

        days = self.book_start.daysTo(self.book_end)

        self.length = int(days * 5/7)

        self.record = common_db_orm.InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        date = self.book_start.addDays(-1)

        while date < self.book_end:

            date = date.addDays(1)
            dayno = date.dayOfWeek()

            year, month, day = date.year(), date.month(), date.day()
            if dayno in (1,3,4):
                start = QtCore.QDateTime(year, month, day, 8, 30)
                finish = QtCore.QDateTime(year, month, day, 18, 0)
            elif dayno == 2:
                start = QtCore.QDateTime(year, month, day, 8, 30)
                finish = QtCore.QDateTime(year, month, day, 19, 0)
            elif dayno == 5:
                start = QtCore.QDateTime(year, month, day, 8, 30)
                finish = QtCore.QDateTime(year, month, day, 17, 0)
            else: #no sessions for sat/sun
                continue

            self.record.clearValues()

            self.record.setValue('practice_id', 1)
            self.record.setValue('start', start)
            self.record.setValue('finish', finish)

            yield self.record.insert_query

            #test code
            '''for i in range(1000):
                s = QtCore.QDateTime(year, month, day, randint(9,12), randint(0,11)*5)
                self.record.setValue('start',s)
                self.record.setValue('finish',s.addSec5%s(10*60))
                self.record.setValue('type', 'appointment')
                yield self.record.insert_query
            '''




if __name__ == "__main__":
    from lib_openmolar.admin.connect import AdminConnection
    sc = AdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print "builder generator", builder.length
    print builder.book_start, builder.book_end
    i = 0
    query = builder.demo_queries()
    q = query.next()
    while q:
        #print q
        q = query.next()
        i += 1

    print i

