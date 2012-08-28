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
Provides a DemoGenerator for clincal_memos table
'''

from PyQt4 import QtSql

from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "clinical_memos"

class DemoGenerator(object):
    def __init__(self, database):

        q_query= QtSql.QSqlQuery(
            '''select ix from patients
            where last_name='POTTER' and first_name='HARRY' ''', database)

        self.length = 0
        self.patient_id = None

        if q_query.first():
            self.length = 1
            self.patient_id = q_query.value(0).toInt()[0]

        self.record = InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf('checked_date'))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        sql_list = []
        if self.patient_id:
            self.record.setValue('patient_id', self.patient_id)
            self.record.setValue('memo',
                "Nasty scar on forehead, present since birth")
            self.record.setValue('checked_by', 'demo_installer')
            sql_list.append(self.record.insert_query)

        return sql_list

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries()[:1]
