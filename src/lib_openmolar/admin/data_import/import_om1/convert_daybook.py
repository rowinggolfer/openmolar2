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

# a list of default materials
FILL_MATERIALS = {
"D01":"AM",
"D02":"AM",
"D03":"AM",
"D04":"AM",
"D10":"CO",
"D11":"CO",
"D12":"CO",
"D13":"CO",
"D20":"GL",
"D21":"GL",
"D30":"OT",
"D31":"OT",
"D32":"OT",
"D33":"OT",
"D40":"PR",
"D50":"CO",
"D51":"CO",
"G10":"GO",
"G11":"GO",
"G20":"PO",
"G21":"PO",
"G30":"CO",
"G31":"CO",
}



class ImportCode(object):
    def __init__(self, code, tooth=None):
        self.code = code
        self.tooth = tooth
        self.pontics = []
        self.surfaces = ""
        self.description = ""
        self.tooth_tx_type = None

    def setSurfaces(self, surfaces):
        surf = surfaces.replace("I","O")
        surf = surf.replace("P","L")

        if not re.match("[MODBL]{1,5}$", surf) or len(set(surf)) != len(surf):
            print "INVALID SURFACES", surfaces
        else:
            self.surfaces = surf

    @property
    def is_fill(self):
        if self.code in FILL_MATERIALS.keys():
            self.tooth_tx_type = "filling"
            return True


    @property
    def material(self):
        return FILL_MATERIALS.get(self.code, "OT")

    def __repr__(self):
        return "ImportCode = %s"% (self.code)

def convert_diagn(line):
    treatments = line.split(" ")
    for tx in treatments:
        if tx == "":
            pass
        elif tx == "CE":
            yield ImportCode("A01")
        elif tx == "ECE":
            yield ImportCode("A02")
        elif tx == "FCA":
            yield ImportCode("A03")
        elif tx=="AA":
            yield ImportCode("L10")

        else:
            m = re.match("(\d+)?S$", tx)
            if m:
                numbers = m.groups()[0]
                n = 1 if numbers is None else int(numbers)
                for i in range(n):
                    yield(ImportCode("B01"))
                continue

            m = re.match("(\d+)?M$", tx)
            if m:
                numbers = m.groups()[0]
                n = 1 if numbers is None else int(numbers)
                for i in range(n):
                    yield(ImportCode("B03"))
                continue

            m = re.match("(\d+)?L$", tx)
            if m:
                numbers = m.groups()[0]
                n = 1 if numbers is None else int(numbers)
                for i in range(n):
                    yield(ImportCode("B04"))
                continue

            m = re.match("(\d+)?P$", tx)
            if m:
                numbers = m.groups()[0]
                n = 1 if numbers is None else int(numbers)
                for i in range(n):
                    yield(ImportCode("B05"))
                continue

            m = re.match("(\d+)?PHO$", tx)
            if m:
                numbers = m.groups()[0]
                n = 1 if numbers is None else int(numbers)
                for i in range(n):
                    yield(ImportCode("B20"))
                continue

            m = re.match("(\d+)?SM[12]$", tx)
            if m:
                numbers = m.groups()[0]
                n = 1 if numbers is None else int(numbers)
                for i in range(n):
                    if tx.endswith("1"):
                        yield(ImportCode("B10"))
                    else:
                        yield(ImportCode("B11"))
                continue

            print "UNHANDLED ITEM %s"% tx

'''
1001 1011 AC CP/1 CP/2 CP/3 GG GV/LL2 GV/LL5 GV/LL6 GV/LR1 GV/LR5 GV/LR7
GV/LR8 GV/UL2 GV/UL3 GV/UL4 GV/UL45 GV/UL46 GV/UL6 GV/UR1 GV/UR12 GV/UR2
GV/UR3 GV/UR6 MP/LR1234LL1234 MP/UL3 MP/UR3 MP/UR3,UL3 OHI PI/1 PI/2 SG
SP SP+ SP+/1 SP+/2 SP+/3 SP+/4 SP- SPL ST/LL8 ST/LR6 ST/UR2 ST/UR3 ST/UR3,UL3

simple|C01|Oral hygiene instruction
simple|C10|Minimal Scaling (Debridement)
simple|C11|Scale & Polish
simple|C12|Extended Scale & Polish
simple|C20|Advanced Periodontal Therapy|description
simple|C30|Periodontal Splinting
'''

