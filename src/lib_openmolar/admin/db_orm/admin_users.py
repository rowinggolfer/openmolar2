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
Provides a DemoGenerator for the users table
'''

from PyQt4 import QtCore

from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "users"

class DemoGenerator(object):
    def __init__(self, database=None):
        self.length = 4

        self.record = InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf("time_stamp"))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        ## practitioner 1
        self.record.setValue('title', "Dr.")
        self.record.setValue('last_name',"McCavity")
        self.record.setValue('first_name',"Phil")
        self.record.setValue('full_name', "Dr. McCavity")
        self.record.setValue('abbrv_name',"PM")
        self.record.setValue('sex', "M")
        self.record.setValue('role',"dentist")
        self.record.setValue('dob',QtCore.QDate(1969,12,9))
        self.record.setValue('qualifications', "BDS, LDS")
        self.record.setValue('status', "active")
        self.record.setValue('modified_by', "demo_installer")
        self.record.setValue('avatar_id', 1)

        yield self.record.insert_query
        self.record.clearValues()

        ## practitioner 2
        self.record.setValue('title', "Mr.")
        self.record.setValue('last_name',"AllOut")
        self.record.setValue('first_name',"Rippem")
        self.record.setValue('full_name', "Mr Rippem AllOut")
        self.record.setValue('abbrv_name',"RA")
        self.record.setValue('sex', "M")
        self.record.setValue('role',"dentist")
        self.record.setValue('dob',QtCore.QDate(1988,11,10))
        self.record.setValue('qualifications', "BDS")
        self.record.setValue('status', "active")
        self.record.setValue('modified_by', "demo_installer")
        self.record.setValue('avatar_id', 2)

        yield self.record.insert_query
        self.record.clearValues()

        ## practitioner 3
        self.record.setValue('title', "Miss")
        self.record.setValue('last_name',"Straight")
        self.record.setValue('first_name',"Muzby")
        self.record.setValue('full_name', "Miss Muzby Straight")
        self.record.setValue('abbrv_name',"MS")
        self.record.setValue('role',"dentist")
        self.record.setValue('sex', "F")
        self.record.setValue('dob',QtCore.QDate(1990,3,10))
        self.record.setValue('qualifications', "BDS, DipOrth")
        self.record.setValue('status', "active")
        self.record.setValue('modified_by', "demo_installer")
        self.record.setValue('avatar_id', 3)

        yield self.record.insert_query
        self.record.clearValues()

        ## practitioner 4
        self.record.setValue('title', "Miss")
        self.record.setValue('last_name',"Clean")
        self.record.setValue('first_name',"Crystal")
        self.record.setValue('full_name', "Miss Clean")
        self.record.setValue('abbrv_name',"CC")
        self.record.setValue('sex', "F")
        self.record.setValue('role',"hygienist")
        self.record.setValue('dob',QtCore.QDate(1992,12,9))
        self.record.setValue('qualifications', "MRCH")
        self.record.setValue('status', "active")
        self.record.setValue('modified_by', "demo_installer")
        self.record.setValue('avatar_id', 4)

        yield self.record.insert_query

        ## practitioner 1
        self.record.clearValues()
        self.record.setValue('title', "Miss")
        self.record.setValue('last_name',"Smith")
        self.record.setValue('first_name',"Jane")
        self.record.setValue('abbrv_name',"JS")
        self.record.setValue('sex', "F")
        self.record.setValue('dob',QtCore.QDate(1969,12,9))
        self.record.setValue('qualifications', "")
        self.record.setValue('role', "receptionist")
        self.record.setValue('status', "active")
        self.record.setValue('modified_by', "demo_installer")
        self.record.setValue('avatar_id', 6)
        yield self.record.insert_query

        self.record.clearValues()
        self.record.setValue('title', "Miss")
        self.record.setValue('last_name',"Jones")
        self.record.setValue('first_name',"Emma")
        self.record.setValue('abbrv_name',"EJ")
        self.record.setValue('sex', "F")
        self.record.setValue('dob',QtCore.QDate(1969,12,9))
        self.record.setValue('qualifications', "")
        self.record.setValue('role', "nurse")
        self.record.setValue('status', "active")
        self.record.setValue('modified_by', "demo_installer")
        self.record.setValue('avatar_id', 8)
        yield self.record.insert_query

        self.record.clearValues()
        self.record.setValue('title', "Mr")
        self.record.setValue('last_name',"Baipusi")
        self.record.setValue('first_name',"Mawimba")
        self.record.setValue('abbrv_name',"MB")
        self.record.setValue('sex', "M")
        self.record.setValue('dob',QtCore.QDate(1969,12,9))
        self.record.setValue('qualifications', "")
        self.record.setValue('role', "nurse")
        self.record.setValue('status', "active")
        self.record.setValue('modified_by', "demo_installer")
        self.record.setValue('avatar_id', 5)
        yield self.record.insert_query

        self.record.clearValues()
        self.record.setValue('title', "Mr")
        self.record.setValue('last_name',"Andrews")
        self.record.setValue('first_name',"Jim")
        self.record.setValue('abbrv_name',"JA")
        self.record.setValue('sex', "M")
        self.record.setValue('dob',QtCore.QDate(1969,12,9))
        self.record.setValue('qualifications', "")
        self.record.setValue('role', "nurse")
        self.record.setValue('status', "active")
        self.record.setValue('modified_by', "demo_installer")
        self.record.setValue('avatar_id', 9)
        yield self.record.insert_query

        self.record.clearValues()
        self.record.setValue('title', "Mrs")
        self.record.setValue('last_name',"Smart")
        self.record.setValue('first_name',"Julie")
        self.record.setValue('abbrv_name',"Jules")
        self.record.setValue('sex', "F")
        self.record.setValue('dob',QtCore.QDate(1969,12,9))
        self.record.setValue('qualifications', "")
        self.record.setValue('role', "nurse")
        self.record.setValue('status', "active")
        self.record.setValue('modified_by', "demo_installer")
        self.record.setValue('avatar_id', 7)
        yield self.record.insert_query

if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries().next()
