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
This module provides the AddressObjects Class, and AddressRecord Class
(for client interaction with records in the addresses and address_link table)
'''

from PyQt4 import QtSql, QtCore

from lib_openmolar.common.common_db_orm import InsertableRecord
from lib_openmolar.common.datatypes import EditableField, OMType


class AddressRecord(InsertableRecord):
    '''
    A re-implementation of :doc:`InsertableRecord`
    which is self aware for editing purposes
    '''
    _editable_fields = None

    def __init__(self, record=None):
        if record is None:
            blank_record = SETTINGS.psql_conn.blank_address_record
            QtSql.QSqlRecord.__init__(self, blank_record)
        else:
            QtSql.QSqlRecord.__init__(self, record)

    @property
    def editable_fields(self):
        '''
        a property called by dialogs which edit this class
        hence the order is important!
        a list of tuples.
        item0 in the tuple is the field name used by the db
        item1 is the string displayed to the user.
        item3 is optional type
        '''
        if self._editable_fields is None:
            cat_field = EditableField('address_cat', _("Category"))
            cat_field.set_type(SETTINGS.OM_TYPES['address'])

            mail_field = EditableField('mailing', _('Mailing Preference'))
            mail_field.set_type(SETTINGS.OM_TYPES['mailing_pref'])
            mail_field.set_advanced()

            from_f = EditableField('from_date', _("Start Date for this address"))
            from_f.set_advanced()

            to_f = EditableField('to_date', _("Leaving Date for this address"))
            to_f.set_advanced()

            self._editable_fields = ([
                EditableField('addr1', _("Address Line 1"), required=True),
                EditableField('addr2', _("Address Line 2")),
                EditableField('addr3', _("Address Line 3")),
                EditableField('city', _('City'), required=True),
                EditableField('county', _('County')),
                EditableField('country', _('Country')),
                EditableField('postal_cd', _('Postal_cd'), required=True)],
                [cat_field,
                mail_field,
                from_f,
                to_f
                ])

        return self._editable_fields

    def details_html(self):
        html = u""
        cat = self.value('address_cat').toString()
        addr1 = unicode(self.value('addr1').toString()).title()
        addr2 = unicode(self.value('addr2').toString()).title()
        addr3 = unicode(self.value('addr3').toString()).title()
        city = self.value('city').toString()
        country = self.value('country').toString()
        pcde = self.value('postal_cd').toString()
        residents = self.value('known_residents').toInt()[0]

        html += '<i>- %s</i><br />'% cat
        if residents > 1:
            html = u"%s (%d)<br />"% (
                html.replace("<br />",""), residents)

        if addr1:
            html += u"%s <br />"% addr1
        if addr2:
            html += u"%s <br />"% addr2
        if addr3:
            html += u"%s <br />"% addr3
        if city:
            html += u"%s <br />"% city
        if country:
            html += u"%s <br />"% country
        if pcde:
            html += u"%s"% pcde
        else:
            html += _("Please get postal code!")

        return html

    def load_values(self, value_store):
        '''
        applies data gathered from a ui built on EditableFields to the object
        returns a tuple
        (Result (bool), ommisions (list of ommited fields))
        '''

        # step 1.. get the values the user has entered.
        for field_name in value_store:
            widg, field_type = value_store[field_name]
            if field_type == QtCore.QVariant.Date:
                self.setValue(field_name, widg.date())
            elif field_type == QtCore.QVariant.String:
                self.setValue(field_name, widg.text())
            elif type(field_type) == OMType:
                val = widg.itemData(widg.currentIndex())
                self.setValue(field_name, val)
            else:
                print "Whoops!" ## <-shouldn't happen

        # step 2.. see if all required fields are completed

        ommisions = []
        all_completed = True
        for editable_field in self.editable_fields:
            if editable_field.required:
                field_name = editable_field.fieldname

                if self.value(field_name).toString()== "":
                    all_completed = False
                    ommisions.append(editable_field.readable_fieldname)

        return (all_completed, ommisions)


class AddressObjects(object):
    '''
    instantiating this class
    grabs a list of :doc:`AddressRecord` types using the
    view_addresses pseudo table
    '''
    def __init__(self, patient_id):
        #: a pointer to the id of the :doc:`PatientModel`
        self.patient_id = patient_id
        self.get_records()

    def get_records(self):
        '''
        poll the database to get all address records associated with the
        patient_id given at init
        '''
        self.record_list, self.orig_record_list = [], []

        # this query LOOKS simple.. but the underlying view is VERY complex.
        query = '''
    select * from view_addresses where patient_id=? order by mailing_pref'''
        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        q_query.addBindValue(self.patient_id)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()

            #make a copy
            orig = QtSql.QSqlRecord(record)
            new = AddressRecord(record)

            if self.record_list == []:
                SETTINGS.set_last_used_address(new)

            self.record_list.append(new)
            self.orig_record_list.append(orig)

    @property
    def records(self):
        '''
        returns a list of all records (type QtSql.QSqlRecords) found
        '''
        return self.record_list

    def is_dirty_record(self, i):
        return self.record_list[i] != self.orig_record_list[i]

    def add_address_link(self, address_id, category = "home"):
        new_link = AddressLinkRecord()
        new_link.set_link(self.patient_id, address_id)
        new_link.setValue("modified_by", SETTINGS.user)
        new_link.setValue("address_cat", category)
        query, values = new_link.insert_query
        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        for value in values:
            q_query.addBindValue(value)
        if not q_query.exec_():
            print q_query.lastError().text()
        else:
            self.get_records()

    def break_address_link(self, address):
        '''
        need to put some code in here that alters the date in the address_link table
        '''
        print "break link"
        address.setValue("to_date", QtCore.QDate.currentDate())
        print address
        query = "UPDATE address_link set to_date=? WHERE ix=?"
        print query
        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        q_query.addBindValue(address.value('to_date'))
        q_query.addBindValue(address.value('ix'))

        q_query.exec_()
        if not q_query.lastError().isValid():
            result = False
        else:
            print q_query.lastError().text()

    @property
    def is_dirty(self):
        is_dirty = False
        for i in range(len(self.record_list)):
            is_dirty = is_dirty or self.is_dirty_record(i)
        return is_dirty

    def changes_html(self):
        '''
        an html representation of any changes to the object since __init__
        '''
        changes = "<body><div align='center'>"
        for i in range(len(self.record_list)):
            edited = self.record_list[i]
            orig = self.orig_record_list[i]

            changes += "<h4>Address %d - %s</h4>"% (i,
                orig.value('addr1').toString())

            if edited == orig:
                changes += "- no changes found<br />"
                continue

            changes += "<table width = '100%' border='2'>"
            changes += '''<tr><td><b>field</b></td><td><b>orig value</b></td>
            <td><b>changed value</b></td></tr>'''

            edit_fields = edited.editable_fields
            for edit_field in edit_fields[0]:
                if not edit_field: #separator
                    continue

                fieldname = edit_field.fieldname
                if edited.value(fieldname) == orig.value(fieldname):
                    continue

                changes += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"% (
                edit_field.readable_fieldname,
                orig.value(fieldname).toString(),
                edited.value(fieldname).toString())

            changes += "</table><br /><br />"
        changes += "</div></body>"
        return changes

    def commit_changes(self):
        result = True
        for i in range(len(self.record_list)):
            if self.is_dirty_record(i):
                record = self.record_list[i]
                orig = self.orig_record_list[i]
                changes, values = "", []
                for i in range(record.count()):
                    if record.field(i) != orig.field(i):
                        changes += "%s = ?,"% record.field(i).name()
                        values.append(record.field(i).value())

                changes = changes.rstrip(",")
                query = "UPDATE view_addresses set %s WHERE address_id=?"% changes
                print query
                q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
                q_query.prepare(query)
                for value in values + [record.value('address_id')]:
                    q_query.addBindValue(value)
                q_query.exec_()
                if not q_query.lastError().isValid():
                    result = False
                else:
                    print q_query.lastError().text()
        return result

    def details_html(self):
        '''
        an html representation of this object
        '''
        full_html = u""
        i = 0
        for record in self.record_list:

            html = u"<div><a href='edit_addy %d'>%s</a>%s</div>"% (
                i, SETTINGS.PENCIL, record.details_html())

            full_html += html+"<hr width=50% />"
            i += 1

        if full_html == "":
            full_html = u'''
            <div>NO ADDRESS FOUND!<a href='edit_addy'>%s</a></div>'''% _("Add")

        return full_html

    def who_else_lives_here(self, address_id):
        '''
        polls the database to get details of who else lives here now, or in the
        past.

        returns 2 lists. ([present occupants],[past occupants])
        the lists are in the form
        ["Mr John Smith 10/10/1964", "Mrs.... "]
        '''

        past_list, present_list = [], []

        present_query = '''select title, first_name, last_name, dob from patients
