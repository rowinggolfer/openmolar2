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
provides a schema and insertquery for the diary settings table
which stores calendar start dates and limits for each practice
'''

from PyQt4 import QtCore, QtSql

from lib_openmolar.admin.table_schema import TableSchema
from lib_openmolar.common import common_db_orm

SCHEMA = '''
ix serial,
practice_id INTEGER NOT NULL REFERENCES practices(ix),
book_start DATE NOT NULL,
last_day DATE NOT NULL,
book_end DATE NOT NULL,
CONSTRAINT pk_diary_settings PRIMARY KEY (ix),
CONSTRAINT ck_diary_limits CHECK (book_start<last_day and last_day<=book_end)
'''

TABLENAME = "diary_settings"


class SchemaGenerator(TableSchema):
    '''
    A custom object which lays out the schema for this table.
    '''
    def __init__(self):
        TableSchema.__init__(self, "diary_settings", SCHEMA)
        self.comment = _('diary settings')

class DemoGenerator(object):
    def __init__(self, database=None):
        self.length = 1

        self.record = common_db_orm.InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        this_year = QtCore.QDate.currentDate().year()
        start = QtCore.QDate(this_year,1,1)
        end = QtCore.QDate(this_year+2,12,31)

        self.record.setValue('practice_id', 1)
        self.record.setValue('book_start', start)
        self.record.setValue('book_end', end)
        self.record.setValue('last_day', QtCore.QDate.currentDate().addMonths(6))

        yield self.record.insert_query

if __name__ == "__main__":
    from lib_openmolar.admin.connect import AdminConnection
    sc = AdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries()
