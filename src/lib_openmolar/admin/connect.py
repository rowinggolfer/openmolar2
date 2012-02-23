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
AdminPostgresDatabase -
a custom class inheriting from :doc:`PostgresDatabase`
'''
from __future__ import division

from PyQt4 import QtSql
from PyQt4 import QtGui, QtCore

from lib_openmolar.common.datatypes import OMTypes, ConnectionData
from lib_openmolar.common.qt4.postgres.postgres_database import \
    PostgresDatabase

from lib_openmolar.admin.db_orm import *

class AdminConnection(PostgresDatabase):
    '''
    inherits from lib_openmolar.common.connect.PostgresDatabase,
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

    def populateDemo(self, ommitted_modules=[]):
        '''
        checks connection is to openmolar_demo, and if so,
        adds demo data to the tables.
        '''
        if not self.isOpen():
            return (False, _("no connection"))

        LOGGER.info("POPULATING DATABASE WITH DEMO DATA")

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
                        LOGGER.info(u"%s..."% query[:77])
                        logged = True

                    q_query = QtSql.QSqlQuery(self)
                    q_query.prepare(query)
                    for value in values:
                        q_query.addBindValue(value)
                    q_query.exec_()

                    if q_query.lastError().isValid():
                        error = q_query.lastError().text()
                        self.emit_(QtCore.SIGNAL("Query Error"), error)
                        LOGGER.error(error)
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
                LOGGER.error('ERROR INSTALLING DATA from module %s'%
                    module.__name__)
                LOGGER.exception('CRITICAL ERROR')

        self.emit_(QtCore.SIGNAL("demo install complete"))

        LOGGER.info("DEMO INSTALL COMPLETE")
        return True

    def emit_(self, *args):
        '''
        emit signals but be wary of case when there is no gui
        (ie. when install demo is called from CLI)
        '''
        if QtGui.QApplication.instance() is None:
            return
        QtGui.QApplication.instance().emit(*args)


class DemoAdminConnection(AdminConnection):
    '''
    A connection to the demo database (on localhost)
    used for testing purposes.
    '''
    def __init__(self):
        conn_data = ConnectionData()
        conn_data.demo_connection()

        AdminConnection.__init__(self, conn_data)
    

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")

    app = QtGui.QApplication([])

    sc = DemoAdminConnection()
    sc.connect()
