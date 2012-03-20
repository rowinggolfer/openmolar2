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

import os
import hashlib

from lib_openmolar.admin.db_orm import *

def proc_code_inserts():
    for code in SETTINGS.PROCEDURE_CODES:
        yield '''INSERT INTO procedure_codes (category, code, description)
        VALUES ('%s', '%s', '%s');\n'''% (
        code.cat_no, code.code, code.description)


class SchemaManager(object):
    _bare_sql = None
    _md5 = None

    @property
    def CURRENT_SQL(self):
        '''
        the Sql applied to create the current schema
        this gathers up all types, tables, functions, views and rules,
        along with data for the special procedure codes table.
        '''
        if self._bare_sql is None:
            LOGGER.debug("grabbing CURRENT_SQL")
            queries = ""

            # gather up all types, tables, functions, views and rules
            klasses = SETTINGS.OM_TYPES.values()
            for module in ADMIN_MODULES:
                klasses.append(module.SchemaGenerator())
            klasses.append(admin_procedure_codes.SchemaGenerator())
            for klass in klasses:
                for query in klass.creation_queries:
                    queries += query + ";\n"

            for query in proc_code_inserts():
                queries += query

            for view_queries in (
                om_views.FUNCTION_SQLS,
                om_views.VIEW_SQLS,
                om_views.RULE_SQLS):
                for query in view_queries:
                    queries += query + ";\n"

            self._bare_sql = queries

        return self._bare_sql

    @property
    def MD5(self):
        LOGGER.debug("getting MD5 sum for the schema")
        if self._md5 is None:
            self._md5 = hashlib.md5(self.CURRENT_SQL).hexdigest()
        LOGGER.debug("MD5 sum is '%s'"% self._md5)
        return self._md5

    def match(self, filepath):
        if not os.path.isfile(filepath):
            return False
        f = open(filepath)
        saved_md5 = hashlib.md5(f.read()).hexdigest()
        f.close()
        result = saved_md5 == self._md5
        LOGGER.debug("saved schema is current? %s"% result)
        return result

    def write(self, filepath):
        LOGGER.info("writing sql to %s"% filepath)
        f = open(filepath, "w")
        f.write(self.CURRENT_SQL)
        f.close()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    s = SchemaManager()
    s.MD5
    FILEPATH = "../../../../misc/server/blank_schema.sql"
    if not s.match(FILEPATH):
        s.write(FILEPATH)
