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
Provides a SchemaGenerator and DemoGenerator for procedure_codes table
'''
from PyQt4 import QtCore, QtSql

from lib_openmolar.admin import table_schema
from lib_openmolar.common import common_db_orm


from lib_openmolar.common import SETTINGS
from lib_openmolar.admin import qrc_resources


SCHEMA = '''
ix SERIAL,
category int not NULL default 1,
code VARCHAR(8),
description VARCHAR(140),
CONSTRAINT pk_procedure_codes PRIMARY KEY (ix),
CONSTRAINT unique_procedure_codes UNIQUE (code)
'''

TABLENAME = "procedure_codes"


class SchemaGenerator(table_schema.TableSchema):
    '''
    A custom object which lays out the schema for this table.
    '''
    def __init__(self):
        table_schema.TableSchema.__init__(self, TABLENAME, SCHEMA)

class DemoGenerator(object):
    def __init__(self, database):
        self.length = len(SETTINGS.PROCEDURE_CODES)

        self.record = common_db_orm.InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''

        for code in SETTINGS.PROCEDURE_CODES:
            self.record.clearValues()

            #set values, or allow defaults
            self.record.setValue('category', code.cat_no)
            self.record.setValue('code', code.code)
            self.record.setValue('description', code.description)
            yield self.record.insert_query

if __name__ == "__main__":
    from lib_openmolar.admin.connect import AdminConnection
    sc = AdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries().next()
