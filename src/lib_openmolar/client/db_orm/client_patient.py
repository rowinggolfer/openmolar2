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
This module provides the PatientDB Class
(for client interaction with records in the patients table)
'''

from PyQt4 import QtCore, QtSql

from lib_openmolar.common.common_db_orm.editable_field import EditableField

from lib_openmolar.common import common_db_orm

TABLENAME = "patients"

class PatientNotFoundError(Exception):
    pass

class DuckPatient(object):
    '''
    a duck type of the Patient Record
    '''
    def __init__(self):
        #:
        self.patient_id = None

        #:
        self.title = ""

        #:
        self.last_name = ""

        #:
        self.first_name = ""

        #:
        self.preferred_name = ""

        #:
        self.correspondence_name = ""

        #:
        self.sex = "M"

        #:
        self.dob = QtCore.QDate(1900,1,1)

        #:
        self.status = "Active"

        #:
        self.modified_by = ""

        #:
        self.time_stamp = None

    @property
    def full_name(self):
        '''
        returns the :attr:`correspondence_name` (if it exists)
        or "%s %s %s"% (title, fname, sname)
        
        .. note::
        
            appends the :attr:`preferred_name` (if it exists)

        '''
        if self.correspondence_name != "":
            return self.correspondence_name
        fn = u'%s %s %s'% (self.title, self.first_name, self.last_name)
        if self.preferred_name:
            fn = u'%s "%s"'% (fn, self.preferred_name)
        return fn

    def __repr__(self):
        return u"patient - %s"% self.full_name

class PatientDB(QtSql.QSqlRecord):
    def __init__(self, patient_id):

        #:
        self.patient_id = patient_id

        query = 'SELECT * from %s WHERE ix = ?'% TABLENAME
        q_query = QtSql.QSqlQuery(SETTINGS.database)
        q_query.prepare(query)
        q_query.addBindValue(patient_id)
        q_query.exec_()
        if not q_query.next():
            raise PatientNotFoundError
        else:
            record = q_query.record()
            QtSql.QSqlQuery.__init__(self, record)

            ## make a copy (a marker of database state)
            self.orig = QtSql.QSqlRecord()
            QtSql.QSqlQuery.__init__(self.orig, record)

    @property
    def is_dirty(self):
        return self != self.orig

    def commit_changes(self):
        if not self.is_dirty:
            return
        changes, values = "", []
        for i in range(self.count()):
            if self.field(i) != self.orig.field(i):
                changes += "%s = ?,"% self.field(i).name()
                values.append(self.field(i).value())

        changes = changes.rstrip(",")
        query = "UPDATE %s set %s WHERE ix=?"% (TABLENAME, changes)
        q_query = QtSql.QSqlQuery(SETTINGS.database)
        q_query.prepare(query)
        for value in values+[self.patient_id]:
            q_query.addBindValue(value)
        q_query.exec_()
        if not q_query.lastError().isValid():
            return True
        else:
            print q_query.lastError().text()
            SETTINGS.database.emit_caught_error(q_query.lastError())

    @property
    def full_name(self):
        correspondence_name = self.value('correspondence_name').toString()
        if correspondence_name != "":
            return correspondence_name
        fn =  u"%s %s %s"% (self.value('title').toString(),
                            self.value('first_name').toString(),
                            self.value('last_name').toString())
        preferred = self.value('preferred_name').toString()
        if preferred != "":
           fn = u'%s<br />"%s"'% (fn, preferred)
        return fn.title()

    def details_html(self):
        html =  u'''<div><a href="edit_pt">%s</a>Patient %d<br /><b>%s</b><br />
        %s %s</div>'''% (SETTINGS.PENCIL,
        self.value('ix').toInt()[0], self.full_name,
        self.value('dob').toDate().toString(SETTINGS.QDATE_FORMAT),
        self._display_age)

        status = unicode(self.value('status').toString())
        if status != "active":
            html += u"<h3>%s</h3>"% (
                SETTINGS.OM_TYPES['pt_status'].readable_dict.get(status, "????"))
        return html

    def age_tuple(self):
        '''
        return the age in form (year(int), months(int), isToday(bool))
        '''
        dob = self.value('dob').toDate()
        try:
            today = QtCore.QDate.currentDate()
            nextbirthday = QtCore.QDate(today.year(), dob.month(),dob.day())

            age_years = today.year() - dob.year()

            if nextbirthday > today:
                age_years -= 1
                months = (12 - dob.month()) + today.month()
            else:
                months = today.month() - dob.month()
            if dob.day() > today.day():
                months -= 1

            isToday =  nextbirthday == today

            return (age_years, months, isToday)

        except Exception, e:
            print "error calculating patient's age", e
            return (0,0,False)

    @property
    def _display_age(self):
        '''
        display the patient's age in human readable form
        '''
        years, months, is_today = self.age_tuple()
        if is_today:
            return "<h5>%s TODAY!</h5>"% years
        if years > 18:
            return "(%syo)"% years
        else:
            retarg = "<br />%s years"% years
            if years == 1:
                retarg = retarg.strip("s")
            retarg += " %s months"% months
            if months == 1:
                retarg = retarg.strip("s")
            return retarg

    @property
    def editable_fields(self):
        '''
        a property called by dialogs which edit this class
        hence the order is important!
        a list of tuples.
        item0 in the tuple is the field name used by the db
        item) is the string displayed to the user.
        '''

        sex_field = EditableField('sex', _('Sex'), True)
        sex_field.set_type(SETTINGS.OM_TYPES['sex'])

        status_field = EditableField('status', _('Status'), True)
        status_field.set_type(SETTINGS.OM_TYPES['pt_status'])
        status_field.set_advanced(True)

        preferred_field = EditableField(
            'preferred_name', u"<i>%s</i>"% _("Preferred Name"))
        preferred_field.set_advanced(True)

        qualifications_field = EditableField(
            'qualifications', u"<i>%s</i>"% _("Qualifications"))
        qualifications_field.set_advanced(True)

        return [
        EditableField('title', _("Title"), required=True),
        EditableField('first_name', _("First Name"), True),
        EditableField('last_name', _("Surname"), True),
        preferred_field,
        qualifications_field,
        EditableField('dob', _('Date of Birth'), True),
        sex_field,
        status_field
        ]

class NewPatientDB(PatientDB, common_db_orm.InsertableRecord):
    def __init__(self):
        common_db_orm.InsertableRecord.__init__(self, SETTINGS.database,
            TABLENAME)
        self.patient_id = None
        self.orig = None


if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    object = PatientDB(1)

    print object.details_html()
    for i in range(object.count()):
        field = object.field(i)
        print u"%s:%s"% (field.name(), field.value().toString())


    print object.full_name
    print "dirty object?", object.is_dirty
    object.setValue('title', 'Ms')
    print "dirty object?", object.is_dirty
