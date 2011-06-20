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

from lib_openmolar.common.connect import DatabaseConnection
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

    @property
    def has_all_empty_tables(self):
        tables = self.tables()
        query = '''SELECT relname, n_tup_ins - n_tup_del as rowcount
        FROM pg_stat_all_tables'''
        q_query = QtSql.QSqlQuery(query, self)

        while q_query.next():
            if (q_query.value(0).toString() in tables
            and q_query.value(1).toInt()[0] > 0):
                return False

        return True

    def get_db_schema(self):
        '''
        returns the schema of the currently selected database
        '''
        ret_string = u"%s %s\n\n%s\n"% (_("Describing schema of"),
        self.databaseName(),
        "|description start|".rjust(20,"=").ljust(80,"="))
        tables = self.get_available_tables()
        ret_string += "%d tables found\n\n"% len(tables)
        for table in tables:
            ret_string += "%s\n"% table
            query = '''
SELECT f.attname AS name, f.attnotnull AS notnull,
pg_catalog.format_type(f.atttypid,f.atttypmod) AS type,
CASE WHEN p.contype = 'p' THEN 'yes' ELSE '' END AS primarykey,
CASE WHEN p.contype = 'f' THEN g.relname END AS foreignkey,
CASE WHEN p.contype = 'f' THEN p.confkey END AS foreignkey_fieldnum,
CASE WHEN f.atthasdef = 't' THEN d.adsrc END AS default
FROM pg_attribute f JOIN pg_class c ON c.oid = f.attrelid
JOIN pg_type t ON t.oid = f.atttypid
LEFT JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = f.attnum
LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN pg_constraint p ON p.conrelid = c.oid AND f.attnum = ANY ( p.conkey )
LEFT JOIN pg_class AS g ON p.confrelid = g.oid
WHERE c.relkind = 'r'::char AND c.relname = '%s'
AND f.attnum > 0 ORDER BY f.attnum'''% table

            q_query = QtSql.QSqlQuery(query, self)

            schema_model = QtSql.QSqlQueryModel()
            schema_model.setQuery(q_query)

            spacing = {}
            no_columns = schema_model.columnCount()
            no_rows = schema_model.rowCount()

            for row in xrange(0, no_rows):
                for column in range(no_columns):
                    index = schema_model.createIndex(row, column)
                    item = schema_model.data(index)
                    data = item.toString()
                    try:
                        length = spacing[column]
                    except KeyError:
                        length = 0
                    if len(data) > length:
                        length = len(data)
                    spacing[column] = length

            breakline = u""
            header = u""
            for column in range(no_columns):
                item = schema_model.headerData(column, QtCore.Qt.Horizontal)
                data = unicode(item.toString())
                if len(data) > spacing[column]:
                    spacing[column] = len(data)
                breakline += "+" + "-"*spacing[column]
                header += u"|%s"% data.ljust(spacing[column])

            breakline += "+\n"
            ret_string += u"%s%s|\n%s"% (breakline, header, breakline)
            for row in xrange(0, no_rows):
                for column in range(no_columns):
                    index = schema_model.createIndex(row, column)
                    item = schema_model.data(index)
                    data = unicode(item.toString())
                    ret_string += u"|%s"% data.ljust(spacing[column])

                ret_string += "|\n"
            ret_string += "%s"% breakline

        return ret_string + "|description end|".rjust(20,"=").ljust(80,"=")

    def create_openmolar_tables(self, log):
        '''
        iterates over all known openmolar table classes,
        and creates the tables.
        '''
        if not self.isOpen():
            return (False, _("no connection"))

        def exec_queries(queries):
            result = True
            for query in queries:
                q_query = QtSql.QSqlQuery(query, self)
                if q_query.lastError().isValid():
                    log(q_query.lastError().text())
                    result = result and False
                log("="*60)
                log("")
            return result

        def apply_queries(object, removal=False):
            '''
            we have our object, now apply it's queries
            this is subroutined to limit the number of cascades of
            types and foreign keys
            '''
            if removal:
                rem_create_message = "removing"
                queries = object.removal_queries
            else:
                rem_create_message = "creating"
                queries =   object.creation_queries

            if type(object) == om_types.OMType:
                log_name = "type %s"% object.name
            else:
                log_name = "table %s"% object.tablename

            log_message = "%s %s - requires %d "% (rem_create_message,
                log_name, len(queries))
            if len(queries) == 1:
                log_message += "query"
            else:
                log_message += "queries"
            log(log_message, True)

            result = exec_queries(queries)

            return result

        result, message = True, _("UNABLE TO LAYOUT TABLES")

        #######################################################################
        ## iterate over all the objects in the ORM                           ##
        ## note - the order is important!                                    ##
        ## types first, then be wary of foreign keys                         ##
        #######################################################################

        objects = SETTINGS.OM_TYPES.values()

        for module in ADMIN_MODULES:
            objects.append(module.SchemaGenerator())

        objects.reverse()
        for object in objects:
            result = result and apply_queries(object, removal=True)

        objects.reverse()
        for object in objects:
            result = result and apply_queries(object) ## create

        log("CREATING FUNCTIONS")
        exec_queries(om_views.FUNCTION_SQLS)

        log("CREATING VIEWS")
        exec_queries(om_views.VIEW_SQLS)

        log("CREATING RULES")
        exec_queries(om_views.RULE_SQLS)

        if result:
            message = _("tables created")

        return (result, message)

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

    for table in sc.get_available_tables():
        print table

    print sc.has_all_empty_tables