join address_link on patients.ix = address_link.patient_id
where address_id =? and patients.ix != ?
and (to_date is NULL or to_date > CURRENT_DATE) order by dob desc'''

        past_query = '''select title, first_name, last_name, dob from patients
join address_link on patients.ix = address_link.patient_id
where address_id =? and patients.ix != ?
and to_date <= CURRENT_DATE order by dob desc'''

        for query, list_ in (
        (present_query, present_list), (past_query, past_list)):
            q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
            q_query.prepare(query)
            q_query.addBindValue(address_id)
            q_query.addBindValue(self.patient_id)
            q_query.exec_()
            while q_query.next():
                record = q_query.record()
                list_.append(u"%s %s %s (%s)" %(
                    record.value("title").toString(),
                    record.value("first_name").toString(),
                    record.value("last_name").toString(),
                    record.value(
                        "dob").toDate().toString(SETTINGS.QDATE_FORMAT)))

        return present_list, past_list

if __name__ == "__main__":

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    obj = AddressObjects(1)
    addresses = obj.records

    print obj.is_dirty
    addresses[0].setValue('addr1', "The Gables")
    print obj.is_dirty
    print obj.details_html()
    print obj.changes_html()

    print obj.who_else_lives_here(1)

    #obj.add_address_link(2)
