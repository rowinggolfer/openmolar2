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
This module provides the Address Class
'''

from random import randint

from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "addresses"

LINE1s = (u"18 Main Street", u"22 Union Street", u"38, The Hope", u"Asgard",
u"The Gables", u"1058 Rue de la Soleil", u"23 Queen Street", u"The Cottage",
u"The Old Barn", u"The Kennels")

LINE2s = (u"Snoddith", u"Little Crumpet", u"Underberg", u"Laphroig",
u"Port Soy", u"Tampa", u"ShoreHampton", u"Cricket",
u"NeverField", u"Drone")

CITIES = (  (u"Inverness", "IV"),
            (u"Edinburgh", "E"),
            (u"Aberdeen", "AB"),
            (u"Dundee", "DD"),
            (u"Perth", "PH"),
            (u"Aviemore", "IV"),
            (u"Stornoway", "IV"),
            (u"Fort William", "IV"),
            (u"Kircudbright", "KK") )

def random_addy():
    addr1 = LINE1s[randint(0,len(LINE1s)-1)]
    addr2 = LINE2s[randint(0,len(LINE1s)-1)]
    city, pcde = CITIES[randint(0,len(CITIES)-1)]
    pcde = u"%s%d %d%s%s"% (pcde, randint(1,50), randint(1,9),
        chr(randint(65, 90)), chr(randint(65, 90)))

    return (addr1.upper(), addr2.upper(), city.upper(), pcde.upper())


class DemoGenerator(object):
    def __init__(self, database):
        self.database = database
        self.length = 40
        self.record = InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf("time_stamp"))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        for i in xrange(self.length):
            self.record.clearValues()

            addr1, addr2, city, pcde = random_addy()
            self.record.setValue('addr1', addr1)
            self.record.setValue('addr2', addr2)
            self.record.setValue('city', city)
            self.record.setValue('postal_cd', pcde)
            self.record.setValue('modified_by', 'demo')

            yield self.record.insert_query


if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries().next()
