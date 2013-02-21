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
Provides a DemoGenerator for the diary_entries table
'''

from PyQt4 import QtSql, QtCore
from lib_openmolar.common.db_orm import InsertableRecord


TABLENAME = "diary_entries"

class DemoGenerator(object):
    def __init__(self, database=None):
        self.length = 820
        self.record = InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf("active"))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        year = QtCore.QDate.currentDate().year()
        date_ = QtCore.QDate(year, 1, 1)
        finish_year = year + 3
        while date_.year() < finish_year:
            if date_.dayOfWeek() < 6:
                start = QtCore.QDateTime(date_, QtCore.QTime(13,0))
                self.record.clearValues()
                self.record.setValue('diary_id', 1)
                self.record.setValue('start', start)
                self.record.setValue('finish', start.addSecs(3600))
                self.record.setValue('etype', 'lunch')
                yield self.record.insert_query
            date_ = date_.addDays(1)

        # now an entry for an exam done on patient one yesterday
        # (or previous work day)
        self.record.clearValues()
        date_ = QtCore.QDate.currentDate().adddays(-1)
        while date_.dayOfWeek > 6:
            date_.addDays(-1)
        start = QtCore.QDateTime(date_, QtCore.QTime(9,0))
        self.record.setValue('diary_id', 1)
        self.record.setValue('start', start)
        self.record.setValue('finish', start.addSecs(60*15))
        self.record.setValue('etype', 'appointment')
        yield self.record.insert_query


if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print "builder generator", builder.length

    for query in builder.demo_queries():
        print query
