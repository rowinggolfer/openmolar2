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



class NotesClinicalDB(object):
    def __init__(self, patient_id):
        #:
        self.patient_id = patient_id

        #:
        self.exists_in_db = True

        self._records = None

    def get_records(self):
        '''
        get the records from the database
        '''
        self._records = []
        query = 'SELECT * from notes_clinical WHERE patient_id = ?'
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

    def to_html(self):
        '''
        returns the notes in html form
        '''
        html =  u'''<div align='center'><table width='100%%' border='1'>
        <tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
        '''% (_("Date"), _("Clinician"), _("Assistant"), _("notes"))

        for line in self.records:

            author = line.value("author").toInt()[0]
            co_author = line.value("co_author").toInt()[0]

            author_repr = SETTINGS.users.get_avatar_html(author)
            co_author_repr = SETTINGS.users.get_avatar_html(co_author)

            html += u'''<tr><td>%s</td><td>%s</td><td>%s</td><td>
            <pre>%s</pre></td></tr>'''% (
                line.value('open_time').toDateTime().toString(
                    QtCore.Qt.DefaultLocaleShortDate),
                author_repr, co_author_repr,
                line.value("line").toString())


        return html + '</table></div>'

if __name__ == "__main__":



    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    object = NotesClinicalDB(1)

    print object.to_html()
