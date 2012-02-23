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
Provides a SchemaGenerator and DemoGenerator for the telephone_link table'''

from random import randint
from PyQt4 import QtSql

from lib_openmolar.admin.table_schema import TableSchema
from lib_openmolar.common import common_db_orm

SCHEMA = '''
ix SERIAL NOT NULL,
tel_cat telephone_type NOT NULL DEFAULT 'home',
patient_id INTEGER NOT NULL REFERENCES patients(ix),
tel_id INTEGER NOT NULL REFERENCES telephone(ix),
comment VARCHAR(240),
CONSTRAINT pk_telephone_link PRIMARY KEY (ix)
'''

TABLENAME = "telephone_link"


class SchemaGenerator(TableSchema):
    '''
    A custom object which lays out the schema for this table.
    '''
    def __init__(self):
        TableSchema.__init__(self, TABLENAME, SCHEMA)
        self.comment = _(
'''links the unique id of an telephone number to the unique id of a patient,
along with some other information (home, work, mobile etc..)
allowing a many-to-many relationship''')


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
            "select min(ix), max(ix) from telephone", database)
        if q_query.first():
            self.min_tel_id = q_query.value(0).toInt()[0]
            self.max_tel_id = q_query.value(1).toInt()[0]
        else:
            self.min_tel_id, self.max_tel_id = 0,0

        self.length = self.max_patient_id - self.min_patient_id

        self.record = common_db_orm.InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf('tel_cat'))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        sql_list = []
        for patient_id in xrange(self.min_patient_id, self.max_patient_id+1):
            self.record.clearValues()
            tel_id = (randint(self.min_tel_id, self.max_tel_id))

            #set values, or allow defaults
            self.record.setValue("patient_id", patient_id)
            self.record.setValue("tel_id", tel_id)

            sql_list.append(self.record.insert_query)

        return sql_list

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries()[:1]
