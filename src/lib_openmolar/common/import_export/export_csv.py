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

import csv, cStringIO, types, datetime
from PyQt4 import QtCore


class CSV_Writer(object):
    def __init__(self, f, **kwds):
        self.writer = csv.writer(f,
            quoting = csv.QUOTE_MINIMAL, dialect=csv.excel, **kwds)

    def writerow(self, row):
        write_list = []
        for s in row:
            if type(s) in types.StringTypes:
                write_list.append(s)
            elif type(s) == datetime.date:
                write_list.append(s)
            elif type(s) == QtCore.QVariant:
                if s.type() == QtCore.QVariant.Int:
                    write_list.append(s.toInt()[0])
                elif s.type() == QtCore.QVariant.Date:
                    write_list.append(s.toDate().toPyDate())
                elif s.type() == QtCore.QVariant.DateTime:
                    write_list.append(s.toDateTime().toPyDateTime())
                else:
                    write_list.append(s.toString())
            else:
                write_list.append(None)
        self.writer.writerow(write_list)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

    def write_model(self, model):
        s_list = [] #QtCore.QStringList()
        for col_no in range(model.columnCount()):
            item = model.headerData(col_no, QtCore.Qt.Horizontal)
            s_list.append(item.toString())
        self.writer.writerow(s_list)

        for row_no in range(model.rowCount()):
            s_list = []#  QtCore.QStringList()
            for col_no in range(model.columnCount()):
                index = model.index(row_no, col_no)
                item = model.data(index)
                s_list.append(item)
            self.writerow(s_list)

if __name__ == "__main__":
    from datetime import date

    l = (
        ("Neil",date(2009,12,9)),
        ("Bea",date(1970,3,8)),
        ("Iona",date(1998,3,11)),
        ("Fraser", QtCore.QVariant(QtCore.QDate(2000,11,10)))
        )

    f = open("/home/neil/Desktop/test.csv", "wb")
    writer = CSV_Writer(f, delimiter='|')
    writer.writerows(l)
    f.close()
