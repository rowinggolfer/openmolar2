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
Provides a DemoGenerator for the patients diary
'''

from PyQt4 import QtSql, QtCore
from lib_openmolar.common.db_orm import InsertableRecord


TABLENAME = "diary_patients"

class DemoGenerator(object):
    def __init__(self, database=None):
        self.length = 0
        self.record = InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        ##TODO - yield some demos?
        return []

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print "builder generator", builder.length

    print builder.demo_queries()
