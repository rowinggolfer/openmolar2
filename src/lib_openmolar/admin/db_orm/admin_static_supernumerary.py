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
Provides a DemoGenerator for static_supernumerary table
'''
from random import randint
from PyQt4 import QtSql

from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "static_supernumerary"

class DemoGenerator(object):
    def __init__(self, database):
        q_query= QtSql.QSqlQuery(
            "select min(ix), max(ix) from patients", database)
        if q_query.first():
            min_patient_id = q_query.value(0).toInt()[0]
            max_patient_id = q_query.value(1).toInt()[0]
            self.patient_id = randint(min_patient_id, max_patient_id)
        else:
            self.patient_id = 0

        self.length = 1

        self.record = InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf('checked_date'))
        self.record.remove(self.record.indexOf('is_erupted'))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''

        self.record.clearValues()
        #set values, or allow defaults
        self.record.setValue('patient_id', self.patient_id)
        self.record.setValue('mesial_neighbour', 9)
        self.record.setValue('distal_neighbour', 10)
        self.record.setValue('checked_by', 'demo_installer')

        yield self.record.insert_query

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries().next()
