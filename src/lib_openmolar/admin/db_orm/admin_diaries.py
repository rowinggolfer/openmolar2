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
Provides a DemoGenerator for the diaries table
'''

from PyQt4 import QtSql, QtCore
from lib_openmolar.common.db_orm import InsertableRecord


TABLENAME = "diaries"

class DemoGenerator(object):
    def __init__(self, database=None):
        self.length = 2
        self.record = InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf("active"))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        year = QtCore.QDate.currentDate().year()

        for id in range(1, 3):
            self.record.clearValues()
            self.record.setValue('user_id', id)
            self.record.setValue('book_start', QtCore.QDate(year, 1, 1))
            self.record.setValue('book_end', QtCore.QDate(year+3, 1, 1))
            self.record.setValue('comment', 'demo diary')
            yield self.record.insert_query


if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print "builder generator", builder.length

    for query in builder.demo_queries():
        print query
