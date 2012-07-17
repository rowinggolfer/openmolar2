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
Provides a DemoGenerator for the diary
'''
from random import randint
from PyQt4 import QtSql, QtCore

from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "diary_appointments"

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

        self.length = int(days * 6 * 5/7)

        self.record = InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        date = self.book_start.addDays(-1)

        while date < self.book_end:
            date = date.addDays(1)
            if date.dayOfWeek() > 5:
                continue

            year, month, day = date.year(), date.month(), date.day()

            self.record.clearValues()
            self.record.setValue('diary_id', 1)

            self.record.setValue('start',
                QtCore.QDateTime(year, month, day, 13, 00))
            self.record.setValue('finish',
                QtCore.QDateTime(year, month, day, 14, 00))
            self.record.setValue('type', 'lunch')

            yield self.record.insert_query

            for i in range(5):
                d = QtCore.QDateTime(
                    year, month, day, randint(9,16), randint(0,11)*5)
                self.record.setValue('start', d)
                self.record.setValue('finish', d.addSecs(randint(1,10) * 5 * 60))
                self.record.setValue('type', 'appointment')
                self.record.setValue('location', 'practice')
                self.record.setValue('comments', 'random demo appointment')
                yield self.record.insert_query

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
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
