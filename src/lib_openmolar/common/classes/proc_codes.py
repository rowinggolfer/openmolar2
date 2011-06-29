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
this module provides one class, ProcCode

ProcCode is a class which encapsulates a treatment procedure known to openmolar

as an example, such an object may represent a 3 surface amalgam filling.

this only becomes a treatment item, when it is planned or performed on a
specific tooth on a specific patient.
'''

import re
from lib_openmolar.common import qrc_resources
from PyQt4 import QtCore

class ProcCode(object):
    #:
    SIMPLE = 0
    #:
    TOOTH = 1
    #:
    ROOT = 2
    #:
    FILL = 3
    #:
    CROWN = 4
    #:
    BRIDGE = 5
    #:
    PROSTHETICS = 6
    #:
    OTHER = 7

    def __init__(self, cat, cat_no):
        #:
        self.cat_no = cat_no
        #:
        self.category = cat.strip()

        #:
        self.type = self.SIMPLE

        #:
        self.code = None

        self._description_required = False

        #:
        self.description = ""

        self._surfaces_required = False
        self._multi_teeth = False
        self._pontics_required = False
        self._no_pontics = 0
        self._no_surfaces = ""
        self._total_span = "0"
        self._allowed_pontics = None

    @property
    def is_fill(self):
        return self.type == self.FILL

    @property
    def is_crown(self):
        return self.type == self.CROWN

    @property
    def is_root(self):
        return self.type == self.ROOT

    @property
    def is_tooth(self):
        return (
            self.is_bridge or
            self.is_crown or
            self.is_fill or
            self.is_root or
            self.type == self.TOOTH
            )

    @property
    def is_bridge(self):
        return self.type == self.BRIDGE

    @property
    def is_prosthetics(self):
        return self.type == self.PROSTHETICS

    @property
    def description_required(self):
        return self._description_required

    @property
    def tooth_required(self):
        '''
        this is a property indicating that to become a treatment item
        a tooth is required.
        this is, for example, the case with an MOD filling,
        but not needed for an examination
        '''
        return self.is_tooth

    @property
    def surfaces_required(self):
        return self._surfaces_required

    @property
    def no_surfaces(self):
        return self._no_surfaces

    @property
    def multi_tooth(self):
        return self._multi_teeth

    @property
    def pontics_required(self):
        return self._pontics_required

    @property
    def allowed_pontics(self):
        '''
        a list of teeth which can be replaced with this procedure
        (eg upper teeth only for a P/-)
        '''
        if self._allowed_pontics != None:
            return self._allowed_pontics
        return SETTINGS.all_teeth

    @property
    def no_pontics(self):
        return self._no_pontics

    @property
    def total_span(self):
        if self.is_bridge:
            return self._total_span

    def parse(self, line):
        try:
            vals = line.split("|")

            if vals[0] in ("tooth", "teeth"):
                self.type = self.TOOTH
                if vals[0] == "teeth":
                    self._multi_teeth = True
            elif vals[0] == "root":
                self.type = self.ROOT
            elif vals[0] == "fill":
                self.type = self.FILL
            elif vals[0] == "crown":
                self.type = self.CROWN
            elif vals[0] == "prosthetics":
                self.type = self.PROSTHETICS
            elif vals[0] == "bridge":
                self.type = self.BRIDGE
            elif vals[0] == "simple":
                pass #already the default
            else:
                print "WARNING - illegal proc-code type", vals

            self.code = vals[1].strip()
            self.description = unicode(vals[2])
            try:
                self.parse_info_list(vals[3])
            except IndexError:
                pass
        except IndexError:
                return False
        return True

    def parse_info_list(self, info):
        self._description_required = "description" in info

        if self.type == self.SIMPLE:
            return

        info_list = info.split(",")

        for item in info_list:
            if item.startswith("abutments"):
                self._tooth_required = True
            elif item.startswith("pontics"):
                self.parse_pontic_item(item)
            elif re.search("total\(\d+\)", item):
                self._total_span = re.search("\d+\+?", item).group()
            elif item == "description":
                self.get_description = True
            elif re.match("surfaces\(\d+\+?\)", item):
                self._surfaces_required = True
                self._no_surfaces = re.search("\d+\+?", item).group()

    @property
    def material(self):
        if "amalgam" in self.description.lower():
            return "amalgam"
        if "composite" in self.description.lower():
            return "composite"
        if "gold" in self.description.lower():
            return "gold"
        if "glass" in self.description.lower():
            return "glass"
        return "unknown"
            

    @property
    def further_info_needed(self):
        return (self.tooth_required or
            self.surfaces_required or
            self.description_required or
            self.pontics_required)

    def parse_teeth_item(self, item):
        range_value = re.search("\{tooth_range\((\d+)\.\.(\d+)\)\}", item)
        if range_value:
            start, finish = range_value.groups()
            self.allowed_teeth = range(int(start), int(finish))

    def parse_pontic_item(self, item):
        range_value = re.search("\{tooth_range\((\d+)\.\.(\d+)\)\}", item)
        if range_value:
            start, finish = range_value.groups()
            self._allowed_pontics = range(int(start), int(finish))

        if re.match("pontics\(\d+", item):
            self._no_pontics = re.search("\((\d+\+?)\)", item).groups()[0]

        self._pontics_required = True

    def __repr__(self):
        return "ProcCode - %s"% self.__str__()

    def __str__(self):
        return  u"%s %s %s"% (
            self.category.ljust(28), self.code, self.description)

    def __cmp__(self, other):
        try:
            return cmp(self.code, other.code)
        except AttributeError as e:
            return -1

class ProcedureCodes(object):
    '''
    this dictionary like object stores all the hard-coded treatment codes
    note - this is wrapped in a decorator to ensure only one instance of
    this class exists
    '''
    def __init__(self):
        self._list = []
        self._cats = []

        f = QtCore.QFile(":proc_codes/om2_codes.txt")
        f.open(QtCore.QIODevice.ReadOnly)
        cat, cat_no = "", 0
        line = f.readLineData(255)
        while line:
            line = line.strip()
            vals = line.split("|")
            if line == "" or line.startswith("#"):
                pass
            elif line.startswith("--"):
                cat_no += 1
                vals = line.split("|")
                cat = vals[1]
                self._cats.append(cat)
            else:
                proc_code = ProcCode(cat, cat_no)

                if proc_code.parse(line):
                    self._list.append(proc_code)

            line = f.readLineData(255)

        f.close()

        reg_file = ":proc_codes/om2_code_regex.txt"
        f = QtCore.QFile(reg_file)
        f.open(QtCore.QIODevice.ReadOnly)
        line = f.readLineData(255)
        self._regex_dict = {}
        self._charting_dict = {}
        i = 1
        while line:
            line = line.strip()
            if line == "" or line.startswith("#"):
                pass
            else:
                try:
                    code, reg_code = line.strip("\n").split("|")
                    key = re.compile(reg_code)
                    self._regex_dict[key] = code
                    self._charting_dict[code] = reg_code
                except ValueError:
                    print "unsplittable line  - line %d, %s"% (i, reg_file)
                except Exception:
                    print "??regex compile error - line %d, %s"% (i, reg_file)
            i += 1
            line = f.readLineData(255)
        f.close()

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

    def convert_to_user_shortcut(self, code):
        '''
        take a code a return the shortcut eg. CR,V1
        '''
        return QtCore.QString(self._charting_dict.get(code.code))

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

        if proc_code:
            print "which converts back as",
            print procedure_codes.convert_to_user_shortcut(proc_code)


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

    test_main()

    while False:
        print "=" * 40
        user_input = raw_input(
        "enter a user shortcut (eg. MOD,AM) or 'exit' to quit~$ ").upper()

        if user_input == "EXIT":
            print "GOODBYE!"
            break

        proc_code = procedure_codes.convert_user_shortcut(user_input)
        print "returns proc code - ", proc_code
        print "which converts back as",
        print procedure_codes.convert_to_user_shortcut(proc_code)

        print "=" * 40


