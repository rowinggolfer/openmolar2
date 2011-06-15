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

def decode(line):
    if "ST" in line or "2771" in line:
        #print "special tray", line
        yield ("special tray", True)
    if "SL" in line:
        #print "soft lining", line
        yield ("soft lining", True)
    if "ID" in line:
        #print "ID", line
        yield ("ID insert", line)

    if line in ("2771",):
        pass #already handled
    elif re.match("SR P/([LR][1-8]*),?([LR][1-8]*)?", line):
        yield ("resin partial", True)
    elif re.match("SR P", line):
        yield ("resin partial", True)
    elif re.match("=?OCCL", line):
        yield ("occlusal appliance", True)
    elif re.match("SS(/PL)? P/([LR][1-8]*),?([LR][1-8]*)?", line):
        yield ("resin partial", True)
    elif re.match("CC/SKM? P/([LR][1-8]*),?([LR][1-8]*)?", line):
        yield ("chrome partial", True)
    elif re.match("CC/PL P/([LR][1-8]*),?([LR][1-8]*)?", line):
        yield ("chrome partial", True)
    elif re.match("274[345]", line):
        yield ("chrome partial", True)
    elif re.match("SR F", line) or re.search("2731", line):
        yield ("Full Acrylic", True)
    elif re.match("SS F", line) or re.match("CC F", line):
        yield ("Full Metal", True)
    elif re.match("SPL/C (\d)U", line):
        yield ("Composite Splint %s teeth"% re.match(
            "SPL/C (\d)U", line).groups()[0], True)
    elif re.match("SPL/O", line):
        yield ("Other Splint", True)
    elif re.match("OA", line):
        yield ("Other Appliance", True)
    else:
        yield ("unknown", False)

if __name__ == "__main__":
    f = open("/home/neil/Desktop/adp_import/distinct_ndl.txt","r")
    bad_count = 0
    for line in f.readlines():
        if not line.startswith("#"):
            for converted, result in decode(line.strip()):
                if not result:
                    print line,
                    bad_count += 1

    f.close()

    print "%d items unknown"% bad_count