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
this module can convert data from the mysql openmolar schema, and dump into
the new postgresql schema.

command line arguments can be passed in
(specifying locations of the old and new databases, passwords etc)

an example of usage would be::

    python main.py -u [USER] -p [PASSWORD] --pg_user [USER] --pg_password [PASSWORD] --pg_dbname openmolar_test -i /path/to/importdir> logfile.txt


If information is missing a gui is raised.
'''

import sys

if __name__ == "__main__":
    print "setting path"
    import os
    os.chdir(os.path.dirname(__file__))
    sys.path.insert(0, os.path.abspath("../../../../../"))

from lib_openmolar.admin.data_import.import_om1 import *
from lib_openmolar.common.qt4.postgres.postgres_database import (
    PostgresDatabase, ConnectionError)

from PyQt4 import QtCore, QtGui

import optparse

class Parser(optparse.OptionParser):
    '''
    Inherits from optparse.OptionParser, and checks the cli arguments
    '''
    def __init__(self):
        '''
        adds options
            - --user
            - --Host
            - --password
            - --Port
            - --dbname
            - --pg_user
            - --pg_host
            - --pg_password
            - --pg_port
            - --pg_dbname
            - --import_directory
        '''
        optparse.OptionParser.__init__(self)

        self.add_option("-u", "--user",
                        dest = "username",
                        help = "username for the original MySQL database",
                        type="string")

        self.add_option("-H", "--Host",
                        dest = "hostname", default = 'localhost',
                        help = "hostname for the original MySQL database",
                        type="string")

        self.add_option("-p", "--password",
                        dest = "password",
                        help = "password for the original MySQL database",
                        type="string")

        self.add_option("-P", "--Port",
                        dest = "port", default = 3306,
                        help = "port for the original MySQL database",
                        type="int")

        self.add_option("-d", "--dbname",
                        dest = 'dbname', default = 'openmolar',
                        help = "dbname for the original MySQL database",
                        type="string")

        self.add_option("--pg_user",
                        dest = "pg_username",
                        help = "username for the new Postgres database",
                        type="string")

        self.add_option("--pg_host",
                        dest = "pg_hostname", default = '127.0.0.1',
                        help = "hostname for the new Postgresdatabase",
                        type="string")

        self.add_option("--pg_password",
                        dest = "pg_password",
                        help = "password for the new Postgresdatabase",
                        type="string")

        self.add_option("--pg_port",
                        dest = "pg_port", default = 5432,
                        help = "port for the new Postgresdatabase",
                        type="int")

        self.add_option("--pg_dbname",
                        dest = 'pg_dbname', default = 'openmolar',
                        help = "dbname for the new Postgresdatabase",
                        type="string")

        self.add_option("-i", "--import_directory",
                        dest = 'import_directory',
                        help = "dbname for the new Postgresdatabase",
                        type="string")

        self.add_option("-m", "--min_sno",
                        dest = 'min_sno', default = 0,
                        help = "the minimum id to be imported, default is 0",
                        type="int")

        self.add_option("-M", "--max_sno",
                        dest = 'max_sno', default = -1,
                        help = "the maximum id to be imported, or -1 for all (default)",
                        type="int")


    def parse_args(self):
        options, args = optparse.OptionParser.parse_args(self)
        if args != []:
            self.error("incorrect number of arguments")
        return options, args

def main():
    '''
    parse cl for these connection params.
    if none found, raise a gui.
    '''

    parser  = Parser()
    options, args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)

    if (options.username !=None and
    options.password !=None and
    options.pg_username !=None and
    options.pg_password !=None and
    options.import_directory !=None) :
        dl = options
    else:
        dl = ConnectionParamsDialog(options)
        if not dl.exec_():
            print ("nothing to do")
            return

    connection = MySQLConnection(   host=dl.hostname,
                                    user=dl.username,
                                    passwd=dl.password,
                                    db_name=dl.dbname,
                                    port=dl.port)
    try:
        connection.connect()
    except IOError as e:
        QtGui.QMessageBox.warning(None, "error",
        "unable to connect to Mysql <hr />%s "% e)
        sys.exit()

    new_connection = PostgresDatabase(    host=dl.pg_hostname,
                                        user=dl.pg_username,
                                        passwd=dl.pg_password,
                                        db_name=dl.pg_dbname,
                                        port=dl.pg_port)

    try:
        new_connection.connect()
    except ConnectionError as e:
        QtGui.QMessageBox.warning(None, "error",
        "unable to connect to postgres <hr />%s "% e)
        sys.exit()

    print "Importing from MYSQL DB %s@%s:%s %s"% (
        dl.username, dl.hostname, dl.port, dl.dbname)
    print "Into PSQL DB %s:%s:%s %s" %(
        dl.pg_username, dl.pg_hostname, dl.pg_port, dl.pg_dbname)
    print "using metadata and xml files stored in %s"% dl.import_directory

    importer = OM1Importer(connection, new_connection)

    importer.set_import_directory(dl.import_directory)

    importer.import_all(options.min_sno, options.max_sno)

    sys.exit(app.exit())

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")

    main()
