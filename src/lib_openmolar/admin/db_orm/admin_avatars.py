#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
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
This module inserts demo avatars into the database
'''

from PyQt4 import QtCore
from lib_openmolar.admin import qrc_resources

from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "avatars"

class DemoGenerator(object):
    def __init__(self, database=None):
        self.length = 6

        self.record = InsertableRecord(database, TABLENAME)

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        for avatar in ( "demo_neil.svg",
                        "demo_andi.svg",
                        "demo_blondie.svg",
                        "demo_helen.svg",
                        "demo_me.svg",
                        "demo_nattress.svg",
                        "demo_iceman.svg",
                        "demo_frog.svg",
                        "demo_jellyman.svg",
                        "demo_lucy.svg",
                        "demo_negro.svg",
                        "demo_ja.svg",
                        "demo_sally.svg"
                        ):
            f = QtCore.QFile(":avatars/%s"% avatar)
            f.open(QtCore.QIODevice.ReadOnly)
            ts = QtCore.QTextStream(f)

            self.record.clearValues()
            self.record.setValue("svg_data", ts.readAll())
            self.record.setValue("description", avatar)

            f.close()

            yield self.record.insert_query

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries().next()
