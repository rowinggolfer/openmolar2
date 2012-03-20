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
This module provides Demo sql queries for the treatment_chart table

this table stores data about how treatment is graphically
represented on the plan or completed chart.

the data is relatively unimportant, and it should be able to completely
repopulate this table by parsing data from the other treatment tables.
'''

from lib_openmolar.admin.table_schema import TableSchema
from lib_openmolar.common.db_orm import InsertableRecord

SCHEMA = '''
ix serial,
tooth_id INTEGER REFERENCES treatment_teeth(ix),
type tx_chart_type NOT NULL default 'tooth' /* which box to draw in */,
draw_text VARCHAR(12),
svg VARCHAR(30),
CONSTRAINT pk_treatment_chart PRIMARY KEY (ix),
CONSTRAINT treatment_chart_data CHECK (draw_text is NOT NULL or svg is NOT NULL)
'''

TABLENAME = "treatment_chart"


class SchemaGenerator(TableSchema):
    '''
    A custom object which lays out the schema for this table.
    '''
    def __init__(self):
        TableSchema.__init__(self, TABLENAME, SCHEMA)
        self.comment = _(
            '''treatment chart items - unimportant duplicate data''')

class DemoGenerator(object):
    def __init__(self, database=None):
        self.length = 0

        self.record = InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''

        return []

        '''
        self.record.setValue('tooth_id', 2)
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
        '''

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries()
