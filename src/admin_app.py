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
this module puts the "lib_openmolar" onto the python path,
and starts the admin gui
'''

import gettext
import os
import pexpect
import sys
import subprocess

from PyQt4 import QtGui, QtCore

def run():
    '''
    main function
    '''
    lang = os.environ.get("LANG")
    if lang:
        try:
            print "trying to install your environment language", lang
            lang1 = gettext.translation('openmolar', languages=[lang,])
            lang1.install(unicode=True)
        except IOError:
            print "%s not found, using default"% lang
            gettext.install('openmolar', unicode=True)
    else:
        print "no language environment found"
        gettext.install('openmolar', unicode=True)

    from lib_openmolar.admin.qt4gui import maingui
    maingui.main()

def populate_demo():
    '''
    will connect with no args (ie. default to openmolar_demo on localhost)
    and populate it with demo data.
    This can be done from within the app, but I need this functionality
    available from the CLI for testing.
    '''
    def duck_log(output, timestamp=None):
        print output

    print "installing demo..."

    from lib_openmolar.admin.connect import AdminConnection
    admin_conn = AdminConnection()
    admin_conn.connect()
    admin_conn.populateDemo(duck_log)
    admin_conn.close()

def layout_tables():
    '''
    will connect with no args (ie. default to openmolar_demo on localhost)
    and install the latest schema
    '''
    def duck_log(output, timestamp=None):
        print output

    print "installing schema..."

    from lib_openmolar.admin.connect import AdminConnection
    admin_conn = AdminConnection()
    admin_conn.connect()
    return admin_conn.create_openmolar_tables(duck_log)

def delete_demo_database():
    print "deleting any existing database called 'openmolar_demo'",
    print " (if already exists)..."
    p = subprocess.Popen(["dropdb", "openmolar_demo"])
    p.wait()
    print "SUCCESSFULLY dropped (or not present)\n"

def delete_demo_user():
    print "deleting postgres user 'om_user' (if already exists)..."
    p = subprocess.Popen(["dropuser", "om_user"])
    p.wait()
    print "SUCCESSFULLY dropped (or not present)\n"

def create_demo_database():
    print "creating database 'openmolar_demo'..."
    p = subprocess.Popen(["createdb", "openmolar_demo"])
    p.wait()


def create_demo_user():
    '''
    creates our default demo user 'om_demo'
    '''
    print "creating postgres user 'om_user'..."
    child = pexpect.spawn ("createuser -P -S -D -R om_user")
    child.expect ("Enter password for new role:")
    child.sendline ("password")
    child.expect ("Enter it again:")
    child.sendline ("password")
    child.logfile = sys.stdout
    child.expect(pexpect.EOF, timeout=None)

def install_fuzzy_match(db="openmolar_demo"):
    '''
    this function needs work to provide the soundex functions.
    '''

    print "="*80
    print "WARNING - manual installation of soundex function required"
    print "drop to a terminal and excute this"
    print "psql -d openmolar_demo < ",
    print "/usr/share/postgresql/8.4/contrib/fuzzystrmatch.sql"
    print "="*80

def initiate_demo_database():
    '''
    deletes any existing openmolar_demo database on this machine
    also removes any user om_user

    gksu -u postgres
    createdb openmolar_demo
    createuser -P om_user
    '''
    delete_demo_database()
    delete_demo_user()
    create_demo_database()
    install_fuzzy_match()
    create_demo_user()
    layout_tables()
    populate_demo()



if __name__ == "__main__":
    if "--install-demo" in sys.argv:
        initiate_demo_database()
        sys.exit(True)
    else:
        run()
