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
This module provides Demo sql queries for the treatments table
'''

from lib_openmolar.admin.table_schema import TableSchema
from lib_openmolar.common.db_orm import InsertableRecord


SCHEMA = '''
ix SERIAL NOT NULL,
patient_id INTEGER NOT NULL REFERENCES patients(ix),
/* parent_id INTEGER REFERENCES treatments(ix) ON DELETE CASCADE, */
om_code VARCHAR(5) NOT NULL  /* REFERENCES PROCEDURE CODES????*/,
completed BOOL NOT NULL DEFAULT FALSE,
px_clinician INTEGER NOT NULL REFERENCES practitioners(ix),
px_date DATE NOT NULL DEFAULT CURRENT_DATE,
tx_clinician INTEGER REFERENCES practitioners(ix),
tx_date DATE,
added_by VARCHAR(20) NOT NULL DEFAULT CURRENT_USER,
comment VARCHAR(240),
CONSTRAINT pk_treatments PRIMARY KEY (ix),
CONSTRAINT completed_treatment_rule CHECK (NOT completed or tx_clinician is NOT NULL),
CONSTRAINT completed_treatment_rule2 CHECK (NOT completed or tx_date is NOT NULL)
'''

TABLENAME = "treatments"


class SchemaGenerator(TableSchema):
    '''
    A custom object which lays out the schema for this table.
    '''
    def __init__(self):
        TableSchema.__init__(self, TABLENAME, SCHEMA)
        self.comment = _('''base table for treatments planned or completed''')

class DemoGenerator(object):
    def __init__(self, database):
        self.length = 4

        self.record = InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf("px_date"))
        self.record.remove(self.record.indexOf("added_by"))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('om_code', "A01")
        self.record.setValue('completed', True)
        self.record.setValue('px_clinician', 1)
        self.record.setValue('tx_clinician', 1)
        self.record.setValue('tx_date', "now()")

        yield self.record.insert_query

        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('om_code', "D02")
        self.record.setValue('completed', False)
        self.record.setValue('px_clinician', 1)
        yield self.record.insert_query

        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('om_code', "F10")
        self.record.setValue('completed', False)
        self.record.setValue('px_clinician', 1)
        yield self.record.insert_query

        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('om_code', "E01")
        self.record.setValue('completed', False)
        self.record.setValue('px_clinician', 1)
        yield self.record.insert_query


if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries()
    print builder.record.insert_query