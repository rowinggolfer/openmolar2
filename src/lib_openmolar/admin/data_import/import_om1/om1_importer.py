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

import re
import sys
from PyQt4 import QtSql, QtCore
from lib_openmolar.admin.data_import.importer import Importer
from lib_openmolar.admin.data_import.import_om1 import convert_notes
from lib_openmolar.admin.data_import.import_om1 import teeth_present
from lib_openmolar.admin.data_import.import_om1 import convert_perio
from lib_openmolar.admin.data_import.import_om1 import convert_daybook
from lib_openmolar.admin.data_import.import_om1 import convert_daybook_chart
from lib_openmolar.admin.data_import.import_om1 import convert_daybook_ndu
from lib_openmolar.admin.data_import.import_om1 import convert_daybook_ndl
from lib_openmolar.admin.data_import.import_om1 import convert_daybook_odu
from lib_openmolar.admin.data_import.import_om1 import convert_daybook_odl
from lib_openmolar.admin.data_import.import_om1 import convert_static

from lib_openmolar.common import SETTINGS


class OM1Importer(Importer):
    '''
    inherit and overwrite functions from the base Importer class
    '''
    def __init__(self, connection, om2_connection):
        Importer.__init__(self, om2_connection)
        self.connection = connection

    def OLDimport_practitioners(self):
        print "importing practitioners"

        ps_query = '''insert into practitioners
        (ix, title, last_name, first_name, abbrv_name, full_name,
        sex, dob, status, qualifications, registration, avatar_id,
        comments, type, modified_by)
        values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        psql_query = QtSql.QSqlQuery(self.om2_connection)

        query = '''select id, inits, name, apptix, formalname, fpcno, quals,
        flag0, flag3 from practitioners where id>0'''
        mysql_query = QtSql.QSqlQuery(self.connection)
        mysql_query.prepare(query)
        mysql_query.exec_()

        while mysql_query.next():

            if mysql_query.value(8).toBool():
                status="active"
            else:
                status="inactive"

            if mysql_query.value(7).toInt()[0]==1:
                p_type="dentist"
            else:
                p_type="hygienest"

            psql_query.prepare(ps_query)
            psql_query.addBindValue(mysql_query.value(0)) #id
            psql_query.addBindValue("MR") #title
            psql_query.addBindValue(mysql_query.value(2)) #last_name
            psql_query.addBindValue(mysql_query.value(2)) #first_name
            psql_query.addBindValue(mysql_query.value(1)) #abbrv_name
            psql_query.addBindValue(mysql_query.value(4)) #full_name
            psql_query.addBindValue("M") #sex
            psql_query.addBindValue(QtCore.QDate(1900,1,1)) #dob
            psql_query.addBindValue(status) #status
            psql_query.addBindValue(mysql_query.value(6)) #qualifications
            psql_query.addBindValue("") #registration
            psql_query.addBindValue(0) #avatar_id
            psql_query.addBindValue('imported from mysql') #modified_by
            psql_query.addBindValue(p_type) #practitioner_type
            psql_query.addBindValue('') #comments

            psql_query.exec_()
            if psql_query.lastError().isValid():
                print "ERROR IMPORTING %s - %s"% (
                    mysql_query.value(0).toInt()[0],
                    psql_query.lastError().text())

        print "WARNING - practiitioner sex, dob and names will require attention"


    def import_patients(self, sno_limit=None):
        print "importing patients"

        ps_query = '''insert into patients
        (ix, title, last_name, first_name, sex, dob,
        status, modified_by)
        values (?,?,?,?,?,?,?,?)'''
        psql_query = QtSql.QSqlQuery(self.om2_connection)

        query = '''select serialno, title, sname, fname, sex, dob,
        status from patients'''

        if sno_limit is not None:
            print "limited to serialno", sno_limit
            query +=" where serialno <= %d"% sno_limit
        mysql_query = QtSql.QSqlQuery(self.connection)
        mysql_query.prepare(query)
        mysql_query.exec_()

        while mysql_query.next():
            psql_query.prepare(ps_query)
            psql_query.addBindValue(mysql_query.value(0))
            psql_query.addBindValue(mysql_query.value(1))
            psql_query.addBindValue(mysql_query.value(2))
            psql_query.addBindValue(mysql_query.value(3))
            psql_query.addBindValue(mysql_query.value(4))
            psql_query.addBindValue(mysql_query.value(5))
            status = mysql_query.value(6).toString()
            #| DECEASED      |
            #| BAD DEBT      |
            #| NO MORE APPTS |
            #| MOVED AWAY    |
            #| ACTIVE

            if status == "":
                status = "active"
            elif status == "BAD DEBT":
                status = "bad_debt"
            elif status == "NO MORE APPTS":
                status = "banned"
            else:
                status = status.toLower() #QString
            psql_query.addBindValue(status)
            psql_query.addBindValue('imported from mysql')

            psql_query.exec_()
            if psql_query.lastError().isValid():
                print "ERROR IMPORTING %s - %s"% (
                    mysql_query.value(0).toInt()[0],
                    psql_query.lastError().text())

    def import_static_charts(self, sno_limit=None):
        print "importing static_charts"

        psql_query = QtSql.QSqlQuery(self.om2_connection)
        mysql_query = QtSql.QSqlQuery(self.connection)

        convert_static.convert(mysql_query, psql_query, sno_limit)

    def import_clerical_memos(self, max_sno=None):
        print "importing clerical memos"

        ps_query = '''INSERT INTO clerical_memos
        (patient_id, memo, checked_by)
        VALUES (?, ?, ?)'''

        psql_query = QtSql.QSqlQuery(self.om2_connection)

        query = '''select serialno, memo from patients'''
        if max_sno:
            query += " where serialno <= %d"% max_sno

        mysql_query = QtSql.QSqlQuery(self.connection)
        mysql_query.prepare(query)
        mysql_query.exec_()

        while mysql_query.next():
            memo = mysql_query.value(1).toString()
            if memo == "":
                continue

            for garbage in ("\\", "JJ_TR", "X-ECM", "SDPB LIST",
            "ECM-BW TRANSFER"):
                memo = memo.replace(garbage,"")
            memo = memo.trimmed()

            if memo == "":
                continue

            psql_query.prepare(ps_query)
            psql_query.addBindValue(mysql_query.value(0))
            psql_query.addBindValue(memo)
            psql_query.addBindValue("imported from mysql")

            psql_query.exec_()
            if psql_query.lastError().isValid():
                print "ERROR IMPORTING %s - %s"% (
                    mysql_query.value(0).toInt()[0],
                    psql_query.lastError().text())

    def import_addresses(self, max_sno=None):
        print "importing addresses"

        ps_query = '''INSERT INTO addresses
        (addr1, addr2, addr3, city, county, country, postal_cd, modified_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?) returning ix'''

        psql_query = QtSql.QSqlQuery(self.om2_connection)

        ps_query2 = '''INSERT INTO address_link
        (address_cat, patient_id, address_id, comments)
        VALUES (?, ?, ?, ?)'''

        psql_query2 = QtSql.QSqlQuery(self.om2_connection)

        query = '''select addr1, addr2, addr3, town, county, pcde,
        serialno from patients order by addr1, addr2, addr3, pcde'''
        if max_sno:
            query += " where serialno<=%d"% max_sno
        mysql_query = QtSql.QSqlQuery(self.connection)
        mysql_query.prepare(query)
        mysql_query.exec_()

        previous = (None, None, None, None)
        address_id = None
        while mysql_query.next():

            if (mysql_query.value(0).toString(),
            mysql_query.value(1).toString(),
            mysql_query.value(2).toString(),
            mysql_query.value(3).toString()) != previous:
                previous = (
                    mysql_query.value(0).toString(),
                    mysql_query.value(1).toString(),
                    mysql_query.value(2).toString(),
                    mysql_query.value(3).toString())

                psql_query.prepare(ps_query)
                psql_query.addBindValue(mysql_query.value(0))
                psql_query.addBindValue(mysql_query.value(1))
                psql_query.addBindValue(mysql_query.value(2))
                city = "%s"% mysql_query.value(3).toString()
                psql_query.addBindValue(city)
                psql_query.addBindValue(mysql_query.value(4))
                psql_query.addBindValue(None)
                psql_query.addBindValue(mysql_query.value(5))
                psql_query.addBindValue("imported from mysql")

                psql_query.exec_()
                if psql_query.lastError().isValid():
                    print "ERROR IMPORTING %s - %s"% (
                        mysql_query.value(0).toInt()[0],
                        psql_query.lastError().text())

                psql_query.first()
                address_id = psql_query.value(0).toInt()[0]

            psql_query2.prepare(ps_query2)
            psql_query2.addBindValue("home")
            psql_query2.addBindValue(mysql_query.value(6))
            psql_query2.addBindValue(address_id)
            psql_query2.addBindValue("imported from mysql")

            psql_query2.exec_()
            if psql_query2.lastError().isValid():
                print "ERROR IMPORTING %s - %s"% (
                    mysql_query.value(0).toInt()[0],
                    psql_query2.lastError().text())


    def import_clinical_memos(self, max_sno=None):
        print "importing clinical memos"

        ps_query = '''INSERT INTO clinical_memos
        (patient_id, memo, checked_date, checked_by)
        VALUES (?, ?, ?, ?)'''

        psql_query = QtSql.QSqlQuery(self.om2_connection)

        query = '''select serialno, synopsis, datestamp, author
        from clinical_memos order by serialno, ix desc'''
        if max_sno:
            query += " where serialno<=%d"% max_sno

        mysql_query = QtSql.QSqlQuery(self.connection)
        mysql_query.prepare(query)
        mysql_query.exec_()

        previous_id = None
        while mysql_query.next():
            memo = mysql_query.value(1).toString()
            pt_id = mysql_query.value(0)

            if memo == "" or pt_id == previous_id:
                continue

            psql_query.prepare(ps_query)

            psql_query.addBindValue(pt_id)
            psql_query.addBindValue(memo)
            psql_query.addBindValue(mysql_query.value(2))
            psql_query.addBindValue(mysql_query.value(3))

            psql_query.exec_()
            if psql_query.lastError().isValid():
                print "ERROR IMPORTING %s - %s"% (
                    mysql_query.value(0).toInt()[0],
                    psql_query.lastError().text())

            previous_id = pt_id

    def import_appointments(self, max_sno=None):
        print "importing appointments from aslot"

        ps_query = '''insert into diary_appointments
        (diary_id, start, finish, type, comments)
        values (?,?,?,?,?) returning ix'''
        psql_query = QtSql.QSqlQuery(self.om2_connection)

        ps_query2 = '''insert into diary_patients
        (patient, appt_ix, clinician_spec, reason1, reason2, length, comment)
        values (?,?,?,?,?,?,?)'''
        psql_query2 = QtSql.QSqlQuery(self.om2_connection)

        query = '''select apptix, adate, start, end, serialno,
        name, code0, concat(code1, ' ', code2), note from aslot
        where adate>20090101'''
        if max_sno:
            query += " and serialno <=%d "% max_sno

        mysql_query = QtSql.QSqlQuery(self.connection)
        mysql_query.prepare(query)
        mysql_query.exec_()
        while mysql_query.next():
            # convert dodgy old date/time system into standard values
            d = mysql_query.value(1).toDate()
            start = mysql_query.value(2).toInt()[0]
            start_time = QtCore.QDateTime(d.year(), d.month(), d.day(),
                int(start/100), int(start%100))
            end = mysql_query.value(3).toInt()[0]
            end_time = QtCore.QDateTime(d.year(), d.month(), d.day(),
                int(end/100), int(end%100))

            length = start_time.secsTo(end_time)//60

            psql_query.prepare(ps_query)
            psql_query.addBindValue(mysql_query.value(0)) #diary id
            psql_query.addBindValue(start_time) #start
            psql_query.addBindValue(end_time) #finish
            psql_query.addBindValue('appointment') #type
            psql_query.addBindValue('imported from mysql') #comments

            psql_query.exec_()
            if psql_query.lastError().isValid():
                print psql_query.lastError().text()

            #appointments such as lunch, emergency, staff meetings etc..
            #do not need to go into diary patients
            patient_id = mysql_query.value(4).toInt()[0]
            if patient_id == 0:
                continue

            psql_query.first()
            appointment_ix = psql_query.record().value("ix").toInt()[0]

            psql_query2.prepare(ps_query2)
            psql_query2.addBindValue(mysql_query.value(4)) #patient no
            psql_query2.addBindValue(appointment_ix)   #appointment ix
            psql_query2.addBindValue(mysql_query.value(0)) #clinician_spec
            psql_query2.addBindValue(mysql_query.value(6)) #reason1
            psql_query2.addBindValue(mysql_query.value(7)) #reason2
            psql_query2.addBindValue(length) #length
            psql_query2.addBindValue(mysql_query.value(8)) #comment

            psql_query2.exec_()
            if psql_query2.lastError().isValid():
                print "ERROR IMPORTING %s - %s"% (
                    mysql_query.value(0).toInt()[0],
                    psql_query.lastError().text())


        print "importing unmade appointments from apr"

        ps_query2 = '''insert into diary_patients
        (patient, appt_ix, clinician_spec, reason1, reason2, length, comment)
        values (?,?,?,?,?,?,?)'''
        psql_query2 = QtSql.QSqlQuery(self.om2_connection)

        query = '''select serialno, practix, code0, concat(code1, ' ', code2),
        note, length from apr where adate IS NULL order by serialno, aprix'''

        if max_sno:
            query = query.replace("IS NULL",
            "IS NULL and serialno <=%d "% max_sno)

        mysql_query = QtSql.QSqlQuery(self.connection)
        mysql_query.prepare(query)
        mysql_query.exec_()
        while mysql_query.next():
            length = mysql_query.value(5).toInt()[0]

            psql_query2.prepare(ps_query2)
            psql_query2.addBindValue(mysql_query.value(0)) #patient no
            psql_query2.addBindValue(None)   #appointment ix
            psql_query2.addBindValue(mysql_query.value(1)) #clinician_spec
            psql_query2.addBindValue(mysql_query.value(2)) #reason1
            psql_query2.addBindValue(mysql_query.value(3)) #reason2
            psql_query2.addBindValue(length) #length
            psql_query2.addBindValue(mysql_query.value(4)) #comment

            psql_query2.exec_()
            if psql_query2.lastError().isValid():
                print "ERROR IMPORTING %s - %s"% (
                    mysql_query.value(0).toInt()[0],
                    psql_query.lastError().text())


    def import_notes(self, sno_limit=None):
        print "importing notes (this may take time)"
        sys.stdout.flush()

        ps_query = '''INSERT INTO notes_clinical
        (patient_id, open_time, commit_time, type, line, author, co_author)
        VALUES (?, ?, ?, ?, ?, ?, ?)'''

        ps_query2 = '''INSERT INTO notes_clerical
        (patient_id, open_time, commit_time, type, line, author)
        VALUES (?, ?, ?, ?, ?, ?)'''

        psql_query = QtSql.QSqlQuery(self.om2_connection)

        query = "select max(serialno) from notes"
        mysql_query = QtSql.QSqlQuery(self.connection)
        mysql_query.prepare(query)
        mysql_query.exec_()
        mysql_query.first()
        max_sno = mysql_query.value(0).toInt()[0]

        ##TESTING FUNCTIONALITY!
        if sno_limit is not None:
            max_sno =  sno_limit

        for i in xrange(0, max_sno, 1):

            print "="*80
            print "converting notes for record %s"% i

            query = '''SELECT line from notes where serialno = %d
            order by serialno, lineno'''% i
            mysql_query = QtSql.QSqlQuery(self.connection)
            mysql_query.prepare(query)
            mysql_query.exec_()

            lines = []
            while mysql_query.next():
                line = unicode(mysql_query.value(0).toString())
                lines.append(line)

            try:
                for note in convert_notes.notes(lines):
                    clerical_note = note.is_clerical
                    if clerical_note:
                        psql_query.prepare(ps_query2)
                        if note.operator2:
                            note.operator1  = note.operator2
                    else: #clinical note
                        psql_query.prepare(ps_query)

                    psql_query.addBindValue(i)

                    psql_query.addBindValue(note.time)
                    psql_query.addBindValue(note.commit_time)

                    om_type = note.om_type
                    psql_query.addBindValue(om_type)

                    psql_query.addBindValue(note.note)

                    author = self.USER_DICT.get(note.operator1, 0)
                    psql_query.addBindValue(author)

                    if not clerical_note:
                        co_author = self.USER_DICT.get(note.operator2, None)
                        psql_query.addBindValue(co_author)

                    psql_query.exec_()
                    if psql_query.lastError().isValid():
                        print "DATABASE IMPORTING notes for serialno %d - %s"% (i,
                            psql_query.lastError().text().toUtf8())

            except AttributeError as e:
                print "Unknown ERROR  IMPORTING notes for serialno %d - %s"% (
                    i, e)
                continue


    def get_users_from_notes(self):
        print "searching notes for users (this takes some time)"

        USERS = set([])

        query = 'SELECT line from notes'
        mysql_query = QtSql.QSqlQuery(query, self.connection)
        mysql_query.exec_()

        lines = []
        while mysql_query.next():
            line = unicode(mysql_query.value(0).toString())

            for note in convert_notes.decipher_noteline(line):
                user1 = note.operator1
                user2 = note.operator2
                if user1:
                   USERS.add(user1)
                if user2:
                   USERS.add(user2)

        user_list = list(USERS)
        user_list.sort()
        return user_list

    def insert_null_user(self):
        print "inserting null user to index 0"

        ps_query = '''INSERT INTO users
        (ix, title, last_name, first_name, qualifications,
        abbrv_name, sex, dob, status, comments, modified_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        psql_query = QtSql.QSqlQuery(self.om2_connection)

        psql_query.prepare(ps_query)

        for val in ("0", "?", "?", "?", "?", "-", "M",
        QtCore.QDate(1900,1,1), "none", "",""):
            psql_query.addBindValue(val)

        psql_query.exec_()

    def OLDimport_users(self, userlist=None):
        userlist = self.get_users_from_notes()
        Importer.insert_users(self, userlist)

    def import_bpe(self, max_sno=None):
        print "importing bpe"

        ps_query = '''INSERT INTO perio_bpe
        (patient_id, checked_date, values, checked_by)
        VALUES (?, ?, ?, ?)'''

        psql_query = QtSql.QSqlQuery(self.om2_connection)

        query = '''select serialno, bpedate, bpe from bpe'''
        if max_sno:
            query += " where serialno<=%d"% max_sno

        mysql_query = QtSql.QSqlQuery(self.connection)
        mysql_query.prepare(query)
        mysql_query.exec_()

        while mysql_query.next():
            psql_query.prepare(ps_query)
            psql_query.addBindValue(mysql_query.value(0))
            psql_query.addBindValue(mysql_query.value(1))
            #hammer out some inconsistencies over several iterations of wysdom
            bpe = str(mysql_query.value(2).toString()).ljust(6,"-")
            bpe = bpe.replace(" ","-")
            bpe = bpe.replace("_","-")
            bpe = bpe.replace("X","-")
            psql_query.addBindValue(bpe)
            psql_query.addBindValue("imported")

            psql_query.exec_()
            if psql_query.lastError().isValid():
                print "ERROR IMPORTING %s %s '%s' - %s"% (
                    mysql_query.value(0).toInt()[0],
                    mysql_query.value(1).toString(),
                    mysql_query.value(2).toString(),
                    psql_query.lastError().text())

    def import_perio(self, max_sno=None):
        print "importing perio"

        ps_query = '''INSERT INTO perio_pocketing
        (patient_id, tooth, checked_date, values, checked_by)
        VALUES (?, ?, ?, ?, ?)'''

        psql_query = QtSql.QSqlQuery(self.om2_connection)

        query = '''select serialno, chartdate, chartdata, flag
        from perio order by chartdate'''
        if max_sno:
            query += " where serialno<=%d"% max_sno

        mysql_query = QtSql.QSqlQuery(query, self.connection)

        hex_depths = (0,1,2,3,4,5,6,7,8,9,'A','B','C','D','E','F')

        while mysql_query.next():
            data = convert_perio.get_perioData(
                        mysql_query.value(2).toByteArray())
            #print "%s %s %s %s"% (
            #        mysql_query.value(0).toInt()[0],
            #        mysql_query.value(1).toString(),
            #        data,
            #        mysql_query.value(3).toString())

            for key in data.pocketing.keys():
                value = ""
                pocket_depths = data.pocketing[key]
                for pocket_depth in pocket_depths:
                    if pocket_depth == 127:
                        value += " "
                    else:
                        try:
                            value += "%s"% hex_depths[pocket_depth]
                        except IndexError:
                            print "POCKET DEPTH OUT OF RANGE", pocket_depth
                if value == "      ":
                    continue
                psql_query.prepare(ps_query)
                psql_query.addBindValue(mysql_query.value(0))
                psql_query.addBindValue(key)
                psql_query.addBindValue(mysql_query.value(1))
                psql_query.addBindValue(value)
                psql_query.addBindValue("imported")

                psql_query.exec_()
                if psql_query.lastError().isValid():
                    print "ERROR IMPORTING %s tooth %s"% (
                        mysql_query.value(0).toInt()[0], key),
                    print psql_query.lastError().text()

    def import_contracted_practitioners(self, max_sno=None):
        print "importing contracted practitioners"

        ps_query = '''INSERT INTO contracted_practitioners
        (patient_id, practitioner_id, contract_type, comments)
        VALUES (?, ?, ?, ?)'''

        psql_query = QtSql.QSqlQuery(self.om2_connection)

        query = '''select serialno, dnt1 from patients'''
        if max_sno:
            query += " where serialno<=%d"% max_sno

        mysql_query = QtSql.QSqlQuery(self.connection)
        mysql_query.prepare(query)
        mysql_query.exec_()

        while mysql_query.next():
            dnt1, result = mysql_query.value(1).toInt()
            if not (dnt1 and result):
                continue
            psql_query.prepare(ps_query)
            psql_query.addBindValue(mysql_query.value(0))
            psql_query.addBindValue(mysql_query.value(1))
            psql_query.addBindValue("dentist")
            psql_query.addBindValue("imported")

            psql_query.exec_()
            if psql_query.lastError().isValid():
                print "ERROR IMPORTING contracted_practitioner for %s - %s"% (
                    mysql_query.value(0).toInt()[0],
                    psql_query.lastError().text())

    def import_telephones(self, max_sno=None):
        print "importing telephones"

        ps_query = '''INSERT INTO telephone
        (number, sms_capable) VALUES (?, ?) returning ix'''

        psql_query = QtSql.QSqlQuery(self.om2_connection)

        ps_query2 = '''INSERT INTO telephone_link
        (tel_cat, patient_id, tel_id, comment)
        VALUES (?, ?, ?, ?)'''

        psql_query2 = QtSql.QSqlQuery(self.om2_connection)

        i = 0
        for field in "tel1", "tel2", "mobile":

            new_type = ("home", "work", "mobile")[i]
            i += 1

            query = '''select serialno, %s from patients
            where %s IS NOT NULL and %s != "" order by %s'''% (
            field, field, field, field)

            if max_sno:
                query = query.replace('""', '"" and serialno<=%d'% max_sno)


            mysql_query = QtSql.QSqlQuery(query, self.connection)

            previous = None
            ix = None
            while mysql_query.next():
                val = mysql_query.value(1).toString()
                if val != previous:

                    psql_query.prepare(ps_query)
                    if re.match("[\d+ \+]", val):
                        psql_query.addBindValue(val)
                        comment = "imported from mysql field %s"% field
                    else:
                        psql_query.addBindValue("00000 0000000")
                        comment = val
                    psql_query.addBindValue(field == "mobile")

                    psql_query.exec_()
                    if psql_query.lastError().isValid():
                        print "ERROR IMPORTING %s - %s"% (
                            mysql_query.value(0).toInt()[0],
                            psql_query.lastError().text())

                        ## if there is an error.. don't try and link
                        continue

                    psql_query.first()
                    ix = psql_query.value(0).toInt()[0]
                    previous = val

                psql_query2.prepare(ps_query2)
                psql_query2.addBindValue(new_type)
                psql_query2.addBindValue(mysql_query.value(0))
                psql_query2.addBindValue(ix)
                psql_query2.addBindValue(comment)

                psql_query2.exec_()
                if psql_query2.lastError().isValid():
                    print "ERROR IMPORTING %s - %s"% (
                        mysql_query.value(0).toInt()[0],
                        psql_query2.lastError().text())

    def import_tx_completed(self, max_sno=None):
        print "inserting tx_completed"
        sys.stdout.flush()
        ps_query = '''INSERT INTO treatments
        (patient_id, om_code, completed, px_clinician, px_date,
        tx_clinician, tx_date, comment) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        returning ix'''

        ps_query_tooth = '''INSERT INTO treatment_teeth
        (treatment_id, tooth, tx_type) VALUES (?, ?, ?) returning ix'''

        ps_query_fill = '''INSERT INTO treatment_fills
        (tooth_tx_id, surfaces, material) VALUES (?, ?, ?)'''

        psql_query = QtSql.QSqlQuery(self.om2_connection)

        for column, function in (
        ("diagn", convert_daybook.convert_diagn),
        ("chart", convert_daybook_chart.convert),
        ("perio", convert_daybook.convert_perio),
        ("anaes", convert_daybook.convert_anaes),
        ("misc", convert_daybook.convert_misc),
        ("other", convert_daybook.convert_other),
        ("ndu", convert_daybook_ndu.convert),
        ("ndl", convert_daybook_ndl.convert),
        ("odu", convert_daybook_odu.convert),
        ("odl", convert_daybook_odl.convert),
        ):
            print "=" * 80
            print "importing column", column, "from daybook"
            print "=" * 80

            if max_sno is None:
                query = '''select serialno, date, %s, dntid, trtid, id
                from daybook'''% column
            else:
                ##ordering only for debugging.
                query = '''select serialno, date, %s, dntid, trtid, id
                from daybook where serialno <= %d
                order by serialno, id'''% (column, max_sno)
            mysql_query = QtSql.QSqlQuery(self.connection)
            mysql_query.prepare(query)
            mysql_query.exec_()

            previous_serialno = None
            while mysql_query.next():
                serialno = mysql_query.value(0).toInt()[0]
                if max_sno != None and serialno != previous_serialno:
                    print "========== importing pt %6d ========="% serialno
                    previous_serialno = serialno
                value = str(mysql_query.value(2).toString())
                for om_code in function(value):

                    psql_query.prepare(ps_query)
                    psql_query.addBindValue(mysql_query.value(0)) #sno
                    psql_query.addBindValue(om_code.code)
                    psql_query.addBindValue(True)
                    psql_query.addBindValue(mysql_query.value(3)) #px_clinician
                    psql_query.addBindValue(mysql_query.value(1)) #date
                    psql_query.addBindValue(mysql_query.value(4)) #tx_clinician
                    psql_query.addBindValue(mysql_query.value(1)) #date
                    psql_query.addBindValue("ORIG (%s): %s"% (column, value))

                    psql_query.exec_()
                    if psql_query.lastError().isValid():
                        print "ERROR IMPORTING Daybook id %s - %s"% (
                            mysql_query.value(5).toInt()[0],
                            psql_query.lastError().text())
                        continue

                    psql_query.first()
                    treatment_id = psql_query.value(0)

                    if om_code.tooth is not None:
                        psql_query.prepare(ps_query_tooth)
                        psql_query.addBindValue(treatment_id)
                        psql_query.addBindValue(om_code.tooth)
                        psql_query.addBindValue(om_code.tooth_tx_type)
                        psql_query.exec_()
                        psql_query.first()
                        tooth_tx_id = psql_query.value(0)
                        if psql_query.lastError().isValid():
                                print ("ERROR IMPORTING Daybook into"
                                " treatment_teeth table id %s - %s"% (
                                mysql_query.value(5).toInt()[0],
                                psql_query.lastError().text()))
                                print psql_query.executedQuery()

                        if om_code.is_fill:
                            psql_query.prepare(ps_query_fill)
                            psql_query.addBindValue(tooth_tx_id)
                            psql_query.addBindValue(om_code.surfaces)
                            psql_query.addBindValue(om_code.material)
                            psql_query.exec_()
                            if psql_query.lastError().isValid():
                                print ("ERROR IMPORTING Daybook into"
                                " treatment_fills table id %s - %s"% (
                                mysql_query.value(5).toInt()[0],
                                psql_query.lastError().text()))
                                print psql_query.executedQuery()

                    for pontic in om_code.pontics:
                        psql_query.prepare(ps_query_tooth)
                        psql_query.addBindValue(treatment_id)
                        psql_query.addBindValue(pontic.tooth)
                        psql_query.addBindValue("pontic")
                        psql_query.exec_()
                        #psql_query.first()
                        #tooth_tx_id = psql_query.value(0)
                        if psql_query.lastError().isValid():
                                print ("ERROR IMPORTING Daybook into"
                                " treatment_teeth table id %s - %s"% (
                                mysql_query.value(5).toInt()[0],
                                psql_query.lastError().text()))
                                print psql_query.executedQuery()


        ## temporary code!
        convert_daybook_chart.rogue_output()

    def import_all(self):
        '''
        don't overwrite this normally... for testing one function only
        '''
        if True:
            Importer.import_all(self)
            return

        ##for testing
        print "=" * 80
        print "WARNING - using custom import_all"
        print "=" * 80
        sys.stdout.flush()
        max_sno = 1000

        #self.import_avatars()

        if False:
            self.import_users()
        else:
            print "WARNING - trusting XML for user dict!"
            #self.import_users(ignore_errors=True)

        #self.insert_null_user()
        #self.import_practitioners()
        #self.import_patients(max_sno)
        #self.import_tx_completed(max_sno)

        #self.import_notes(max_sno)

        #self.import_appointments(max_sno)
        #self.import_clerical_memos(max_sno)
        #self.import_clinical_memos(max_sno)
        #self.import_addresses(max_sno)

        self.import_static_charts(max_sno)
        self.import_bpe(max_sno)
        self.import_perio(max_sno)
        self.import_contracted_practitioners(max_sno)
        self.import_telephones(max_sno)

    print "ALL DONE!"

if __name__ == "__main__":
    pass
