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
This module provides Demo sql queries for the practice table
'''
from random import randint

from lib_openmolar.admin.table_schema import TableSchema
from lib_openmolar.common import common_db_orm

SCHEMA = '''
ix SERIAL NOT NULL /*Multiple Practices Allowed*/,
name VARCHAR(50) NOT NULL,
address_ix INTEGER REFERENCES addresses(ix),
website VARCHAR(50) DEFAULT NULL,
email1 VARCHAR(30) DEFAULT NULL,
email2 VARCHAR(30) DEFAULT NULL,
tel1 VARCHAR(30) DEFAULT NULL,
tel2 VARCHAR(30) DEFAULT NULL,
tel3 VARCHAR(30) DEFAULT NULL,
fax VARCHAR(30) DEFAULT NULL,
CONSTRAINT pk_practices PRIMARY KEY (ix)
'''

TABLENAME = "practices"
class SchemaGenerator(TableSchema):
    '''
    A custom object which lays out the schema for this table.
    '''
    def __init__(self):
        TableSchema.__init__(self, TABLENAME, SCHEMA)
        self.comment = _('''data on all known clinics''')

class DemoGenerator(object):
    def __init__(self, database):
        self.length = 1
        self.record = common_db_orm.InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        self.record.setValue('name', u"The Hogwarts Dental Clinic")
        self.record.setValue('website', u"http://en.wikipedia.org/wiki/Hogwarts")
        self.record.setValue('tel1', u"+44 1234 567890")
        self.record.setValue('address_ix', 1)
        sql = self.record.insert_query

        sql2 = '''INSERT INTO addresses
        (addr1, addr2, city, country, postal_cd, modified_by)
        VALUES (?,?,?,?,?,?)'''
        values = ('HOGWARTS SCHOOL OF WITCHCRAFT AND WIZARDRY',
        'THE FORBIDDEN FORREST', 'HOGSMEADE', 'SCOTLAND', 'HG1 1HG',
        'demo_installer')

        return [sql, (sql2, values)]

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries()
