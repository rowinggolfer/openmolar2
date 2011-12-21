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
Provides a SchemaGenerator and DemoGenerator for the notes_clinical table
'''
from random import randint, choice

from lib_openmolar.admin import table_schema
from lib_openmolar.common import common_db_orm

from PyQt4 import QtSql, QtCore

SCHEMA = '''
ix SERIAL NOT NULL,
patient_id INTEGER NOT NULL REFERENCES patients(ix),
open_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
commit_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
type notes_clinical_type NOT NULL DEFAULT 'observation',
line TEXT DEFAULT NULL,
author INTEGER NOT NULL REFERENCES users(ix),
co_author INTEGER REFERENCES users(ix),
committed bool NOT NULL DEFAULT false,
CONSTRAINT pk_notes_clinical PRIMARY KEY (ix)
'''

TABLENAME = "notes_clinical"


class SchemaGenerator(table_schema.TableSchema):
    '''
    A custom object which lays out the schema for the patient table.
    '''
    def __init__(self):
        table_schema.TableSchema.__init__(self, TABLENAME, SCHEMA)

class DemoGenerator(object):
    def __init__(self, database=None):
        q_query= QtSql.QSqlQuery(
            "select min(ix), max(ix) from patients", database)
        if q_query.first():
            self.min_patient_id = q_query.value(0).toInt()[0]
            self.max_patient_id = q_query.value(1).toInt()[0]
        else:
            self.min_patient_id, self.max_patient_id = 0,0

        self.clinicians = []
        q_query= QtSql.QSqlQuery(
            "select user_id from view_practitioners", database)
        while q_query.next():
            self.clinicians.append(q_query.value(0).toInt()[0])

        self.authors = []
        q_query= QtSql.QSqlQuery(
            "select ix from users", database)
        while q_query.next():
            self.authors.append(q_query.value(0).toInt()[0])

        for clinician in self.clinicians:
            self.authors.remove(clinician)

        self.length = 500

        self.record = common_db_orm.InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        today = QtCore.QDateTime.currentDateTime()
        self.record.remove(self.record.indexOf('type'))

        for i in xrange(0, self.length):
            self.record.clearValues()
            self.record.setValue('line',
                u"a line of clinical notes. \nrandom %06d"% randint(1,10000))
            self.record.setValue('patient_id',
                randint(self.min_patient_id, self.max_patient_id))

            self.record.setValue('author', choice(self.clinicians))
            self.record.setValue('co_author', choice(self.authors + [None]))
            t_stamp = today.addSecs(- randint(0, 86400))
            t_stamp = t_stamp.addDays(- randint(0, 4000))

            self.record.setValue('open_time', t_stamp)
            self.record.setValue('commit_time', t_stamp)
            self.record.setValue('committed', True)

            yield self.record.insert_query


if __name__ == "__main__":
    from lib_openmolar.admin.connect import AdminConnection
    sc = AdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    i = 0
    query = builder.demo_queries()
    q = query.next()
    while q and i<3:
        print q
        q = query.next()
        i += 1