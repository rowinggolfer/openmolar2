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

import re
from convert_daybook import ImportCode

RIGHT_TEETHMAP = {"8":1,"7":2,"6":3,"5":4,"4":5,"3":6,"2":7,"1":8}
LEFT_TEETHMAP = {"8":16,"7":15,"6":14,"5":13,"4":12,"3":11,"2":10,"1":9}

class Pontic(object):
    type = "pontic"
    def __init__(self, tooth, rhs=True):
        if rhs:
            self.tooth = RIGHT_TEETHMAP[tooth]
        else:
            self.tooth = LEFT_TEETHMAP[tooth]

    def __eq__(self, other):
        return cmp(self.tooth, other.tooth)

    def __repr__(self):
        return "%s %s"% (self.type, self.tooth)


def get_teeth(line):
    teeth = set([])
    m=re.search("P/(R\d*)?,?(L\d*)?", line)
    if m:
        for i, rhs in enumerate((True, False)):
            if m.groups()[i] is not None:
                #uppper right teeth found
                for tooth in m.groups()[i][1:]:
                    pontic = Pontic(tooth, rhs)
                    teeth.add(pontic)

    return sorted(teeth)

def convert(line):
    line = line.strip(" ")

    part_handled = False

    if "ST" in line or "2771" in line:
        code = ImportCode("H90")
        code.description = "upper"
        yield code
        part_handled = True

    if "SL" in line:
        code = ImportCode("H70")
        code.description = "upper"
        yield code
        part_handled = True

    if "ID" in line:
        code = ImportCode("H72")
        code.description = "upper"
        yield code
        part_handled = True

    if line == "":
        pass

    elif re.match("SR P/([LR][1-8]*),?([LR][1-8]*)?", line):
        #"resin partial"
        code = ImportCode("H20")
        code.pontics = get_teeth(line)
        yield code

    elif re.match("SR P", line):
        #"resin partial"
        code = ImportCode("H20")
        code.description = "NDU: %s"% line
        yield code

    elif re.match("=?OCCL", line):
        #"occlusal appliance"
        code = ImportCode("Z00")
        code.description = "NDU: %s"% line
        yield code


    elif re.match("SS(/PL)? P/([LR][1-8]*),?([LR][1-8]*)?", line):
        #"metal partial"
        code = ImportCode("H30")
        code.pontics = get_teeth(line)
        code.description = "NDU: %s"% line
        yield code

    elif re.match("CC/SKM? P/([LR][1-8]*),?([LR][1-8]*)?", line):
        #"chrome partial"
        code = ImportCode("H30")
        code.pontics = get_teeth(line)
        code.description = "NDU: %s"% line
        yield code

    elif re.match("CC/PL P/([LR][1-8]*),?([LR][1-8]*)?", line):
        #"chrome partial"
        code = ImportCode("H30")
        code.pontics = get_teeth(line)
        code.description = "NDU: %s"% line
        yield code

    elif re.match("274[345]", line):
        #"metal partial"
        code = ImportCode("H30")
        code.description = "NDU: %s"% line
        yield code

    elif re.match("SR F", line) or re.search("2731", line):
        #"metal partial"
        code = ImportCode("H01")
        code.description = "NDU: %s"% line
        yield code

    elif re.match("SS F", line) or re.match("CC F", line):
        #full metal
        code = ImportCode("H11")
        code.description = "NDU: %s"% line
        yield code

    elif re.match("SPL/C (\d)U", line):
        #"Composite Splint %s teeth"%
        #re.match("SPL/C (\d)U", line).groups()[0], True)
        code = ImportCode("C30")
        code.description = "NDU: %s"% line
        yield code

    elif re.match("SPL/O", line):
        code = ImportCode("Z00")
        code.description = "NDU (SPLINT?): %s"% line
        yield code

    elif re.match("OA", line):
        code = ImportCode("Z00")
        code.description = "NDU: %s"% line
        yield code

    else:
        if not part_handled:
            print "UNMATCHED", line
            code = ImportCode("Z00")
            yield code

if __name__ == "__main__":
    f = open("/home/neil/Desktop/adp_import/distinct_ndu.txt","r")
    for line in f.readlines():
        if not line.startswith("#"):
            for code in convert(line.strip()):
                print code, code.pontics, line.strip()
    f.close()
