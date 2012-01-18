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
Provides a SchemaGenerator for diary_slots which is a dummy table
'''

from lib_openmolar.admin.table_schema import TableSchema

from PyQt4 import QtSql, QtCore

'''
This module provides the DiarySlots Class
note - this table has NO DATA!
populated at runtime by the get_slots function
'''

SCHEMA = '''
start TIMESTAMP (0) WITH TIME ZONE NOT NULL,
length INTERVAL
'''
TABLENAME = "diary_slots"


class SchemaGenerator(TableSchema):
    '''
    A custom object which lays out the schema for the patient table.
    '''
    def __init__(self):
        TableSchema.__init__(self, "diary_slots", SCHEMA)
        self.comment = _('''dummy table,
        populated via a function working on the diary table proper''')

class DemoGenerator(object):
    def __init__(self, database=None):
        self.length = 0

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        return []

if __name__ == "__main__":
    from lib_openmolar.admin.connect import AdminConnection
    sc = AdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print "builder generator", builder.length
    i = 0
    query = builder.demo_queries()