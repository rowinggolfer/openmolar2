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
Provides a DemoGenerator for the patients diary
'''

from PyQt4 import QtSql, QtCore
from lib_openmolar.common.db_orm import InsertableRecord


TABLENAME = "appointments"

class DemoGenerator(object):
    def __init__(self, database=None):
        self.database = database
        self.length = 3
        self.record = InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf("trt2"))
        self.record.remove(self.record.indexOf("memo"))

    def get_diary_id(self):
        '''
        poll the database for the demo exam diary_entry
        '''
        LOGGER.debug("polling diary_entries table for an appointment")
        q_query= QtSql.QSqlQuery(
            "select ix from diary_entries where etype='appointment' limit 1",
            self.database)
        if q_query.first():
            return q_query.value(0).toInt()[0]
        else:
            LOGGER.warning("No exam appointment found in diary table")
            return None

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('trt1', "exam")
        self.record.setValue('len', 15)
        self.record.setValue('preferred_practitioner', 1)
        self.record.setValue('diary_entry_id', self.get_diary_id())
        yield self.record.insert_query

        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('trt1', "fill")
        self.record.setValue('len', 30)
        self.record.setValue('preferred_practitioner', 1)
        yield self.record.insert_query

        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('trt1', "hyg")
        self.record.setValue('len', 30)
        self.record.setValue('preferred_practitioner', 3)
        yield self.record.insert_query



if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print "builder generator", builder.length

    for query in builder.demo_queries():
        print query