def convert_perio(line):
    treatments = line.split(" ")

    for tx in treatments:
        if tx == "":
            pass
        elif tx == "OHI":
            yield ImportCode("C01")
        elif tx == "SP-":
            yield ImportCode("C10")
        elif tx in ("SP", "1001", "PS"):
            yield ImportCode("C11")
        elif tx in ("1011", "SP+"):
            yield ImportCode("C12")
        elif tx.startswith("SP+/") or tx.startswith("CP/"):
            yield ImportCode("C13")
        elif tx == "SPL":
            yield ImportCode("C30")
        elif tx == "AC":
            yield ImportCode("M20")
        elif tx == "SG": #soft tissue excision
            yield ImportCode("K30")
        elif tx.startswith("GV/"):
            yield(ImportCode("K20", tx))
        elif tx.startswith("MP/"):
            yield(ImportCode("C40", tx))
        else:
            print "UNHANDLED PERIO",tx

def convert_anaes(line):
    treatments = line.split(" ")

    for tx in treatments:
        if tx == "":
            pass
        elif tx == "S2A":
            yield ImportCode("Z30")
        else:
            print "UNHANDLED ANAES",tx

'''
FR nTU nXV FLD OS/OP PR PB FL/1 INC &FLD
1MGT: BL2: TU1: AB AH IS PSR RA2 RA1 1BL1:
MGT: OS OE 1TU1: BL1: 1AB SC OT DV1 2MGT: DV2
'''

def convert_misc(line):
    treatments = line.split(" ")

    for tx in treatments:
        if tx == "":
            pass
        elif tx == "OT":
            yield ImportCode("Z00")
        elif tx == "PR":
            yield ImportCode("Z02")
        elif tx in ("FLD", "&FLD", "INC"):
            print "ignoring", tx
        elif tx == "PB":
            yield ImportCode("K50", tx)
        elif tx.startswith("OS"):
            yield ImportCode("J00", tx)
        elif tx.startswith("FL"):
            yield ImportCode("Z03")
        elif tx.startswith("RA"):
            yield ImportCode("Z41")
        elif tx.startswith("DV"):
            yield ImportCode("Z41")
        elif tx == "SC":
            yield ImportCode("Z04")
        elif tx == "AH":
            yield ImportCode("K33")
        elif tx == "IS":
            yield ImportCode("K34")
        elif tx == "OE":
            yield ImportCode("Z05")
        elif tx == "PSR":
            yield ImportCode("K35")
        elif tx in ("BL1:", "1BL1:"):
            yield ImportCode("Z18")
        elif tx == "BL2:":
            yield ImportCode("Z13")
        else:
            m = re.match("(\d+)?XV$", tx)
            if m:
                print "ignoring", tx
                continue

            handled = False
            for pattern, code in (
                ("(\d+)?TU(\d+)?:?$", "Z01"),
                ("(\d+)?MGT:$", "Z40"),
                ("(\d+)?FR$", "K31"),
                ("(\d+)?AB$", "K32"),
            ):
                m = re.match(pattern, tx)
                if m:
                    numbers = m.groups()[0]
                    n = 1 if numbers is None else int(numbers)
                    for i in range(n):
                        yield(ImportCode(code))
                    handled = True
                    continue


            if not handled:
                print "UNHANDLED MISC Tx",tx

'''
PR AC 2863 6002 2810 AH IS
2922 3631 PSR S OCCL RA2 3501 SC XV 3512 1462
'''
def convert_other(line):
    treatments = line.split(" ")

    for tx in treatments:
        if tx == "":
            pass
        elif tx == "PR":
            yield ImportCode("Z02")
        elif tx == "AC":
            yield ImportCode("M20")
        elif tx == "SC":
            yield ImportCode("Z04")
        elif tx == "AH":
            yield ImportCode("K33")
        elif tx == "IS":
            yield ImportCode("K34")
        elif tx == "PSR":
            yield ImportCode("K35")
        elif tx == "2863":
            yield ImportCode("H40")
        elif tx == "6002":
            yield ImportCode("F40")
        elif tx == "2810":
            yield ImportCode("H41")
        elif tx == "2922":
            yield ImportCode("C30")
        elif tx == "3631":
            yield ImportCode("Z04")
        elif tx == "S":
            yield ImportCode("B01")
        elif tx == "OCCL":
            yield ImportCode("Z06")
        elif tx in ("RA2", "3512"):
            yield ImportCode("Z41")
        elif tx == "3501":
            yield ImportCode("Z42")
        elif tx == "XV":
            print "ignoring", tx
        elif tx == "1462":
            yield ImportCode("D21")

        else:
            print "UNHANDLED OTHER Tx",tx
