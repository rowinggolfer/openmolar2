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

import os
from xml.dom import minidom
from PyQt4 import QtSql, QtCore
from lib_openmolar.common import common_db_orm


class Importer(object):
    '''
    this object imports data from xml files and puts them into the database
    the data integrity is ensure by the db schema.. so watch output for
    errors.
    Inherit from this class and overwrite if importing from a different source
    for some tables (eg.. I have a subclass which imports data from an
    existing openmolar 1 database
    '''
    def __init__(self, om2_connection):
        self.om2_connection = om2_connection
        self._import_directory = os.path.curdir
        self.USER_DICT = {}

    @property
    def import_directory(self):
        '''
        returns the file path where XML data files can be found
        '''
        assert os.path.isdir(self._import_directory)
        return self._import_directory

    def set_import_directory(self, directory):
        '''
        set the file path to the directory where XML data can be found
        '''
        assert os.path.isdir(directory)
        self._import_directory = directory

    def import_practitioners(self):
        TABLENAME = "practitioners"
        print "importing %s"% TABLENAME

        dom = minidom.parse(os.path.join(self.import_directory,
            "%s.xml"% TABLENAME))

        record = common_db_orm.InsertableRecord(self.om2_connection, TABLENAME)
        record.include_ix = True

        record.remove(record.indexOf("time_stamp"))
        ps_query, values = record.insert_query
        psql_query = QtSql.QSqlQuery(self.om2_connection)

        rows = dom.getElementsByTagName(TABLENAME.rstrip("s"))

        for row in rows:
            psql_query.prepare(ps_query)
            for node in ("ix", "user_id", "type", "speciality",
             "status", "comments", ):
                vals = row.getElementsByTagName(node)
                try:
                    val = vals[0].firstChild.data.strip()
                except IndexError:
                    val = None
                except AttributeError:
                    val = ""
                psql_query.addBindValue(val)

            psql_query.addBindValue("imported from xml")
            psql_query.exec_()
            if psql_query.lastError().isValid():
                print "ERRROR IMPORTING %s - %s"% (
                    row.toxml(),
                    psql_query.lastError().text())

    def import_avatars(self):
        TABLENAME = "avatars"
        print "importing %s"% TABLENAME

        dom = minidom.parse(os.path.join(self.import_directory,
            "%s.xml"% TABLENAME))

        record = common_db_orm.InsertableRecord(self.om2_connection, TABLENAME)

        ps_query, values = record.insert_query
        psql_query = QtSql.QSqlQuery(self.om2_connection)

        rows = dom.getElementsByTagName(TABLENAME.rstrip("s"))

        for row in rows:
            psql_query.prepare(ps_query)
            for node in ("description", "svg_data"):
                vals = row.getElementsByTagName(node)
                try:
                    val = vals[0].firstChild.data.strip()
                except IndexError:
                    val = None
                except AttributeError:
                    val = ""
                psql_query.addBindValue(val)

            psql_query.exec_()
            if psql_query.lastError().isValid():
                print "ERRROR IMPORTING - %s"% psql_query.lastError().text()


    def import_patients(self):
        print "importing patients"

    def import_static_charts(self):
        print "importing static_charts"

    def import_clerical_memos(self):
        print "importing clerical memos"

    def import_addresses(self):
        print "importing addresses"

    def import_clinical_memos(self):
        print "importing clinical memos"

    def import_appointments(self):
        print "importing appointments from aslot"

    def import_notes(self):
        print "importing notes"

    def insert_null_user(self):
        print "inserting null user to index 0"

        ps_query = '''INSERT INTO users
        (ix, title, last_name, first_name, qualifications,
        abbrv_name, sex, dob, status, comments, modified_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        psql_query = QtSql.QSqlQuery(self.om2_connection)

        psql_query.prepare(ps_query)

        for val in (0, "?", "?", "?", "?", "-", "M",
        QtCore.QDate(1900,1,1), "none", "",""):
            psql_query.addBindValue(val)

        psql_query.exec_()

    def import_users(self):
        TABLENAME = "users"
        print "importing %s"% TABLENAME

        dom = minidom.parse(os.path.join(self.import_directory,
            "%s.xml"% TABLENAME))

        record = common_db_orm.InsertableRecord(self.om2_connection, TABLENAME)
        record.include_ix = True
        record.remove(record.indexOf("time_stamp"))
        ps_query, values = record.insert_query
        psql_query = QtSql.QSqlQuery(self.om2_connection)

        rows = dom.getElementsByTagName(TABLENAME.rstrip("s"))

        ps_query += " returning ix"
        for row in rows:
            psql_query.prepare(ps_query)
            for node in ('ix', 'abbrv_name', 'role', 'title', 'last_name',
            'middle_name', 'first_name', 'qualifications', 'registration',
            'correspondence_name', 'sex', 'dob', 'dbuser',
            'status', 'comments', 'avatar_id', 'display_order'):
                vals = row.getElementsByTagName(node)
                try:
                    val = vals[0].firstChild.data.strip()
                    if node == "abbrv_name":
                        user = val
                except IndexError:
                    val = None
                except AttributeError:
                    val = ""
                psql_query.addBindValue(val)

            psql_query.addBindValue("imported from xml")
            psql_query.exec_()
            if psql_query.lastError().isValid():
                print "ERRROR IMPORTING %s - %s"% (
                    row.toxml(),
                    psql_query.lastError().text())
            else:
                psql_query.first()
                self.USER_DICT[user] = psql_query.value(0).toInt()[0]
        print self.USER_DICT

    def import_bpe(self):
        print "importing bpe"

    def import_contracted_practitioners(self):
        print "importing contracted practitioners"

    def import_telephones(self):
        print "importing telephones"

    def import_tx_completed(self):
        print "importing tx_completed"


    def import_all(self):
        self.insert_null_user()
        self.import_avatars()
        self.import_users()
        self.import_practitioners()
        self.import_patients()

        self.import_tx_completed()
        self.import_appointments()
        self.import_clerical_memos()
        self.import_clinical_memos()
        self.import_addresses()

        self.import_notes()

        self.import_static_charts()
        self.import_bpe()
        self.import_perio()
        self.import_contracted_practitioners()
        self.import_telephones()
        print "ALL DONE!"

if __name__ == "__main__":
    from lib_openmolar.admin.connect import AdminConnection
    sc = AdminConnection()
    sc.connect()

    im = Importer(sc)
    im.set_import_directory("/home/neil/Desktop/adp_import")
    im.import_all()