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
Provides a DemoGenerator for static_comments table
'''
from random import randint
from PyQt4 import QtSql


from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "static_comments"

class DemoGenerator(object):
    def __init__(self, database=None):
        q_query= QtSql.QSqlQuery(
            "select min(ix), max(ix) from patients", database)
        if q_query.first():
            self.min_patient_id = q_query.value(0).toInt()[0]
            self.max_patient_id = q_query.value(1).toInt()[0]
        else:
            self.min_patient_id, self.max_patient_id = 0,0

        self.length = (self.max_patient_id - self.min_patient_id) * 24
        if self.length > 100:
            self.length = 100

        self.record = InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        comments = ["big tooth", "little tooth", "rotated tooth"]
        list_len = len(comments)-1

        unique_teeth = set([])
        while len(unique_teeth) < self.length:
            pt = randint(self.min_patient_id, self.max_patient_id)
            tooth = randint(1,32)
            unique_teeth.add((pt, tooth))


        for pt, tooth in unique_teeth:
            self.record.clearValues()

            #set values, or allow defaults
            self.record.setValue('patient_id', pt)
            self.record.setValue('tooth', tooth)
            self.record.setValue('checked_by', 'demo_installer')
            self.record.setValue('comment', comments[randint(0, list_len)])
            self.record.remove(self.record.indexOf('checked_date'))

            yield self.record.insert_query

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries().next()
