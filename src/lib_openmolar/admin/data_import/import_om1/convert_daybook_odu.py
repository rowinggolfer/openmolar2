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

ALLTYPES = "(SR)|(CC)|(SS)|(CC SKM)"

def convert(line):
    line = line.strip(" &")

    part_handled = False

    if " RL" in line:
        code = ImportCode("H71")
        yield code
        part_handled = True

    if " SL" in line:
        code = ImportCode("H71")
        yield code
        part_handled = True

    if line == "":
        pass

    elif line == "2863":
        #tooth additions
        yield ImportCode("H60")

    elif line == "2801":
        #repair
        yield ImportCode("H66")

    elif line == "2831":
        #adjust
        yield ImportCode("H65")

    elif line == "2851":
        #reline
        yield ImportCode("H71")

    elif line == "2851 2861":
        #reline
        yield ImportCode("H71")
        yield ImportCode("H61")

    elif line == "2861" or line == "2861 2861":
        #addition of clasp
        yield ImportCode("H61")

    elif line == "2871":
        # a "maximum" fee - irrelevant
        pass

    elif re.match("%s A/T/"% ALLTYPES, line):
        #"teeth additions"
        code = ImportCode("H60")
        code.pontics = get_teeth(line)
        yield code

    elif re.match("%s R/(\d)?G"% ALLTYPES, line):
        #"repair"
        code = ImportCode("H66")
        yield code

    elif re.match("%s ADJ"% ALLTYPES, line):
        #"teeth additions"
        code = ImportCode("H65")
        yield code

    else:
        if not part_handled:
            print "UNMATCHED", line
            code = ImportCode("Z00")
            yield code

if __name__ == "__main__":
    f = open("/home/neil/Desktop/adp_import/distinct_odu.txt","r")
    for line in f.readlines():
        if not line.startswith("#"):
            for code in convert(line.strip()):
                print code, code.pontics, line.strip()
    f.close()