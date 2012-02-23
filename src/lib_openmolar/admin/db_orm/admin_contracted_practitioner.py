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
Provides a SchemaGenerator and DemoGenerator for the
contracted practitioner table
'''
from random import randint, choice
from PyQt4 import QtSql

from lib_openmolar.admin.table_schema import TableSchema
from lib_openmolar.common import common_db_orm

TABLENAME = "contracted_practitioners"

SCHEMA = '''
ix SERIAL NOT NULL,
patient_id INTEGER NOT NULL REFERENCES patients(ix),
practitioner_id INTEGER NOT NULL REFERENCES practitioners(ix),
contract_type VARCHAR(20),
start_date DATE NOT NULL DEFAULT CURRENT_DATE,
end_date DATE,
comments VARCHAR(255),
CONSTRAINT pk_contracted_practitioners PRIMARY KEY (ix)
'''


class SchemaGenerator(TableSchema):
    '''
    A custom object which lays out the schema for this table.
    '''
    def __init__(self):
        TableSchema.__init__(self, TABLENAME, SCHEMA)
        self.comment = _('links a patient to their regular practitioner')

class DemoGenerator(object):
    def __init__(self, database=None):

        q_query= QtSql.QSqlQuery(
            "select min(ix), max(ix) from patients", database)
        if q_query.first():
            self.min_patient_id = q_query.value(0).toInt()[0]
            self.max_patient_id = q_query.value(1).toInt()[0]
        else:
            self.min_patient_id, self.max_patient_id = 0,0

        q_query= QtSql.QSqlQuery('''select ix from practitioners
        where type='dentist' ''', database)

        self.dentist_ids = []
        while q_query.next():
            self.dentist_ids.append(q_query.value(0).toInt()[0])

        self.length = self.max_patient_id - self.min_patient_id

        self.record = common_db_orm.InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf('address_cat'))
        self.record.remove(self.record.indexOf('end_date'))
        self.record.remove(self.record.indexOf('start_date'))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''

        for patient_id in xrange(self.min_patient_id, self.max_patient_id+1):
            self.record.clearValues()
            dent_id = choice(self.dentist_ids)

            #set values, or allow defaults
            self.record.setValue('patient_id', patient_id)
            self.record.setValue('practitioner_id', dent_id)
            self.record.setValue('contract_type', "dentist")
            self.record.setValue('comments', "random")

            yield self.record.insert_query


if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries().next()