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
This module provides Demo sql queries for the fees table
'''

from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "fees"

class DemoGenerator(object):
    def __init__(self, database):
        self.length = 4

        self.record = InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf("time_stamp"))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('fee', 20.50)
        self.record.setValue('type', 'treatment')
        yield self.record.insert_query

        self.record.clearValues()
        self.record.setValue('patient_id', 1)
        self.record.setValue('fee', 4.50)
        self.record.setValue('type', 'sundries')
        yield self.record.insert_query


if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries()
