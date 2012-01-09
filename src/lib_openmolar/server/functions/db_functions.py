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
from lib_openmolar.server.functions.password_generator import new_password

from lib_openmolar.server.functions.om_server_config import OMServerConfig

def log_exception(func):
    def db_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            log = logging.getLogger("openmolar-server")
            log.debug("unhandled exception")
            return ""
    return db_func

class DBFunctions(object):
    '''
    A class whose functions will be inherited by the server
    '''
    def __init__(self):
        self.config = OMServerConfig()

    @property
    def default_conn_atts(self):
        return self.__conn_atts()

    def __conn_atts(self, dbname="openmolar_master"):
        '''
        has to be a private function because of the password!
        a well set up server will restrict user "openmolar"
        to a unix socket connection (ie local machine only)
        or at the very least a TCP/IP connection to only localhost.
        (function doesn't get picked up by register_instance)
        '''
        return "host='%s' user='%s' port='%s' password='%s' dbname='%s'"% (
            self.config.postgres_host, self.config.postgres_user,
            self.config.postgres_port,
            self.config.postgres_pass, dbname)

    @log_exception
    def _execute(self, statement, dbname="openmolar_master"):
        '''
        execute an sql statement with default connection rights.
        '''
        log = logging.getLogger("openmolar_server")
        try:
            conn = psycopg2.connect(self.__conn_atts(dbname))
            try:
                # functions such as create and drop do not support transactions
                conn.autocommit = True
            except AttributeError:
                log.warning(
                    "no autocommit attribute in pyscopg2 - old version?")
                conn.set_isolation_level(0)

            cursor = conn.cursor()
            #log.debug(statement)
            cursor.execute(statement)
            conn.close()
            return True
        except psycopg2.Warning as warn:
            log.warning(warn)
            conn.close()
            return True
        except psycopg2.Error as exc:
            log.exception("error executing statement")
            log.error(statement)
            raise exc

    @log_exception
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
        except Exception as exc:
            log.exception("Serious Error")
            return "NONE"
        return databases

    @log_exception
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

    @log_exception
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

    @log_exception
    def install_fuzzymatch(self, dbname):
        '''
        installs fuzzymatch functions into database with the name given
        '''
        log = logging.getLogger("openmolar_server")
        log.info("Installing fuzzymatch functions into database '%s'"% dbname)
        try:
            p = subprocess.Popen(["openmolar-install-fuzzymatch", dbname],
                stdout = subprocess.PIPE)
            while True:
                line = p.stdout.readline()
                if not line:
                    break
                log.info(line)
        except Exception as exc:
            log.exception("unable to install fuzzymatch into '%s'"% dbname)
            return False
        return True

    @log_exception
    def newDB_sql(self, dbname):
        '''
        returns the sql to layout the users and tables in a database.
        '''
        sql_file = "/usr/share/openmolar/blank_schema.sql"
        perms_file = "/usr/share/openmolar/permissions.sql"

        log = logging.getLogger("openmolar_server")
        log.info("reading sql from %s"% sql_file)
        log.info("reading sql from %s"% perms_file)

        groups = {}
        perms, sql = "",""

        for group in ('admin', 'client'):
            groupname = "om_%s_group_%s"% (group, dbname)

            sql += "drop user if exists %s;\n"% groupname
            sql += "create user %s;\n"% groupname

            groups[group] = groupname

        try:
            f = open(sql_file, "r")
            sql += f.read()
            f.close()

            f = open(perms_file, "r")
            perms = f.read()
            f.close()
        except IOError:
            log.exception("error reading sql files.")

        permissions = perms.replace("ADMIN_GROUP", groups["admin"]).replace(
                            "CLIENT_GROUP", groups["client"])

        return sql + permissions

    @log_exception
    def create_demodb(self):
        '''
        creates a demo database (loose permission to do this)
        '''
        return self.create_db("openmolar_demo")

    @log_exception
    def create_db(self, dbname):
        '''
        creates a database with the name given
        '''
        log = logging.getLogger("openmolar_server")
        try:
            log.info("creating new database %s [with owner openmolar]"% dbname)
            self._execute("create database %s with owner openmolar"% dbname)

            return self._layout_schema(dbname)
        except:
            log.exception("exeption in %(module)s")
        return False

    @log_exception
    def _layout_schema(self, dbname):
        '''
        creates a blank openmolar table set in the database with the name given
        '''
        try:
            sql = self.newDB_sql(dbname)

            log = logging.getLogger("openmolar_server")
            log.info("laying out schema for database '%s'"% dbname)

            self._execute(sql, dbname)
            return True
        except:
            log.exception("exeption in %(module)s")
        return False

    @log_exception
    def create_demo_user(self):
        '''
        create our demo user
        '''
        log = logging.getLogger("openmolar_server")
        log.info("creating a demo user")

        if self.create_user("om_demo", "password"):
            log.info("user om_demo created")
        else:
            log.error("unable to create user om_demo. perhaps exists already?")

        return self.grant_user_permissions("om_demo", "openmolar_demo",
                True, True)

    @log_exception
    def drop_demodb(self):
        '''
        remove the openmolar_demo database
        '''
        return self.drop_db("openmolar_demo")

    @log_exception
    def drop_db(self, dbname):
        '''
        remove the database with this name
        also attempts to remove the standard user groups (this will fail if
        other roles in these groups haven't been removed first)
        '''
        logging.warning("user '%s' is deleting database %s" %(
            self._user, dbname))
        logging.warning("removing database (if exists) %s"% dbname)
        if self._execute('drop database if exists %s;'% dbname):
            logging.info("database '%s' removed"% dbname)
        else:
            return False

        for group in ("admin", "client"):
            user_group = 'om_%s_%s;'% (group, dbname)
            logging.warning("removing role (if exists) '%s'"% user_group)
            if self._execute('drop user if exists %s'% user_group ):
                logging.info("role '%s' removed"% user_group)
            else:
                return False

        return True

    @log_exception
    def create_user(self, username, password=None):
        '''
        create a user (remote user)
        '''
        log = logging.getLogger("openmolar_server")
        log.info("add a login user with name '%s' and password"% username)

        if password is None:
            password = new_password()

        try:
            self._execute(
                "create user %s with login encrypted password '%s' "% (
                    username, password))
            return True
        except Exception:
            log.exception("Serious Error")
        return False

    @log_exception
    def grant_user_permissions(self, user, dbname, admin=True, client=True):
        '''
        grant permissions for a user to database dbname
        '''
        log = logging.getLogger("openmolar_server")
        log.info("adding %s to priv groups on database %s"% (user, dbname))

        SQL = ""
        if admin:
            SQL += "GRANT om_admin_group_%s to %s;\n"% (dbname, user)
        if client:
            SQL += "GRANT om_client_group_%s to %s;\n"% (dbname, user)
        try:
            self._execute(SQL, dbname)
            return True
        except Exception:
            log.exception("Serious Error")
        return False

    @log_exception
    def drop_demo_user(self):
        '''
        drops the demo user
        '''
        return self.drop_user("om_demo")

    @log_exception
    def drop_user(self, username):
        '''
        drops a user
        '''
        logging.warning("removing user %s"% username)
        if self._execute('drop user %s;'% username):
            logging.info("user '%s' removed"% username)
            return True
        return False

def _test():
    '''
    test the DBFunctions class
    '''
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger("openmolar_server")
    sf = DBFunctions()
    sf._user = "test_user"
    log.debug(sf.available_databases())

    dbname = "openmolar_demo"
    #log.debug(sf.newDB_sql(dbname))
    #sf.drop_db(dbname)
    #sf.drop_demo_user()
    sf.create_db(dbname)
    sf.create_demo_user()
    #sf.drop_db(dbname)
    #sf.drop_demo_user()


if __name__ == "__main__":
    _test()
