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
from lib_openmolar.server.password_generator import new_password


class DBFunctions(object):
    '''
    A class whose functions will be inherited by the server
    '''
    MASTER_PWORD = ""

    def __init__(self):
        if __name__ == "__main__":
            ## this is useful for testing purposes only
            f = open("/home/neil/openmolar/master_pword.txt")
            self.MASTER_PWORD = f.read()
            f.close()

    @property
    def default_conn_atts(self):
        return self.__conn_atts()

    def __conn_atts(self, dbname="openmolar_master"):
        '''
        has to be a private function because of the password!
        a well set up server will restrict user "openmolar" to TCP/IP
        connections restricted to localhost though.
        (doesn't get picked up by register_instance)
        '''
        return "host=127.0.0.1 user=openmolar password=%s dbname=%s"% (
            self.MASTER_PWORD, dbname)

    def _execute(self, statement, dbname="openmolar_master"):
        '''
        execute an sql statement with default connection rights.
        '''
        log = logging.getLogger("openmolar_server")
        try:
            conn = psycopg2.connect(self.__conn_atts(dbname))
            conn.autocommit = True
            cursor = conn.cursor()
            #log.debug(statement)
            cursor.execute(statement)
            conn.close()
            return True
        except:
            log.exception("error executing statement")
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
            conn = psycopg2.connect(self.default_conn_atts)
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
            self._execute("drop database %s"% name)
        except:
            log.exception("unable to drop database %s"% name)

    def create_db(self, name):
        '''
        creates a database with the name given
        '''
        log = logging.getLogger("openmolar_server")
        log.info("creating new database %s [with owner openmolar]"% name)
        try:
            self._execute("create database %s with owner openmolar"% name)
        except Exception as exc:
            log.exception("unable to create database '%s'"% name)
            return False
        return True

    def create_usergroups(self, dbname):
        '''
        creates usergroups.
        to do this we create two non-login roles.
        Any future users can inherited permissions from these guys.
        permissions are way to permissive at this point
        '''
        log = logging.getLogger("openmolar_server")
        log.info(
            "creating new roles to act as group privileges for %s"% dbname)
        admin = '%s_admin_privs;' %dbname
        client = '%s_client_privs;' %dbname

        for group in (admin, client):
            SQL = 'create role %s;\n'% group
            SQL += 'grant all privileges on patients to %s ;\n'% group
            logging.debug(SQL)
            try:
                self._execute(SQL, dbname)
            except Exception as exc:
                log.exception("problem executing %s"% SQL)
        return True

    def install_fuzzymatch(self, dbname):
        '''
        installs fuzzymatch functions into database with the name given
        '''
        log = logging.getLogger("openmolar_server")
        log.info("Installing fuzzymatch functions into database '%s'"% dbname)
        try:
            p = subprocess.Popen(["openmolar-install-fuzzymatch", dbname])
            p.wait()
        except Exception as exc:
            log.exception("unable to install fuzzymatch into '%s'"% dbname)
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

    def save_schema(self, sql):
        '''
        the admin app is responsible for the schema in use.
        here, it has passed the schema in text form to the server, so that the
        server can lay out new databases without the admin app.
        '''
        filename = "/usr/share/blank_schema.sql"
        log = logging.getLogger("openmolar_server")
        log.info("saving schema to %s"% filename)
        f = open(filename, "w")
        f.write(sql)
        f.close()
        return True

    def get_schema(self):
        '''
        gets the schema from file
        '''
        filename = "/usr/share/openmolar/blank_schema.sql"

        log = logging.getLogger("openmolar_server")
        log.info("reading schema from %s"% filename)

        f = open(filename, "r")
        sql = f.read()
        f.close()

        return sql

    def layout_schema(self, dbname):
        '''
        creates a blank openmolar table set in the database with the name given
        '''
        sql = self.get_schema()
        log = logging.getLogger("openmolar_server")
        log.info("laying out schema for database '%s'"% dbname)

        try:
            self._execute(sql, dbname)
            return True
        except Exception:
            log.exception("Serious Error")
        return False

    def create_demo_user(self):
        '''
        create our demo user
        '''
        log = logging.getLogger("openmolar_server")
        log.info("creating a demo user")

        return self.create_user("om_demo", "password")

    def create_user(self, username, password=None):
        '''
        create a user (remote user)
        '''
        log = logging.getLogger("openmolar_server")
        log.info("add a user(role) with name '%s'"% username)

        if password is None:
            password = new_password()

        try:
            self._execute(
                "create user %s with password '%s' "% (username, password))
            return True
        except Exception:
            log.exception("Serious Error")
        return False

    def grant_user_permissions(self, user, dbname, admin=True, client=True):
        '''
        grant permissions for a user to database dbname
        '''
        log = logging.getLogger("openmolar_server")
        log.info("adding %s to priv groups on database %s"% (user, dbname))

        SQL = ""
        if admin:
            SQL += "GRANT %s_admin_privs to %s;\n"% (dbname, user)
        if client:
            SQL += "GRANT %s_client_privs to %s;\n"% (dbname, user)
        try:
            self._execute(SQL, dbname)
            return True
        except Exception:
            log.exception("Serious Error")
        return False

    def grant_demo_user_permissions(self, dbname="openmolar_demo"):
        return self.grant_user_permissions('om_demo', dbname)


def _test():
    '''
    test the DBFunctions class
    '''
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger("openmolar_server")
    sf = DBFunctions()
    #sf.create_demo_user()
    #log.debug(sf.get_demo_user())
    #log.debug(sf.available_databases())
    #log.debug(sf.get_schema())

    dbname = "openmolar_demo"
    sf.create_db(dbname)
    sf.layout_schema(dbname)
    sf.create_usergroups(dbname)
    sf.create_demo_user()
    sf.grant_demo_user_permissions(dbname)

if __name__ == "__main__":
    _test()
