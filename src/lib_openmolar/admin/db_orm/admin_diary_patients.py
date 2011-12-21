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
Provides a SchemaGenerator and DemoGenerator for the patients diary
'''

from lib_openmolar.admin import table_schema
from lib_openmolar.common import common_db_orm

from PyQt4 import QtSql, QtCore

SCHEMA = '''
ix SERIAL NOT NULL,
patient INTEGER NOT NULL REFERENCES patients(ix),
appt_ix INTEGER REFERENCES diary_appointments(ix),
clinician_type clinician_type NOT NULL default 'dentist',
clinician_spec INTEGER REFERENCES practitioners(ix),
reason1 varchar(20),
reason2 varchar(20),
length INTEGER NOT NULL default 0,
parent INTEGER,
period INTERVAL,
comment VARCHAR(240),
time_stamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT pk_diary_patients UNIQUE (ix),
CONSTRAINT ck_diary_periods CHECK (
    (parent IS NOT NULL AND period IS NOT NULL) OR
    (period IS NULL AND parent IS NULL))
'''

TABLENAME = "diary_patients"


class SchemaGenerator(table_schema.TableSchema):
    '''
    A custom object which lays out the schema for the patient table.
    '''
    def __init__(self):
        table_schema.TableSchema.__init__(self, TABLENAME, SCHEMA)
        self.comment = _('''storage for patients appointments''')

class DemoGenerator(object):
    def __init__(self, database=None):
        self.length = 0
        self.record = common_db_orm.InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        ##TODO - yield some demos?
        return []

if __name__ == "__main__":
    from lib_openmolar.admin.connect import AdminConnection
    sc = AdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print "builder generator", builder.length

    print builder.demo_queries()