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
This module provides the TelephoneDB Class, which works accross
telephone and telephone_link orms, to return a list of values.
'''

from PyQt4 import QtSql

phone = '''<img height='20' width='20' alt="edit phone"
align='right' src='qrc:/icons/phone.png' />'''

TABLENAME = "telephone"

class TelephoneDB(object):
    def __init__(self, patient_id):
        self.record_list = []
        query = '''SELECT number, sms_capable, checked_date, tel_cat
from %s join telephone_link on telephone.ix = telephone_link.tel_id
WHERE patient_id = ? order by checked_date desc'''% TABLENAME
        q_query = QtSql.QSqlQuery(SETTINGS.database)
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
        return self.record_list

    def details_html(self):
        html = u"<a href = 'phone'>%s</a>"% phone
        for record in self.record_list:
            html += "%s (%s)<br />"% (
                record.value('number').toString(),
                record.value('tel_cat').toString())

        if self.record_list == []:
            html = u"%s%s"% (html, _("NO PHONE DETAILS!"))

        return html.rstrip("<br />")

if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    object = TelephoneDB(1)

    print object.records
    print object.details_html()
