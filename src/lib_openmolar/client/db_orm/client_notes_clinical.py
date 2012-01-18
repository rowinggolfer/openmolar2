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

TABLENAME = "notes_clinical"

from PyQt4 import QtCore, QtSql
from lib_openmolar.common.common_db_orm import InsertableRecord

class NotesClinicalDB(object):
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

    @property
    def has_new_note(self):
        return self._new_note is not None

    @property
    def new_note(self):
        if self._new_note is None:
            print "creating new clinical note with authors %s and %s"% (
                SETTINGS.user1, SETTINGS.user2)
            self._new_note = InsertableRecord(SETTINGS.psql_conn, TABLENAME)
            self._new_note.is_clinical = True
            self._new_note.setValue("open_time", QtCore.QDateTime.currentDateTime())

            if SETTINGS.user1:
                self._new_note.setValue("author", SETTINGS.user1.id)
            if SETTINGS.user2:
                self._new_note.setValue("co-author", SETTINGS.user2.id)
        return self._new_note

    def commit_note(self, note):
        '''
        note has been updated
        '''
        if not note in self._records:
            self._records.append(self._new_note)
        return True

    def get_records(self):
        '''
        get the records from the database

        .. note:
            A property of is_clinical is added to each record, and set as True
        '''
        self._records = []
        query = 'SELECT * from %s WHERE patient_id = ? order by open_time'% (
            TABLENAME)
        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        q_query.addBindValue(self.patient_id)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()
            record.is_clinical = True
            self._records.append(record)

    @property
    def records(self):
        '''
        returns a list of all records (type QtSql.QSqlRecords) found
        '''
        if self._records is None:
            self.get_records()
        return self._records

    def record_by_id(self, id):
        '''
        return the text of the record with a specific id
        '''
        for record in self.records:
            if record.value(0) == id:
                return record
        print "ERROR - clinical note record %d not found in memory"% id
        return None

if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    object = NotesClinicalDB(1)
    print object.to_html()

    note = object.create_new_note()
    object.commit_note(note)
    #print object.to_html()
    print object.is_dirty
