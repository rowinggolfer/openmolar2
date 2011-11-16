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
AdminDatabaseConnection -
a custom class inheriting from lib_openmolar.common.DatabaseConnection
'''
from __future__ import division

from PyQt4 import QtSql
from PyQt4 import QtGui, QtCore

from lib_openmolar.common.connect import DatabaseConnection, ConnectionError
from lib_openmolar.common.settings import om_types
from lib_openmolar.common import SETTINGS

from lib_openmolar.admin.db_orm import *

class AdminConnection(DatabaseConnection):
    '''
    inherits from lib_openmolar.common.connect.DatabaseConnection,
    which in turn inherits from PyQt4.QSql.QSqlDatabase
    '''
    @property
    def admin_modules(self):
        '''
        provide access to the list of modules in use
        '''
        return ADMIN_MODULES

    def get_available_tables(self):
        '''
        returns a list of tables in the currently selected database
        '''
        return self.tables()

    def populateDemo(self, log, ommitted_modules=[]):
        '''
        checks connection is to openmolar_demo, and if so,
        adds demo data to the tables.
        '''
        if not self.isOpen():
            return (False, _("no connection"))

        log("POPULATING DATABASE WITH DEMO DATA", True)

        ## iterate over the ORM modules
        ## order is important (foreign keys etc)

        for module in ADMIN_MODULES:
            if module in ommitted_modules:
                continue
            try:

                builder = module.DemoGenerator(self)
                logged = False

                total_number_of_queries = builder.length
                number_of_queries_executed = 0

                for query, values in builder.demo_queries():
                    if not logged:
                        log(u"%s..."% query[:77])
                        logged = True

                    q_query = QtSql.QSqlQuery(self)
                    q_query.prepare(query)
                    for value in values:
                        q_query.addBindValue(value)
                    q_query.exec_()

                    if q_query.lastError().isValid():
                        error = q_query.lastError().text()
                        self.emit_(QtCore.SIGNAL("Query Error"), error)
                        log(error)
                        break

                    number_of_queries_executed += 1
                    progress = int(number_of_queries_executed /
                    total_number_of_queries * 100)

                    self.emit_(QtCore.SIGNAL("demo progress"),
                                module, progress)

                else: #some modules have no queries
                    self.emit_(QtCore.SIGNAL("demo progress"), module, 100)

            except Exception as e:
                self.emit_(QtCore.SIGNAL("Query Error"),
                    '''Error installing demo data from module %s<hr />%s'''% (
                        module.__name__, e))
                log('CRITICAL ERROR')
                log('\tERROR INSTALLING DATA from module %s'% module.__name__)
                log('\t%s'% e)

        self.emit_(QtCore.SIGNAL("demo install complete"))

        log("DEMO INSTALL COMPLETE")
        return True

    def emit_(self, *args):
        '''
        emit signals but be wary of case when there is no gui
        (ie. when install demo is called from CLI)
        '''
        if QtGui.QApplication.instance() is None:
            return
        QtGui.QApplication.instance().emit(*args)


if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")

    app = QtGui.QApplication([])
    sc = AdminConnection()
    sc.connect()

    #print "listing tables in", sc.databaseName()
    #for table in sc.get_available_tables():
    #    print "\t%s"% table


    print sc.virgin_sql