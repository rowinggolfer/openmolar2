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
This module provides the ClinicalNotesDB Class
(for client interaction with records in the notes_clinical table)
'''

from PyQt4 import QtCore, QtSql

class NotesClericalDB(object):
    _new_note = None
    _records = None
    def __init__(self, patient_id):
        #:
        self.patient_id = patient_id

    @property
    def is_dirty(self):
        ## todo - this does not allow for a commited note or an edited note
        if self._new_note is None:
            return False
        return self._new_note.value("line").toString() != ""

    def get_records(self):
        '''
        get the records from the database
        '''
        self._records = []

        query = '''SELECT * from notes_clerical WHERE patient_id = ?
        ORDER BY open_time'''
        q_query = QtSql.QSqlQuery(SETTINGS.database)
        q_query.prepare(query)
        q_query.addBindValue(self.patient_id)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()
            self._records.append(record)

    @property
    def records(self):
        '''
        returns a list of all records (type QtSql.QSqlRecords) found
        '''
        if self._records is None:
            self.get_records()
        return self._records


if __name__ == "__main__":



    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    object = NotesClericalDB(1)

    print object.records
