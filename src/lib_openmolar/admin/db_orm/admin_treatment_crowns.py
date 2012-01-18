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
This module provides Demo sql queries for the treatment_crowns table
'''
from PyQt4 import QtSql
from lib_openmolar.admin.table_schema import TableSchema
from lib_openmolar.common import common_db_orm

SCHEMA = '''
ix serial,
tooth_tx_id INTEGER REFERENCES treatment_teeth(ix),
type crown_type NOT NULL,
technition VARCHAR(30),
CONSTRAINT pk_treatment_crowns PRIMARY KEY (ix)
'''

TABLENAME = "treatment_crowns"


class SchemaGenerator(TableSchema):
    '''
    A custom object which lays out the schema for this table.
    '''
    def __init__(self):
        TableSchema.__init__(self, TABLENAME, SCHEMA)
        self.comment = _('''extension table for treatments - crowns''')

class DemoGenerator(object):
    def __init__(self, database=None):
        self.length = 1

        self.record = common_db_orm.InsertableRecord(database, TABLENAME)

        self.tooth_tx_id = 0

        q_query= QtSql.QSqlQuery(
            "select ix from treatment_teeth where treatment_id=3", database)
        if q_query.first():
            self.tooth_tx_id = q_query.value(0).toInt()[0]

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        self.record.setValue('tooth_tx_id', self.tooth_tx_id)
        self.record.setValue('type', "GO")
        self.record.setValue('technition', 'DTS')
        sql = self.record.insert_query

        yield sql

if __name__ == "__main__":
    from lib_openmolar.admin.connect import AdminConnection
    sc = AdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries()
