#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2013, Neil Wallace <neil@openmolar.com>                   ##
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
This module provides the TextFields Class
'''

from PyQt4 import QtSql

TABLENAME = "text_fields"

class TextFieldsDB(object):
    def __init__(self):
        self._text_fields = {}
        query = "select key, data from %s"% TABLENAME
        q_query = QtSql.QSqlQuery(query, SETTINGS.psql_conn)
        while q_query.next():
            record = q_query.record()
            key = unicode(record.value('key').toString())
            data = unicode(record.value('data').toString())
            self._text_fields[key] = data

    def __getitem__(self, key):
        return self._text_fields.__getitem__(key)

    def get(self, key, default=None):
        return self._text_fields.get(key, default)

if __name__ == "__main__":

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    object = TextFieldsDB()

    print object['trt1']

