#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011, Neil Wallace <rowinggolfer@googlemail.com>               ##
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

import logging
import subprocess
import sys
import psycopg2

class DBFunctions(object):
    '''
    A class whose functions will be inherited by the server
    '''
    MASTER_PWORD = ""
    if __name__ == "__main__":
        f = open("/home/neil/openmolar/master_pword.txt")
        MASTER_PWORD = f.read()
        f.close()

    def __init__(self):
        self.conn_atts = \
            "host=127.0.0.1 user=openmolar password=%s dbname=%s"% (
            self.MASTER_PWORD, "openmolar_master")

    def execute(self, statement):
        log = logging.getLogger("openmolar_server")
        try:
            conn = psycopg2.connect(self.conn_atts)
            conn.autocommit = True
            cursor = conn.cursor()
            log.debug(statement)
            cursor.execute(statement)
            conn.close()
            return True
        except:
            log.exception("error executing statements")
            return False

    def available_databases(self):
        '''
        get a list of databases (owned by "openmolar")

        the query I use for this is based on the following.

        SELECT datname, usename, datdba
        FROM pg_database JOIN pg_user
        ON pg_database.datdba = pg_user.usesysid and usename='openmolar';

        pg_database and pg_user are tables which do not require a superuser
        to poll for this information.

        '''
        log = logging.getLogger("openmolar_server")
        log.debug("polling for available databases")
        databases = []
        try:
            conn = psycopg2.connect(self.conn_atts)
            cursor = conn.cursor()
            cursor.execute('''SELECT datname FROM pg_database JOIN pg_user
            ON pg_database.datdba = pg_user.usesysid
            where usename='openmolar' and datname != 'openmolar_master'
            order by datname''')
            for result in cursor.fetchall():
                databases.append(result[0])
            conn.close()
        except Exception:
            log.exception("Serious Error")

        return databases

    def drop_db(self, name):
        '''
        drops the database with the name given
        '''
        log = logging.getLogger("openmolar_server")
        log.warning("dropping database %s"% name)
        try:
            self.execute("drop database %s"% name)
        except:
            log.exception("unable to drop database %s"% name)

    def create_db(self, name):
        '''
        creates a database with the name given
        '''
        log = logging.getLogger("openmolar_server")
        log.info("creating new database %s [with owner openmolar]"% name)
        try:
            self.execute("create database %s with owner openmolar"% name)
        except Exception as exc:
            log.exception("unable to create database '%s'"% name)
            return False
        return True

    def install_fuzzymatch(self, name):
        '''
        installs fuzzymatch functions into database with the name given
        '''
        log = logging.getLogger("openmolar_server")
        log.info("Installing fuzzymatch functions into database '%s'"% name)
        try:
            p = subprocess.Popen(["openmolar-install-fuzzymatch", name])
            p.wait()
        except Exception as exc:
            log.exception("unable to install fuzzymatch into '%s'"% name)
            return False
        return True

    def refresh_saved_schema(self):
        '''
        gets the schema from the admin app.
        only works if the admin app is installed on the server machine.
        note - this can also be done via the admin gui on a remote machine
        '''
        log = logging.getLogger("openmolar_server")
        log.info("polling admin application for latest schema")
        try:
            from lib_openmolar.admin.connect import AdminConnection
            sql =  AdminConnection().virgin_sql
            self.save_schema(sql)
        except ImportError as exc:
            log.warning("admin app not installed on this machine")
            return False
        return True

    def save_schema(self, sql, version="unknown"):
        '''
        the admin app is responsible for the schema in use.
        here, it has passed the schema in text form to the server, so that the
        server can lay out new databases without the admin app.
        '''
        filename = "/etc/openmolar/server/schema.sql"
        log = logging.getLogger("openmolar_server")
        log.info("saving schema version %s to %s"% (version, filename))
        f = open(filename, "w")
        f.write(sql)
        f.close()
        f = open("/etc/openmolar/server/schema_version.txt", "w")
        f.write(version)
        f.close()
        return True

    def get_schema(self):
        '''
        returns a tuple.
        (sql_statements, version)
        '''
        filename = "/etc/openmolar/server/schema.sql"

        log = logging.getLogger("openmolar_server")
        log.info("saving schema to %s"% filename)

        f = open(filename, "r")
        sql = f.read()
        f.close()

        f = open("/etc/openmolar/server/schema_version.txt", "r")
        version = f.read()
        f.close()
        return (sql, version)

    def layout_schema(self, name):
        '''
        creates a blank openmolar table set in the database with the name given
        '''
        sql, version_ = self.get_schema()
        log = logging.getLogger("openmolar_server")
        log.info("laying out schema version %s for database '%s'"% (
            version_, name))
        self.execute([sql], name)

    def get_demo_user(self):
        '''
        return the demo user (created on install)
        '''
        return {"username":"om_demo","password":"password"}


def _test():
    '''
    test the DBFunctions class
    '''
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger("openmolar_server")
    sf = DBFunctions()
    log.debug(sf.get_demo_user())
    log.debug(sf.available_databases())

if __name__ == "__main__":
    _test()
