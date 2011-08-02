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
This module provides Demo sql queries for the treatment_fills table
'''

from lib_openmolar.admin import table_schema
from lib_openmolar.common import common_db_orm

SCHEMA = '''
ix serial,
treatment_id INTEGER REFERENCES treatments(ix),
tooth SMALLINT NOT NULL,
tx_type tooth_tx_type,
CONSTRAINT pk_treatment_teeth PRIMARY KEY (ix)
'''

TABLENAME = "treatment_teeth"


class SchemaGenerator(table_schema.TableSchema):
    '''
    A custom object which lays out the schema for this table.
    '''
    def __init__(self):
        table_schema.TableSchema.__init__(self, TABLENAME, SCHEMA)
        self.comment = _('''extension table for treatments - teeth''')

class DemoGenerator(object):
    def __init__(self, database=None):
        self.length = 3

        self.record = common_db_orm.InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        self.record.setValue('treatment_id', 2)
        self.record.setValue('tooth', 5)
        sql = self.record.insert_query

        yield sql

        self.record.setValue('treatment_id', 3)
        self.record.setValue('tooth', 4)
        sql = self.record.insert_query

        yield sql

        self.record.setValue('treatment_id', 4)
        self.record.setValue('tooth', 19)
        sql = self.record.insert_query

        yield sql

if __name__ == "__main__":
    from lib_openmolar.admin.connect import AdminConnection
    sc = AdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries()
