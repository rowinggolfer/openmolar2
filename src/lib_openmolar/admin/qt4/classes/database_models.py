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

from xml.dom import minidom
from PyQt4 import QtSql

class MyModel(QtSql.QSqlTableModel):
    def __init__(self, parent = None, db=None):
        super(MyModel, self).__init__(parent, db)
        self.setEditStrategy(QtSql.QSqlTableModel.OnRowChange)

class MyRelationalModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, parent = None, db=None):
        super(MyRelationalModel, self).__init__(parent, db)
        self.setEditStrategy(QtSql.QSqlTableModel.OnRowChange)

    def table_xml(self):
        dom = minidom.Document()
        root = dom.createElement("data")
        table_name = unicode(self.tableName())
        item_name = table_name.rstrip("s")
        for row in range(self.rowCount()):
            data_item = dom.createElement(item_name)

            record = self.record(row)
            for col in range(record.count()):
                field = record.field(col)
                #print field.name(), field.value().toString()
                data_sub_item = dom.createElement(field.name())
                text_node = dom.createTextNode(
                    unicode(field.value().toString()))
                data_sub_item.appendChild(text_node)
                data_item.appendChild(data_sub_item)

            root.appendChild(data_item)
        dom.appendChild(root)
        line_end = "</%s>"% item_name
        return dom.toxml().replace(line_end, line_end+"\n")

    def load_table_xml(self, dom, ommit_key=False):
        '''
        this will take an xml file, and put it into the current table
        '''
        query, columns = self.insert_query(ommit_key)
        psql_query = QtSql.QSqlQuery(self.database())
        item_name = unicode(self.tableName()).rstrip("s")

        rows = dom.getElementsByTagName(item_name)
        i = 1
        for row in rows:
            psql_query.prepare(query)
            for node in columns:
                vals = row.getElementsByTagName(node)
                try:
                    val = vals[0].firstChild.data.strip()
                except IndexError:
                    val = None
                except AttributeError:
                    val = ""
                if not val and node == "ix":
                    val = i
                    i+=1
                psql_query.addBindValue(val)

            psql_query.exec_()
            if psql_query.lastError().isValid():
                print "ERRROR IMPORTING %s - %s"% (
                    row.toxml(),
                    psql_query.lastError().text())

    def insert_query(self, ommit_key=False):
        query = "select * from %s limit 1"% self.tableName()
        q_query = QtSql.QSqlQuery(query, self.database())
        record = q_query.record()

        query = "INSERT into %s ("% self.tableName()
        values = ""
        columns = []
        for col in range(record.count()):
            column = record.fieldName(col)
            if not (column == "ix" and ommit_key):
                query += "%s, "% column
                values += "?, "
                columns.append(column)
        query = "%s) VALUES (%s)"% (query.rstrip(", "), values.rstrip(", "))

        return query, columns
