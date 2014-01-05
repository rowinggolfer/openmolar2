#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
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
Provides a DemoGenerator for the notes_clinical table
'''
from random import randint, choice
from PyQt4 import QtSql, QtCore

from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "notes_clinical"

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

        self.record = InsertableRecord(database, TABLENAME)

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
            self.record.setValue('comitted', True)

            yield self.record.insert_query


if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    i = 0
    query = builder.demo_queries()
    q = query.next()
    while q and i<3:
        print q
        q = query.next()
        i += 1
