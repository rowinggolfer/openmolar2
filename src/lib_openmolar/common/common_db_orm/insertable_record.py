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

from PyQt4 import QtSql

class InsertableRecord(QtSql.QSqlRecord):
    def __init__(self, database, tablename):
        self.tablename = tablename
        record = database.record(tablename)
        QtSql.QSqlRecord.__init__(self, record)

        self.include_ix = False

    @property
    def insert_query(self):
        cols, vals = u"", u""
        values = []
        for i in range(self.count()):
            field = self.field(i)
            if not self.include_ix and field.name() == "ix":
                continue
            cols += u"%s, "% field.name()
            vals += "?, "
            values.append(field.value())
        cols = cols.rstrip(", ")
        vals = vals.rstrip(", ")

        sql = 'INSERT INTO %s (%s) VALUES (%s)'% (self.tablename, cols, vals)
        return (sql, values)

if __name__ == "__main__":
    pass
