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
Provides a DemoGenerator for the diary_in_office table
'''

from PyQt4 import QtSql, QtCore
from lib_openmolar.common.db_orm import InsertableRecord


TABLENAME = "diary_in_office"

class DemoGenerator(object):
    def __init__(self, database=None):
        self.length = 820
        self.record = InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        date_ = QtCore.QDate.currentDate().addMonths(-1)
        finish_date = date_.addMonths(6)
        while date_ < finish_date:
            dayno = date_.dayOfWeek()
            if dayno in (6,7):
                date_ = date_.addDays(1)
                continue
            if dayno == 2:
                start = QtCore.QDateTime(date_, QtCore.QTime(13,0))
                end_ = QtCore.QDateTime(date_, QtCore.QTime(19,0))
            else:
                start = QtCore.QDateTime(date_, QtCore.QTime(9,0))
                end_ = QtCore.QDateTime(date_, QtCore.QTime(17,0))
            self.record.clearValues()
            self.record.setValue('diary_id', 1)
            self.record.setValue('start', start)
            self.record.setValue('finish', end_)
            self.record.setValue('comment', 'demo session')
            yield self.record.insert_query
            date_ = date_.addDays(1)

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print "builder generator", builder.length

    for query in builder.demo_queries():
        print query
