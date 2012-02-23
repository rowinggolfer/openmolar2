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
This module provides Demo sql queries for the fees table
'''

from lib_openmolar.admin.table_schema import TableSchema
from lib_openmolar.common import common_db_orm


SCHEMA = '''
ix SERIAL NOT NULL,
patient_id INTEGER NOT NULL REFERENCES patients(ix),
fee DECIMAL(10,2) NOT NULL DEFAULT 0,
type fee_type NOT NULL DEFAULT 'other',
comment VARCHAR(240),
time_stamp TIMESTAMP NOT NULL DEFAULT NOW(),
CONSTRAINT pk_fees PRIMARY KEY (ix)
'''

TABLENAME = "fees"


class SchemaGenerator(TableSchema):
    '''
    A custom object which lays out the schema for this table.
    '''
    def __init__(self):
        TableSchema.__init__(self, TABLENAME, SCHEMA)

class DemoGenerator(object):
    def __init__(self, database):
        self.length = 4

        self.record = common_db_orm.InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf("time_stamp"))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('fee', 20.50)
        self.record.setValue('type', 'treatment')
        yield self.record.insert_query

        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('fee', 4.50)
        self.record.setValue('type', 'sundries')
        yield self.record.insert_query


if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries()
