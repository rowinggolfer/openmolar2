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
Provides a DemoGenerator for the patients table
'''

from PyQt4 import QtCore, QtSql
from random import randint

from lib_openmolar.common.db_orm import InsertableRecord

TABLENAME = "patients"

class DemoGenerator(object):
    def __init__(self, database):
        self.length = 61

        self.record = InsertableRecord(database, TABLENAME)
        self.record.remove(self.record.indexOf("time_stamp"))

    def demo_queries(self):
        '''
        return a list of queries to populate a demo database
        '''
        for name in (u"MISS HANNAH ABBOTT",
        u"MISS BATHILDA BAGSHOT", u"MISS KATIE BELL",
        u"MISS SUSAN BONES",
        u"MISS MANDY BROCKLEHURST", u"MISS LAVENDER BROWN",
        u"MISS MILLICENT BULSTRODE",
        u"MISS DORIS CROCKFORD",
        u"MRS PETUNIA DURSLEY",
        u"THE FAT LADY",
        u"MISS MIRANDA GOSHAWK",
        u"MISS HERMIONE GRAINGER",
        u"MISS ANGELINA JOHNSON",
        u"PROFESSOR MINERVA MCGONAGALL",
        u"MRS LILY POTTER",
        u"MISS ALICIA SPINNET", u"MISS PHYLLIDA SPORE",
        u"MISS EMERIC SWITCH",
        u"MISS LISA TURPIN", u"MISS GINNY WEASLEY",
        u"MRS MOLLY WEASLEY", u"MISS BLAISE ZABINI"):
            self.record.clearValues()
            title, fname, sname = name.split(" ")
            self.record.setValue("title", title)
            self.record.setValue("first_name", fname)
            self.record.setValue("last_name", sname)
            self.record.setValue("sex", 'F')
            dob = QtCore.QDate(randint(1930,2010), randint(1,12), randint(1,28))
            self.record.setValue("dob", dob)
            self.record.setValue("status", "active")
            if name in ("MRS LILY POTTER"):
                self.record.setValue("status", "deceased")
            self.record.setValue("modified_by", "demo_installer")

            yield self.record.insert_query


        for name in (u"MR SIRIUS BLACK",
        u"MR BLOODY BARON", u"MR TERRY BOOT",
        u"MR VINCENT CRABBE",
        u"MR DEDALUS DIGGLE",
        u"PROFESSOR ALBUS DUMBLEDORE", u"MR DUDLEY DURSLEY",
        u"MR VERNON DURSLEY",
        u"THE FAT FRIAR",
        u"MR ARGUS FILCH", u"MR JUSTIN FINCH-FLETCHLEY", u"MR SEAMUS FINNIGAN",
        u"MR NICOLAS FLAMEL", u"MR MARCUS FLINT",
        u"MR CORNELIUS FUDGE", u"MR GREGORY GOYLE",
        u"PROFESSOR RUBEUS HAGRID", u"MR TERENCE HIGGS",
        u"MR ARSENIUS JIGGER",
        u"MR DRACO MALFOY",
        u"MR NEVILLE LONGBOTTOM", u"MR NEARLY-HEADLESS NICK",
        u"MR PIERS POLKISS",
        u"MR HARRY POTTER", u"MR JAMES POTTER", u"MR ADRIAN PUCEY",
        u"PROFESSOR SEVERUS SNAPE", u"MR DEAN THOMAS", u"MR TOM THE-BARTENDER",
        u"MR QUENTIN TRIMBLE",
        u"MR VINDICTUS VIRIDIAN",
        u"MR ADALBERT WAFFLING", u"MR ARTHUR WEASLEY", u"MR BILL WEASLEY",
        u"MR CHARLIE WEASLEY",
        u"MR FRED WEASLEY", u"MR GEORGE WEASLEY",
        u"MR PERCY WEASLEY", u"MR RON WEASLEY",
        u"MR OLIVER WOOD"):
            self.record.clearValues()
            title, fname, sname = name.split(" ")
            self.record.setValue("title", title)
            self.record.setValue("first_name", fname)
            self.record.setValue("last_name", sname)
            self.record.setValue("sex", 'M')
            dob = QtCore.QDate(randint(1930,2010), randint(1,12), randint(1,28))
            self.record.setValue("dob", dob)
            self.record.setValue("status", "active")
            if name in ("PROFESSOR ALBUS DUMBLEDORE", 'MR JAMES POTTER'):
                self.record.setValue("status", "deceased")
            self.record.setValue("modified_by", "demo_installer")

            yield self.record.insert_query


if __name__ == "__main__":
    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    builder = DemoGenerator(sc)
    print builder.demo_queries().next()
