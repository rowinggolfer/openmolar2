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


EXCEL_MESSAGE='''Error importing support for writing MicroSoft Excel Files
if you need this functionality, visit http://pypi.python.org/pypi/xlutils
and install the package'''

try:
    import xlwt
    AVAILABLE = True
except ImportError as e:
    print EXCEL_MESSAGE
    AVAILABLE = False

from tempfile import TemporaryFile
import types, datetime

from PyQt4 import QtCore


class XLS_Writer(object):
    def __init__(self, filename):
        self.filename = filename
        self.book = xlwt.Workbook()
        self.sheets = {}
        self.add_sheet()

        self.date_style = xlwt.easyxf(num_format_str="MMMM DD, YYYY")
        self.time_style = xlwt.easyxf(num_format_str="HH:MM")
        self.datetime_style = xlwt.easyxf(num_format_str="HH:MM MMMM DD, YYYY")
        #self.current_sheet.col(1).set_style(style)


    def add_sheet(self, sheetname = ""):
        sheet_no = len(self.sheets)+1
        if not sheetname:
            sheetname = "Sheet %d"% sheet_no

        new_sheet = self.book.add_sheet(sheetname)
        self.current_sheet = new_sheet
        self.sheets[sheet_no] = new_sheet

        self.current_rowno = 0

    def save(self):
        self.book.save(self.filename)
        self.book.save(TemporaryFile())

    def writerow(self, row):
        write_list = [] # a list of values, types
        for val in row:
            style = None
            if type(val) in types.StringTypes:
                val = unicode(val)
            elif type(val) == datetime.date:
                style = self.date_style
            elif type(val) == QtCore.QVariant:
                if val.type() == QtCore.QVariant.Int:
                    val = val.toInt()[0]
                elif val.type() == QtCore.QVariant.Date:
                    val = val.toDate().toPyDate()
                    style = self.date_style
                elif val.type() == QtCore.QVariant.Time:
                    val = val.toDateTime().toPyTime()
                    style = self.time_style
                elif val.type() == QtCore.QVariant.DateTime:
                    val = val.toDateTime().toPyDateTime()
                    style = self.datetime_style
                else:
                    val = unicode(val.toString())

            else:
                val = unicode(val)

            write_list.append((val, style))

        colno = 0
        for item, style in write_list:
            newrow = self.current_sheet.row(self.current_rowno)
            print item
            if not style:
                newrow.write(colno, item)
            else:
                newrow.write(colno, item, style)

            colno += 1

        self.current_rowno += 1

    def write_model(self, model):
        s_list = [] #QtCore.QStringList()
        for col_no in range(model.columnCount()):
            item = model.headerData(col_no, QtCore.Qt.Horizontal)
            s_list.append(item.toString())
        self.writerow(s_list)

        for row_no in range(model.rowCount()):
            s_list = []#  QtCore.QStringList()
            for col_no in range(model.columnCount()):
                index = model.index(row_no, col_no)
                item = model.data(index)
                s_list.append(item)
            self.writerow(s_list)
        self.save()

if __name__ == "__main__":
    from datetime import date

    rows = (
        ("Neil",date(2009,12,9)),
        ("Bea",date(1970,3,8)),
        ("Iona",date(1998,3,11)),
        ("Fraser", date(2000,11,10))
        )

    filename = "/home/neil/Desktop/test.xls"
    writer = XLS_Writer(filename)
    for row in rows:
        writer.writerow(row)
    writer.save()
