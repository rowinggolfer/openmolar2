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

from datetime import datetime
import os
import re
import subprocess
import sys
import psycopg2

from lib_openmolar.server.misc.password_generator import new_password
from lib_openmolar.server.misc.om_server_config import OMServerConfig
from lib_openmolar.server.misc.backup_config import BackupConfig

def log_exception(func):
    def db_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            LOGGER.exception("unhandled exception")
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
        try:
            conn = psycopg2.connect(self.__conn_atts(dbname))
            try:
                # functions such as create and drop do not support transactions
                conn.autocommit = True
            except AttributeError:
                LOGGER.warning(
                    "no autocommit attribute in pyscopg2 - old version?")
                conn.set_isolation_level(0)

            cursor = conn.cursor()
            LOGGER.debug(statement)
            cursor.execute(statement)
            conn.close()
            return True
        except psycopg2.Warning as warn:
            LOGGER.warning(warn)
            conn.close()
            return True
        except psycopg2.Error as exc:
            LOGGER.exception("error executing statement")
            LOGGER.error(statement)
            raise exc

    @log_exception
    def newDB_sql(self, dbname):
        '''
        returns the sql to layout the users and tables in a database.
        '''
        sql_file = "/usr/share/openmolar/blank_schema.sql"
        perms_file = "/usr/share/openmolar/permissions.sql"

        LOGGER.info("reading sql from %s"% sql_file)
        LOGGER.info("reading sql from %s"% perms_file)

        groups = {}
        perms, sql = "",""

        for group in ('admin', 'client'):
            groupname = "om_%s_group_%s"% (group, dbname)

            sql += "drop role if exists %s;\n"% groupname
            sql += "create role %s;\n"% groupname

            groups[group] = groupname

        try:
            f = open(sql_file, "r")
            sql += f.read()
            f.close()

            f = open(perms_file, "r")
            perms = f.read()
            f.close()
        except IOError:
            LOGGER.exception("error reading sql files.")

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
        try:
            LOGGER.info("creating new database %s [with owner openmolar]"% dbname)
            self._execute("create database %s with owner openmolar"% dbname)

            return self._layout_schema(dbname)
        except:
            LOGGER.exception("exeption in %(module)s")
        return False

    @log_exception
    def _layout_schema(self, dbname):
        '''
        creates a blank openmolar table set in the database with the name given
        '''
        try:
            sql = self.newDB_sql(dbname)

            LOGGER.info("laying out schema for database '%s'"% dbname)

            self._execute(sql, dbname)
            return True
        except:
            LOGGER.exception("exeption in %(module)s")
        return False

    @log_exception
    def create_demo_user(self):
        '''
        create our demo user
        '''
        LOGGER.info("creating a demo user")

        if self.create_user("om_demo", "password"):
            LOGGER.info("user om_demo created")
        else:
            LOGGER.error("unable to create user om_demo. perhaps exists already?")

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
        LOGGER.warning("user '%s' is deleting database %s" %(
            self._user, dbname))
        LOGGER.warning("removing database (if exists) %s"% dbname)
        if self._execute('drop database if exists %s;'% dbname):
            LOGGER.info("database '%s' removed"% dbname)
        else:
            return False

        for group in ("admin", "client"):
            user_group = 'om_%s_%s;'% (group, dbname)
            LOGGER.warning("removing role (if exists) '%s'"% user_group)
            if self._execute('drop user if exists %s'% user_group ):
                LOGGER.info("role '%s' removed"% user_group)
            else:
                return False
            
        if dbname == "openmolar_demo":
            LOGGER.warning("removing role (if exists) om_demo")
            self._execute('drop user if exists om_demo')
        
        #clean up the permission groups.
        for group in ('admin', 'client'):
            groupname = "om_%s_group_%s"% (group, dbname)
            LOGGER.warning("attempting to remove role '%s'"% groupname)
            self._execute("drop role if exists %s;\n"% groupname)
            
        return "Dropped Database %s"% dbname

    @log_exception
    def create_user(self, username, password=None):
        '''
        create a user (remote user)
        '''
        LOGGER.info("add a login user with name '%s' and password"% username)

        if password is None:
            password = new_password()

        try:
            self._execute("create user %s"% username)
            self._execute(
                "alter user %s with login encrypted password '%s' "% (
                    username, password))
            return True
        except Exception:
            LOGGER.exception("Serious Error")
        return False

    @log_exception
    def grant_user_permissions(self, user, dbname, admin=True, 
    client=True):
        '''
        grant/revoke permissions for a user to database dbname
        '''
        LOGGER.info("adding %s to priv groups on database %s"% (user, dbname))

        SQL = ""
        if admin:
            SQL += "GRANT om_admin_group_%s to %s;\n"% (dbname, user)
        else:
            SQL += "REVOKE om_admin_group_%s from %s;\n"% (dbname, user)
        if client:
            SQL += "GRANT om_client_group_%s to %s;\n"% (dbname, user)
        else:
            SQL += "REVOKE om_client_group_%s from %s;\n"% (dbname, user)
            
        try:
            self._execute(SQL, dbname)
            return True
        except Exception:
            LOGGER.exception("Serious Error")
        return False

    @log_exception
    def get_user_permissions(self, user, dbname):
        '''
        get permissions for a user to database dbname
        returns a dict.
        {"admin":True,"client":True}
        '''
        LOGGER.debug(
            "getting priv groups for user '%s' on dbase '%s'"% (user, dbname))
        conn = psycopg2.connect(self.__conn_atts(dbname))
        cursor = conn.cursor()
        cursor.execute('''
        select rolname from pg_user 
        join pg_auth_members on (pg_user.usesysid=pg_auth_members.member) 
        join pg_roles on (pg_roles.oid=pg_auth_members.roleid) 
        where pg_user.usename=%s'''
        , (user,))
        perms = {}
        
        for rolname in cursor.fetchall():
            for group in ["admin","client"]:
                if re.match("om_%s_group_%s"% (group, dbname), rolname[0]):
                    perms[group] = True
        return perms

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
        LOGGER.warning("removing user %s"% username)
        if self._execute('drop user %s;'% username):
            LOGGER.info("user '%s' removed"% username)
            return True
        return False

    def _tables(self, dbname):
        '''
        returns all the table names in schema dbname
        '''
        conn = psycopg2.connect(self.__conn_atts(dbname))
        cursor = conn.cursor()
        cursor.execute(
        "SELECT tablename FROM pg_tables WHERE schemaname='public'")
        for tablename in cursor.fetchall():
            yield tablename[0]

    def _sequences(self, dbname, exceptions):
        '''
        returns all the sequences in schema dbname
        exceptions is a list of tables whose sequences are to be ignored.
        '''
        conn = psycopg2.connect(self.__conn_atts(dbname))
        cursor = conn.cursor()
        cursor.execute(
        "select sequence_name from information_schema.sequences")
        for sequence_name in cursor.fetchall():
            for exception in exceptions:
                if sequence_name[0].startswith(exception):
                    continue
            yield sequence_name[0]

    def truncate_demo(self):
        '''
        truncates the demo database
        '''
        return self.truncate_all_tables("openmolar_demo")

    @log_exception
    def truncate_all_tables(self, dbname):
        '''
        truncates all tables except 'procedure codes'
        resets the patient serialno index
        '''
        LOGGER.warning("removing all data from %s"% dbname)
        
        exceptions = ("settings", "procedure_codes")
        
        for tablename in self._tables(dbname):
            if tablename not in exceptions:
                LOGGER.info("... truncating '%s'"% tablename)
                self._execute("TRUNCATE %s CASCADE"% tablename, dbname)
        for sequence in self._sequences(dbname, exceptions):
            LOGGER.info("... reseting sequence '%s'"% sequence)
            self._execute("select setval('%s', 1, false)"% sequence,
                dbname)
        return True
    
    @log_exception
    def backup_db(self, dbname, schema_only=False):
        '''
        calls a pg_dump (using db user openmolar)
        if schema_only is True, then the -s option is passed into pg_dump.
        '''
        LOGGER.info("backing up %s"% dbname)

        opts = ["-s", dbname] if schema_only else [dbname]
        
        proc = subprocess.Popen(
            ["pg_dump", "-h", "127.0.0.1", 
            "-U", "openmolar", "-W"] + opts,
            stdin = subprocess.PIPE,
            stdout=subprocess.PIPE)
        
        proc.stdin.write(self.MASTER_PWORD)
        proc.stdin.flush()
            
        stdout, stderr = proc.communicate()
        
        if stderr:
            LOGGER.warning("Errors were thrown %s"% stderr)
        
        try:
            BACKUP_DIR = BackupConfig().backup_dir
        except IOError:
            BACKUP_DIR = "/usr/share/openmolar/backups/"
        
        backup_dir = os.path.join(BACKUP_DIR, dbname)
        
        if not os.path.isdir(backup_dir):
            os.makedirs(backup_dir)
        
        filename = "schema"% now if schema_only else "backup"
        
        filename += datetime.now().strftime("%Y%m%d_%H%M%S") + ".sql"
            
        filepath = os.path.join(backup_dir, filename)
        
        f = open(filepath, "w")
        f.write(stdout)
        f.close()
        
        LOGGER.info("file saved as %s"% filepath)

    @log_exception
    def get_update_script(self, original, current):
        '''
        calls apgdiff to see if the schemas are the same
        '''
        LOGGER.info("comparing schemas of %s and %s"% (original, current))

        proc = subprocess.Popen(
            ["apgdiff", "--ignore-start-with", original, current],
            stdout=subprocess.PIPE)
        
        stdout, stderr = proc.communicate()
        
        if stderr:
            LOGGER.warning("Errors were thrown %s"% stderr)
        
        if not stdout:
            return ""
        return stdout 
        
def _test():
    '''
    test the DBFunctions class
    '''
    sf = DBFunctions()
    sf._user = "test_user"
    
    dbname = "openmolar_demo"
    #LOGGER.debug(sf.newDB_sql(dbname))
    #sf.drop_db(dbname)
    #sf.drop_demo_user()
    #sf.create_db(dbname)
    #sf.create_demo_user()
    #sf.truncate_all_tables(dbname)
    
    print sf.get_user_permissions("om_demo", dbname)
    
if __name__ == "__main__":
    import __builtin__
    import logging

    logging.basicConfig(level=logging.DEBUG)
    __builtin__.LOGGER = logging.getLogger("openmolar_server")
    _test()
