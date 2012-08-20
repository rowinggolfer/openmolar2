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

import psycopg2
import re
import socket

from lib_openmolar.server.misc.om_server_config import OMServerConfig


HEADER = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Server Message</title>
</head>
<body>
'''

FOOTER = None

def get_footer():
    global FOOTER
    if FOOTER is None:

        try:
            from lib_openmolar.server import version
            VERSION = "%s~hg%s"% (version.VERSION, version.revision_number)
            LOGGER.info("SERVER VERSION %s"% VERSION)
            LOGGER.debug("VERSION DATE %s"% version.date)
            LOGGER.debug("REVISION ID %s"% version.revision_id)
        except ImportError:
            VERSION = "Unknown"
            LOGGER.exception("unable to parse for server versioning")
    
        try:
            f = open("/etc/openmolar/manager_password.txt", "r")
            PASSWORD='''
                <em>Your admin password on this server is %s</em>
                    '''% re.search("PASSWORD = (.*)", f.read()).groups()[0]
            f.close()
            
        except IOError:
            PASSWORD="admin password file unreadable. Good!"


        FOOTER = '''
            <h4>Openmolar Server</h4>
                <div class="password">
                    %s
                </div>
            </div>
            <div class = "footer">
                <div class = "footer_txt">
                    <i>lib_openmolar.server version %s</i>
                    <a id = "show_log" href="show server log">%s</a>
                </div>
            </div>
            </body>
            </html>
            '''% (PASSWORD, VERSION, _("Show Server Log"))

    return FOOTER

def log_exception(func):
    def mess_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            LOGGER.exception("unhandled exception in message function")
            return ""
    return mess_func


class MessageFunctions(object):
    '''
    A class whose functions will be inherited by the server
    '''
    def __init__(self):
        self.config = OMServerConfig()

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

    @property
    def location_header(self):
        '''
        an html header giving information about the server.
        '''
        header = '''
        <div class="header">
             <div id="logo" />
            <div class='loc_header'><h3>%s %s '%s'</h3>
            %s %s
        </div>'''% (
            _("Connected to Openmolar-Server"),
            _("on host"), socket.gethostname(),
            _("providing remote procedure calls for"), 
            _("the admin and client applications."))

        return header
    
    @log_exception
    def get_schema_version(self, dbname):
        '''
        issues a query to get the value of schema_version stored in settings.
        '''
        try:
            conn = psycopg2.connect(self.__conn_atts(dbname))
            cursor = conn.cursor()
            cursor.execute(
                "select max(data) from settings where key='schema_version'")
            version = cursor.fetchone()
            conn.close()
            return version[0]
        except Exception as exc:
            LOGGER.exception("Serious Error")
            return "UNABLE TO get Version number."

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
        LOGGER.debug("polling for available databases")
        databases = []
        try:
            conn = psycopg2.connect(self.__conn_atts())
            cursor = conn.cursor()
            cursor.execute('''SELECT datname FROM pg_database JOIN pg_user
            ON pg_database.datdba = pg_user.usesysid
            where usename='openmolar' and datname != 'openmolar_master'
            order by datname''')
            for result in cursor.fetchall():
                databases.append(result[0])
            conn.close()
        except Exception as exc:
            LOGGER.exception("Serious Error")
            return "NONE"
        return databases

    def admin_welcome_template(self):
        '''
        return the html shown at admin_startup
        '''
        html = u'''
        %s
        %s
        <div class="main">
            <h4>Postgresql Server</h4>
            
            <table id="postgres_table">
                <tr>
                    <th>Parameter</th>
                    <th>Value</th>
                </tr>            
                <tr class="even">
                    <td>version</td>
                    <td>9.1.4</td>
                </tr>
                <tr class="odd">
                    <td>listening addresses</td>
                    <td>localhost</td>
                </tr>
                <tr class="even">
                <td>port</td>
                <td>5432</td>
                </tr>
             </table>

            <h4>%s</h4>
            {USERS}
            
            <h4>%s</h4>
            {DATABASE TABLE}
        %s
        '''% (
            HEADER, 
            self.location_header,
            _("Users who can login to postgres"),
            _("Openmolar Databases"),
            get_footer())

        return html
    
    def admin_welcome(self):
        '''
        the html shown on startup to the admin application
        '''
        dbs = self.available_databases()
        
        if dbs == "NONE":
            message = self.postgres_error_message()
        elif dbs == []:
            message = self.no_databases_message()
        else:
            message = self.admin_welcome_template()
            db_table = '''
            <table id="database_table">
            <tr>
                <th>%s</th>
                <th>%s</th>
                <th>%s</th>
                <th>%s</th>                
            </tr>
            '''% (  
                _("Database Name"), 
                _("Schema Version"), 
                _("Server Side Functions"),
                _("Local Functions")
                )

            for i, db in enumerate(dbs):
                s_v = self.get_schema_version(db)
                if i % 2 == 0:
                    db_table += '<tr class="even">'
                else:
                    db_table += '<tr class="odd">'
                db_table += '''
                        <td><b>%s</b></td>
                        <td>%s</td> 
                        <td>
                            <a class="management_link" href='manage_%s'>%s</a>
                        </td>
                        <td>
                            <a class="config_link" href='configure_%s'>%s</a>
                        </td>
                    </tr>
                '''% (
                db, s_v, db, _("Manage"), db, _("Configure"))

            user_html = "<ul>"
            for user in self.login_roles():
                user_html += "<li>%s</li>"% user
            user_html += "</ul>"

            message = message.replace("{USERS}", user_html)
            
            message = message.replace("{DATABASE TABLE}", db_table+"</table>")
        return message 

    def no_databases_message(self):
        return '''%s
        %s
        <p>%s<br />
        %s <a href="install_demo">%s</a>.
        </p>
        <br />
        %s'''%(HEADER, self.location_header,
        _("You do not appear to have any openmolar databases installed."),
        _("To install a demo database now"), _("Click Here"),
        get_footer())

    def postgres_error_message(self):
        return u'''%s
        %s
        <p>
        <b>%s</b>
        <br />
        %s <a href="show server log">%s</a>
        
        </p>
        <br />
        %s'''%(HEADER, self.location_header,
        _("Cannot connect to the postgres server on this machine!"),
        _("further information may be found in the"),
        _("Server Log File"),
        get_footer())

    
    def message_link(self, url):
        '''
        the "url" here will be text of a link that has been displayed as
        part of the html from the server.
        '''
        
        if url == "show server log":
            f = open("/var/log/openmolar/server.log", "r")
            data = f.read()
            f.close()
            return "<html><body><pre>%s</pre></body></html>"% data
        
        return None
    
    @log_exception
    def login_roles(self):
        '''
        get a list of roles allowed to login to postgres.
        '''
        try:
            conn = psycopg2.connect(self.__conn_atts())
            cursor = conn.cursor()
            cursor.execute(
                '''select usename from pg_catalog.pg_user 
                where usename not similar to 'om_[ac][dl][mi][ie]nt?_group%'
                ''')
            users = cursor.fetchall()
            conn.close()
            for user in users:
                yield user
        except Exception as exc:
            LOGGER.exception("Serious Error")
    
    @log_exception
    def list_sessions(self, db_name):
        '''
        list active connections
        '''
        try:
            conn = psycopg2.connect(self.__conn_atts())
            cursor = conn.cursor()
            cursor.execute(
                '''select usename, client_addr, application_name 
                from pg_catalog.pg_stat_activity where datname = '%s'
                '''% db_name)
            sessions = cursor.fetchall()
            conn.close()
            for user, address, application in sessions:
                yield (user, address, application)
        except Exception as exc:
            LOGGER.exception("Serious Error")
    

def _test():
    '''
    test the ShellFunctions class
    '''
    sf = MessageFunctions()
    LOGGER.debug(sf.admin_welcome())
    LOGGER.debug(sf.no_databases_message())
    LOGGER.debug(sf.postgres_error_message())
    
    dbname = "openmolar_demo"
    for user, address, application in sf.list_sessions(dbname):
        print (
        "'%s:%s' is using database '%s' with application '%s'"% (
        user, address, dbname, application))

    for user in sf.login_roles():
        print (user)

if __name__ == "__main__":
    from gettext import gettext as _
    import logging
    logging.basicConfig(level = logging.DEBUG)
    
    LOGGER = logging.getLogger("test")
    
    _test()
