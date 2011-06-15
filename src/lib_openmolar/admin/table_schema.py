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
Provides base classes for the other admin orm classes
'''
import re
from PyQt4 import QtSql


class TableSchema(object):
    def __init__(self, tablename="unknown", schema = ""):
        self.schema = schema
        self.tablename = tablename
        self.comment = ""
        self.columns = []
        self.values_dict = {}
        self.primary_key = None
        self.apply_schema(schema)

    def apply_schema(self, schema):
        schema = re.sub("/\*(.*)\*/", "", schema)
        commands = schema.split(",")
        key_col = ""
        for command in commands:
            command = command.strip()
            if command == "":
                continue
            if command.startswith("CONSTRAINT"):
                continue
            col_name = command.split(" ")[0]
            self.columns.append(col_name)
            if "primary key" in command.lower():
                key_col = col_name
                self.primary_key = key_col

    def __repr__(self):
        return "Class table_schema.TableSchema - '%s' - %d columns"% (
            self.tablename, len(self.columns))

    @property
    def removal_queries(self):
        '''
        returns a list of sql queries to remove this table
        (and associated types from the database)
        '''
        sql = 'DROP TABLE IF EXISTS %s CASCADE'% self.tablename
        return [sql]

    @property
    def creation_queries(self):
        '''
        returns a list of sql queries used to create this table
        '''
        sql = 'CREATE TABLE %s (\n'% self.tablename
        sql += self.schema
        sql += ")"

        return [sql]

    @property
    def insert_query(self):
        '''
        often overwritten if row has a time stamp
        '''
        cols, vals = "", ""
        values = []
        for column_name in self.column_order:
            if column_name != self.primary_key:
                cols +=  "%s, "% column_name
                vals += "?,"
                values.append(self.values_dict.get([column_name]))
        sql = 'INSERT INTO %s (%s) VALUES (%s)'% (self.tablename,
            cols.rstrip(", "), vals.rstrip(", "))

        return (sql, values)



