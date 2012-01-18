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
Provides a SchemaGenerator and DemoGenerator for the address_link table
'''
from random import randint
from PyQt4 import QtSql

from lib_openmolar.admin.table_schema import TableSchema
from lib_openmolar.common import common_db_orm

SCHEMA = '''
ix SERIAL NOT NULL,
address_cat address_type NOT NULL DEFAULT 'home',
patient_id INTEGER NOT NULL REFERENCES patients(ix),
address_id INTEGER NOT NULL REFERENCES addresses(ix),
from_date DATE NOT NULL DEFAULT CURRENT_DATE,
to_date DATE,
mailing_pref mailing_pref_type /*custom enum type*/,
comments VARCHAR(255),
CONSTRAINT pk_address_link PRIMARY KEY (ix)
'''

TABLENAME = "address_link"


class SchemaGenerator(TableSchema):
    '''
    A custom object which lays out the schema for this table.
    '''
    def __init__(self):
        TableSchema.__init__(self, "address_link", SCHEMA)
        self.comment = _(
'''links the unique id of an address to the unique id of a patient,
along with some other information (home, work etc..)
allowing a many-to-many relationship for addresses''')

class DemoGenerator(object):
    def __init__(self, database=None):

        q_query= QtSql.QSqlQuery(
            "select min(ix), max(ix) from patients", database)
        if q_query.first():
            self.min_patient_id = q_query.value(0).toInt()[0]
            self.max_patient_id = q_query.value(1).toInt()[0]
        else:
            self.min_patient_id, self.max_patient_id = 0,0

        q_query= QtSql.QSqlQuery(
            "select min(ix), max(ix) from addresses", database)
        if q_query.first():
            self.max_address_id = q_query.value(1).toInt()[0]
            self.min_address_id = q_query.value(0).toInt()[0]

            #reserve id number 1 for the practice address.
            if self.min_address_id == 1 and self.max_address_id > 1:
                self.min_address_id == 2

        else:
            self.min_address_id, self.max_address_id = 0,0

        self.length = self.max_patient_id - self.min_patient_id

        self.record = common_db_orm.InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf('address_cat'))
        self.record.remove(self.record.indexOf('to_date'))
        self.record.remove(self.record.indexOf('from_date'))
        self.record.remove(self.record.indexOf('mailing'))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''

        for patient_id in xrange(self.min_patient_id, self.max_patient_id+1):
            self.record.clearValues()
            address_id = (randint(self.min_address_id, self.max_address_id))

            #set values, or allow defaults
            self.record.setValue('patient_id', patient_id)
            self.record.setValue('address_id', address_id)

            yield self.record.insert_query


if __name__ == "__main__":
    from lib_openmolar.admin.connect import AdminConnection

    sc = AdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries().next()