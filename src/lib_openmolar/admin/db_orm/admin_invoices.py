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
This module provides Demo sql queries for the fees_raised table
'''

from lib_openmolar.admin.table_schema import TableSchema
from lib_openmolar.common.db_orm import InsertableRecord


SCHEMA = '''
ix SERIAL NOT NULL,
patient_id INTEGER NOT NULL REFERENCES patients(ix),
status_id INTEGER NOT NULL REFERENCES invoice_status(ix),
date_issued DATE NOT NULL DEFAULT CURRENT_DATE,
date_paid DATE,
total_fees DECIMAL(10,2) NOT NULL DEFAULT 0,
discount DECIMAL(10,2) NOT NULL DEFAULT 0,
amount_payable DECIMAL(10,2) NOT NULL DEFAULT 0,
other_details VARCHAR(240),
CONSTRAINT pk_invoices PRIMARY KEY (ix)
'''

TABLENAME = "invoices"


class SchemaGenerator(TableSchema):
    '''
    A custom object which lays out the schema for this table.
    '''
    def __init__(self):
        TableSchema.__init__(self, TABLENAME, SCHEMA)

class DemoGenerator(object):
    def __init__(self, database):
        self.length = 4

        self.record = InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf("date_issued"))
        self.record.remove(self.record.indexOf("discount"))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('status_id', 1)
        self.record.setValue('total_fees', 20.50)
        self.record.setValue('amount_payable', 20.50)
        yield self.record.insert_query

        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('status_id', 2)
        self.record.setValue('total_fees', 4.50)
        self.record.setValue('amount_payable', 4.50)
        yield self.record.insert_query


if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries()
