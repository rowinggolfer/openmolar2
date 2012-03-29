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
import sys
import traceback
from xml.dom import minidom
from PyQt4 import QtSql, QtCore
from lib_openmolar.common.db_orm import InsertableRecord

class _ImportWarning(Exception):
    pass

class Importer(object):
    '''
    this object imports data from xml files and puts them into the database
    the data integrity is ensure by the db schema.. so watch output for
    errors.
    Inherit from this class and overwrite if importing from a different source
    for some tables (eg.. I have a subclass which imports data from an
    existing openmolar 1 database
    '''

    sno_range = None
    sno_conditions = ""

    def __init__(self):
        self.om2_session = None
        self._import_directory = os.path.curdir
        self.USER_DICT = {}

    def set_session(self, om2_session):
        self.om2_session = om2_session

    @property
    def import_directory(self):
        '''
        returns the file path where XML data files can be found
        '''
        return self._import_directory

    def set_import_directory(self, directory):
        '''
        set the file path to the directory where XML data can be found
        '''
        assert os.path.isdir(directory), "%s is not a directory"% directory
        self._import_directory = directory

    def import_practitioners(self):
        table_name = "practitioners"
        LOGGER.info("importing %s"% table_name)

        try:
            filepath = os.path.abspath(
                os.path.join(self.import_directory, "%s.xml"% table_name))
            dom = minidom.parse(filepath)
        except IOError as exc:
            LOGGER.error(
            "Unable to import practitioners - no such file %s"% filepath)
            raise _ImportWarning

        record = InsertableRecord(self.om2_session, table_name)
        record.include_ix = True

        record.remove(record.indexOf("time_stamp"))
        ps_query, values = record.insert_query
        psql_query = QtSql.QSqlQuery(self.om2_session)

        rows = dom.getElementsByTagName(table_name.rstrip("s"))

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
                LOGGER.warning("ERROR IMPORTING %s - %s"% (
                    row.toxml(),
                    psql_query.lastError().text()))

    def import_avatars(self):
        table_name = "avatars"
        LOGGER.info("importing %s"% table_name)

        try:
            filepath = os.path.abspath(
                os.path.join(self.import_directory, "%s.xml"% table_name))
            dom = minidom.parse(filepath)
        except IOError:
            LOGGER.error(
            "Unable to import avatars - no such file %s"% filepath)
            raise _ImportWarning

        record = InsertableRecord(self.om2_session, table_name)

        ps_query, values = record.insert_query
        psql_query = QtSql.QSqlQuery(self.om2_session)

        rows = dom.getElementsByTagName(table_name.rstrip("s"))

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
                LOGGER.error(
                "ERROR IMPORTING - %s"% psql_query.lastError().text())

    def import_patients(self):
        table_name = "patients"
        LOGGER.info("importing %s"% table_name)

    def import_static_charts(self):
        table_name = "static charts"
        LOGGER.info("importing %s"% table_name)

    def import_clerical_memos(self):
        table_name = "clerical memos"
        LOGGER.info("importing %s"% table_name)

    def import_addresses(self):
        table_name = "addresses"
        LOGGER.info("importing %s"% table_name)

    def import_clinical_memos(self):
        table_name = "clinical memos"
        LOGGER.info("importing %s"% table_name)

    def import_appointments(self):
        table_name = "appointments from aslot"
        LOGGER.info("importing %s"% table_name)

    def import_notes(self):
        table_name = "notes"
        LOGGER.info("importing %s"% table_name)

    def insert_null_user(self):
        LOGGER.info("inserting null user to index 0")

        ps_query = '''INSERT INTO users
        (ix, title, last_name, first_name, qualifications,
        abbrv_name, sex, dob, status, comments, modified_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        psql_query = QtSql.QSqlQuery(self.om2_session)

        psql_query.prepare(ps_query)

        for val in (0, "?", "?", "?", "?", "-", "M",
        QtCore.QDate(1900,1,1), "none", "",""):
            psql_query.addBindValue(val)

        psql_query.exec_()

    def import_users(self, ignore_errors=False):
        table_name = "users"
        LOGGER.info("importing %s"% table_name)

        try:
            filepath = os.path.abspath(
                os.path.join(self.import_directory, "%s.xml"% table_name))
            dom = minidom.parse(filepath)
        except IOError:
            LOGGER.error(
            "Unable to import users - no such file %s"% filepath)
            raise _ImportWarning


        record = InsertableRecord(self.om2_session, table_name)
        record.include_ix = True
        record.remove(record.indexOf("time_stamp"))
        ps_query, values = record.insert_query
        psql_query = QtSql.QSqlQuery(self.om2_session)

        rows = dom.getElementsByTagName(table_name.rstrip("s"))

        for row in rows:
            psql_query.prepare(ps_query)
            for node in ('ix', 'abbrv_name', 'role', 'title', 'last_name',
            'middle_name', 'first_name', 'qualifications', 'registration',
            'correspondence_name', 'sex', 'dob', 'dbuser',
            'status', 'comments', 'avatar_id', 'display_order'):
                vals = row.getElementsByTagName(node)
                try:
                    val = vals[0].firstChild.data.strip()
                    if node == "ix":
                        ix = int(val)
                    elif node == "abbrv_name":
                        user = val
                        self.USER_DICT[user] = ix

                except IndexError:
                    val = None
                except AttributeError:
                    val = ""
                psql_query.addBindValue(val)

            psql_query.addBindValue("imported from xml")
            psql_query.exec_()
            if not ignore_errors and psql_query.lastError().isValid():
                print "ERROR IMPORTING %s - %s"% (
                    row.toxml(),
                    psql_query.lastError().text())

        print self.USER_DICT

    def import_bpe(self):
        table_name = "bpe"
        LOGGER.info("importing %s"% table_name)

    def import_perio(self):
        table_name = "perio"
        LOGGER.info("importing %s"% table_name)

    def import_contracted_practitioners(self):
        table_name = "contracted practitioners"
        LOGGER.info("importing %s"% table_name)

    def import_telephones(self):
        table_name = "telephones"
        LOGGER.info("importing %s"% table_name)

    def import_tx_completed(self):
        table_name = "tx_completed"
        LOGGER.info("importing %s"% table_name)

    def import_all(self, *args):
        '''
        go to work

        .. note::
            all arguments are ignored. arguments are for inherited classes only
        '''
        LOGGER.info ("running import_all function")
        tracebacks = []
        for func in (
            self.insert_null_user,
            self.import_avatars,
            self.import_users,
            self.import_practitioners,
            self.import_patients,
            self.import_tx_completed,
            self.import_appointments,
            self.import_clerical_memos,
            self.import_clinical_memos,
            self.import_addresses,
            self.import_notes,
            self.import_static_charts,
            self.import_bpe,
            self.import_perio,
            self.import_contracted_practitioners,
            self.import_telephones,
            ):

            try:
                sys.stdout.flush()
                func()

            except _ImportWarning as exc:
                tracebacks.append((func, exc))
            except Exception as exc:
                LOGGER.exception("UNHANDLED EXCEPTION in function %s"% func)
                tracebacks.append((func, exc))

        LOGGER.info ("import_all function finished")
        if tracebacks:
            LOGGER.warning("The following functions had problems")
            for func, exc in tracebacks:
                if type(exc) == _ImportWarning:
                    LOGGER.warning("Warning from %s"% func)
                else:
                    LOGGER.error("Unhandled exception from %s"% func)
                    LOGGER.error("**** %s"% exc.message)

    def run(self):
        '''
        calls import_all
        '''
        self.import_all()


if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    im = Importer()
    im.set_session(sc)
    im.set_import_directory("/home/neil/adp_import")
    im.import_all()