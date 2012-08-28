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
Provides a DemoGenerator for calendar
'''

from PyQt4 import QtSql, QtCore

from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "calendar"

class DemoGenerator(object):
    def __init__(self, database):
        self.length = 44

        self.record = InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        this_year = QtCore.QDate.currentDate().year()

        for year in (this_year-1, this_year, this_year+1, this_year+2):
            self.record.clearValues()
            self.record.setValue('date_id', QtCore.QDate(year,12,25))
            self.record.setValue('event', "Christmas Day")

            yield self.record.insert_query

            self.record.setValue('date_id', QtCore.QDate(year,12,26))
            self.record.setValue('event', "Boxing Day")

            yield self.record.insert_query

        for year in (this_year-1, this_year, this_year+1, this_year+2):
            self.record.clearValues()

            self.record.setValue('date_id', QtCore.QDate(year,1,1))
            self.record.setValue('event', "New Year's Day")

            yield self.record.insert_query

        for date, event  in (
            (QtCore.QDate(2009,4,10), "Good Friday"),
            (QtCore.QDate(2009,4,13), "Easter Monday"),
            (QtCore.QDate(2009,5,4), "Bank Holiday (UK)"),
            (QtCore.QDate(2009,5,25), "Bank Holiday (UK)"),
            (QtCore.QDate(2009,8,31), "Bank Holiday (UK)"),
            (QtCore.QDate(2009,12,27), "Bank Holiday (UK)"),
            (QtCore.QDate(2009,12,28), "Bank Holiday (UK)"),

            (QtCore.QDate(2010,1,3), "Bank Holiday (UK)"),
            (QtCore.QDate(2010,1,4), "Bank Holiday (SCOT)"),
            (QtCore.QDate(2010,4,2), "Good Friday"),
            (QtCore.QDate(2010,4,5), "Easter Monday"),
            (QtCore.QDate(2010,5,3), "Bank Holiday (UK)"),
            (QtCore.QDate(2010,5,31), "Bank Holiday (UK)"),
            (QtCore.QDate(2010,8,30), "Bank Holiday (UK)"),
            (QtCore.QDate(2010,12,27), "Bank Holiday (UK)"),
            (QtCore.QDate(2010,12,28), "Bank Holiday (UK)"),

            (QtCore.QDate(2011,1,3), "Bank Holiday (UK)"),
            (QtCore.QDate(2011,1,4), "Bank Holiday (SCOT)"),
            (QtCore.QDate(2011,4,22), "Good Friday"),
            (QtCore.QDate(2011,4,25), "Easter Monday"),
            (QtCore.QDate(2011,5,2), "Bank Holiday (UK)"),
            (QtCore.QDate(2011,5,30), "Bank Holiday (UK)"),
            (QtCore.QDate(2011,6,5), "Queen's Diamon Jubilee (UK)"),
            (QtCore.QDate(2011,8,29), "Bank Holiday (UK)"),
            (QtCore.QDate(2012,12,27), "Bank Holiday (UK)"),

            (QtCore.QDate(2012,1,2), "Bank Holiday (UK)"),
            (QtCore.QDate(2012,1,3), "Bank Holiday (SCOT)"),
            (QtCore.QDate(2012,4,6), "Good Friday"),
            (QtCore.QDate(2012,4,9), "Easter Monday"),
            (QtCore.QDate(2012,5,7), "Bank Holiday (UK)"),
            (QtCore.QDate(2012,6,4), "Bank Holiday (UK)"),
            (QtCore.QDate(2012,8,27), "Bank Holiday (UK)")):
                self.record.clearValues()

                self.record.setValue('date_id', date)
                self.record.setValue('event', event)

                yield self.record.insert_query

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    i = 0
    for query, values in builder.demo_queries():
        print query
        i+=1

    print i, "queries"
