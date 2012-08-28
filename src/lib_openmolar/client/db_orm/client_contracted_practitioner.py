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

'''
Provides ContractedPractitionerDB class
'''

from PyQt4 import QtSql
from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "contracted_practitioners"


class NewContractedPractitionerRecord(InsertableRecord):
    def __init__(self):
        InsertableRecord.__init__(self,
            SETTINGS.psql_conn, TABLENAME)

    @property
    def comment(self):
        return unicode(self.value('comment').toString())

    def commit(self):
        query, values = self.insert_query

        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        for value in values:
            q_query.addBindValue(value)
        if not q_query.exec_():
            print q_query.lastError().text()
            SETTINGS.psql_conn.emit_caught_error(q_query.lastError())


class ContractedPractitionerDB(object):
    '''
    class to get contracted practitioner info
    '''
    def __init__(self, patient_id):
        self.record_list = []

        query = '''select ix, practitioner_id,
        contract_type, start_date, end_date, comments
        from %s where patient_id=? and
        (end_date is NULL or end_date <= current_date)  '''% TABLENAME

        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        q_query.addBindValue(patient_id)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()
            self.record_list.append(record)

    @property
    def records(self):
        '''
        returns a list of all records (type QtSql.QSqlRecords) found
        '''
        records = []
        for record in self.record_list:
            yield (record.value("ix").toInt()[0],
                    record.value("practitioner_id").toInt()[0],
                    record.value("start_date").toDate(),
                    record.value("end_date").toDate(),
                    record.value("contract_type").toString(),
                    record.value("comments").toString())

    @property
    def current_contracted_dentist(self):
        for record in self.records:
            if record[4] == "dentist":
                return SETTINGS.practitioners.value(record[1])

    def details_html(self):

        dent, hyg = None, None
        for record in self.records:
            if record[4] == "dentist":
                dent = SETTINGS.practitioners.value(record[1])
                dent_no = record[1]
            elif record[4] == "hygienist":
                hyg = SETTINGS.practitioners.value(record[1])
                hyg_no = record[1]

        if dent is None:
            dent_no = -1
            dent_cell = '''<div>%s
            <a href='edit_contract'>%s</a></div>'''% (
            _("NO PRACTITIONER!"),_("Add"))
        else:
            dent_cell = '''<img src="%s" height="70" alt="%s" />'''% (
            dent.avatar_resource, dent.abbrv_name)

        if hyg is None:
            hyg_no = -1
            hyg_cell = '''<div>
            <a href='edit_contract'>%s</a></div>'''% (_("Add"))
        else:
            hyg_cell = '''<img src="%s" height="70" alt="%s"/>'''% (
            hyg.avatar_resource, hyg.abbrv_name)


        html = u'''<table width = "100%%" border="1">
        <tr><td>%s</td><td>%s</td></tr>
        <tr><td><a href='edit_reg_dent %d'>%s</a></td>
        <td><a href='edit_reg_hyg %d'>%s</a></td></tr></table>'''% (
        _("Regular Dentist"), _("Hygienist"),
        dent_no, dent_cell, hyg_no, hyg_cell)

        return html

if __name__ == "__main__":

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    obj = ContractedPractitionerDB(1)
    for record in obj.records:
        print record

    print obj.details_html()