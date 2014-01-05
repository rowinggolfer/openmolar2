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
this module provides one class, ProcCode

ProcCode is a class which encapsulates a treatment procedure known to openmolar

as an example, such an object may represent a 3 surface amalgam filling.

this only becomes a treatment item, when it is planned or performed on a
specific tooth on a specific patient.
'''

from xml.dom import minidom
import re

from lib_openmolar.common.qt4 import qrc_resources
from PyQt4 import QtCore
from proc_code import ProcCode

class ProcedureCodes(object):
    '''
    this dictionary like object stores all the hard-coded treatment codes
    note - this is wrapped in a decorator to ensure only one instance of
    this class exists
    '''
    def __init__(self):
        self._list = []
        self._cats = []
        self._regex_dict = {}

        f = QtCore.QFile(":proc_codes/om2_codes.xml")
        f.open(QtCore.QIODevice.ReadOnly)
        xml_string = str(f.readAll().data())
        f.close()
        dom = minidom.parseString(xml_string)

        cat_no = 0
        for category in dom.getElementsByTagName("Category"):
            cat = category.attributes["name"].value.strip()
            try:
                cat_no = self._cats.index(cat)
            except ValueError:
                self._cats.append(cat)
                cat_no = self._cats.index(cat)

            for element in category.getElementsByTagName("Code"):
                proc_code = ProcCode(element, cat)
                proc_code.cat_no = cat_no + 1
                self._list.append(proc_code)

                for shortcuts in element.getElementsByTagName("shortcut"):
                    shortcut = shortcuts.childNodes[0].data
                    regex = re.compile(shortcut)
                    self._regex_dict[regex] = proc_code.code

    @property
    def exam_codes(self):
        for item in self:
            if item.cat_no == 1:
                yield item

    @property
    def xray_codes(self):
        for item in self:
            if item.cat_no == 2:
                yield item

    @property
    def hyg_codes(self):
        for item in self:
            if item.cat_no == 3:
                yield item

    @property
    def crown_codes(self):
        for item in self:
            if item.cat_no == 6:
                yield item

    @property
    def CATEGORIES(self):
        return self._cats

    def convert_user_shortcut(self, user_input):
        '''
        takes a user shortcut eg. MOD,AM.. and finds an OM code (if it exists!)
        '''
        code = None
        for key in self._regex_dict:  #keys are pre-compiled regexes
            if key.match(user_input):
                code = self._regex_dict[key]
                break
        if code:
            for proc_code in self:
                if proc_code.code == code:
                    return proc_code

    def find_code(self, code):
        '''
        searches to find a code - returns "other treatment" if it can't!
        '''
        for proc_code in self:
            if proc_code.code == code:
                return proc_code

        return self.find_code("Z00")

    def __getitem__(self, key):
        '''
        convenience function to allow this object to act like a dictionary
        '''
        return self.find_code(key)

    def __iter__(self):
        for code in self._list:
            yield code

    def __len__(self):
        return len(self._list)

def test_main():
    def get_result():
        user_input = str(le.text().toAscii().toUpper())

        if user_input == "EXIT":
            app.closeAllWindows()

        proc_code = procedure_codes.convert_user_shortcut(user_input)
        result_label.setText("%s"% proc_code)

    from PyQt4 import QtGui
    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    label = QtGui.QLabel("test the procedure codes\n"
    "enter a user shortcut (eg. MOD,AM) or 'exit' to quit~$ ")

    le = QtGui.QLineEdit()

    result_label = QtGui.QLabel("")

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(label)
    layout.addWidget(le)
    layout.addWidget(result_label)

    le.returnPressed.connect(get_result)

    dl.show()
    app.exec_()


def _singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@_singleton
class ProcedureCodesInstance(ProcedureCodes):
    pass

if __name__ == "__main__":
    procedure_codes = ProcedureCodesInstance()
    for code in procedure_codes:
        print code

    #for code in procedure_codes.exam_codes:
    #    print code

    if True:
        test_main()
