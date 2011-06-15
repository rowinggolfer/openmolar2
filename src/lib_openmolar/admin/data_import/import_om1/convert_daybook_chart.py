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
from lib_openmolar.common import SETTINGS

CORRECTIONS = {
'CR,PR,SR': 'CR,PR',
'CR,C3,C3': 'CR,C3',
'CR,C1,C1': 'CR,C1',
'CR,C1,C3': 'CR,C1',
'CR,C3,PR': 'CR,C3',
'CR,C4,PR': 'CR,PR',
'CR,PR,C3': 'CR,C3',
'EX/S12': 'EX/S1',
'EX/S1]': 'EX/S1',
'CR,RC,C3,C2,C2,C2':'CR,RC,C3',
'FS,CO.':'FS,CO',
"FS,CO'":'FS,CO',
'FS,GL,':'FS,GC',
'FS,GLC':'FS,GC',
'FS/B':'FS,CO',
'FS/B,CO':'FS,CO',
'FS/B,GC':'FS,CO',
'FS/P':'FS,CO',
'FS/P,CO':'FS,CO',
'FS/P,GC':'FS,CO',
'FS/P,GL':'FS,CO',
'dr':'FS,CO',
'fs,co':'FS,CO',
"GI,RC":'CR,RC',
'RC':'CR,RC',
'RC,PI':'CR,RC',
'RC,PV':'CR,RC',
'TM':'EX',
'SMOOTH':'ST',
'1401':'O,AM',
'1404':'MOD,AM',
'1411':'TR/D',
'1415':'O,CO',
'1421':'O,CO',
'1426':'O,GL',
'1427':'O,GL',
'1461':'O,GL',
'1462':'O,GL',
'1482':'FS,CO',
'1712':'CR,A2',
'1722':'CR,V2',
'1731':'CR,C1',
'1732':'CR,C2',
'1733':'CR,C3',
'1734':'CR,C4',
'1782':'CR,RC',
'1807':'BR/CR,V1',
'1825':'BR/CR,GO',
'1851':'BR,T1',
'1862':'BR,RC',
}


non_tooth_treatments = set([])

def find_codes(treat, tooth):

    def crown_extras(c_type):
        new = treat.replace(",%s"% c_type,"")
        if "," in new:
            return find_codes(new, tooth)
        return []

    ## clear some unique bad data inputs!
    treat = treat.lstrip("#")
    treat = treat.replace("code-","")
    treat = CORRECTIONS.get(treat, treat)

    pinnable = False
    front_tooth = tooth in SETTINGS.front_teeth
    DEFAULT_MAT = ",CO" if front_tooth else ",AM"
    if treat.strip(" ")=="":
        pass
    elif re.match("\(?BR", treat):
        print "UNDISCOVERED BRIDGE TREATMENT!", treat
    elif treat == "EX":
        yield ImportCode("K10", tooth)
    elif treat == "EX/S1":
        yield ImportCode("K11", tooth)
    elif re.match("EX/S(\d)$", treat):
        yield ImportCode("K12", tooth)
    elif treat.startswith("+X"):
        yield ImportCode("K13", tooth)
    elif treat == "RT":
        yield ImportCode("E01", tooth)
    elif treat.startswith("AP"):
        yield ImportCode("K21", tooth)
        if treat == "AP,RR":
            yield ImportCode("E30", tooth)
    elif treat == "FS":
        yield ImportCode("C50", tooth)
    elif treat in ("ST", "3661"):
        yield ImportCode("Z50", tooth)
    elif treat in ("PX", "PX+"):
        yield ImportCode("E20", tooth)
    elif treat == "PV":
        yield ImportCode("G40", tooth)
    elif treat.startswith("CR,V1"):
        yield ImportCode("F02", tooth)
        for code in crown_extras("V1"):
            yield code
    elif treat.startswith("CR,V2"):
        yield ImportCode("F03", tooth)
        for code in crown_extras("V2"):
            yield code
    elif treat == "1711":
        yield ImportCode("F15", tooth)
    elif treat.startswith("CR,A1"):
        yield ImportCode("F15", tooth)
        for code in crown_extras("A1"):
            yield code
    elif treat.startswith("CR,A2"):
        yield ImportCode("F16", tooth)
        for code in crown_extras("A2"):
            yield code
    elif treat == "CR,C1":
        yield ImportCode("F60", tooth)
    elif treat == "CR,C2":
        yield ImportCode("F61", tooth)
    elif treat == "CR,C3":
        yield ImportCode("F62", tooth)
    elif treat in ("CR,C4", "CR,PR"):
        yield ImportCode("F70", tooth)
    elif treat.startswith("CR,PJ"):
        yield ImportCode("F01", tooth)
        for code in crown_extras("PJ"):
            yield code
    elif treat.startswith("CR,GO"):
        yield ImportCode("F10", tooth)
        for code in crown_extras("GO"):
            yield code
    elif treat.startswith("CR,OT"):
        yield ImportCode("F00", tooth)
        for code in crown_extras("OT"):
            yield code
    elif treat == "CR,RESIN":
        yield ImportCode("F20", tooth)
    elif treat.startswith("CR,SR"):  ## this code was incorrectly used!
        yield ImportCode("F20", tooth)
        for code in crown_extras("SR"):
            yield code
    elif treat.startswith("CR,P1"):  ## this was the correct one!
        yield ImportCode("F20", tooth)
        for code in crown_extras("P1"):
            yield code
    elif treat == "CR,T1":
        yield ImportCode("F50", tooth)
    elif treat.startswith("CR,TC"):
        yield ImportCode("F50", tooth)
        for code in crown_extras("TC"):
            yield code
    elif treat.startswith("CR,RC"):
        yield ImportCode("F51", tooth)
        for code in crown_extras("RC"):
            yield code
    elif treat.startswith("CR,LAVA"):
        yield ImportCode("F32", tooth)
        for code in crown_extras("LAVA"):
            yield code
    elif treat.startswith("CR,OPALITE"):
        yield ImportCode("F30", tooth)
        for code in crown_extras("OPALITE"):
            yield code
    elif treat == "CR,RP":
        yield ImportCode("E50", tooth)
    elif treat.startswith("CR,RE") or treat=="CR,RF":
        yield ImportCode("F71", tooth)
    elif treat.startswith("CR,UF"):
        yield ImportCode("F72", tooth)
    elif treat in ("4402", "6002", "SS"):   #non-standard code used once by AH
        yield ImportCode("F40", tooth)
    elif treat in ("1422", "1423"):
        print "ignoring code %s - incisal edge/angle"% treat
    elif treat in("VP", "1511"):
        yield ImportCode("E40", tooth)
    elif treat == "NV":
        yield ImportCode("E41", tooth)
    elif treat == "RI":
        yield ImportCode("K22", tooth)
    elif treat == "SC":
        yield ImportCode("Z04", tooth)
    elif treat.startswith("SC/"):
        yield ImportCode("C60", tooth)
    elif treat in ("1600","1700"):
        print "ignoring code %s - first veneer/crown fee"% treat
    elif treat == "TP/FC":
        yield ImportCode("K16", tooth)
    elif treat == "TP/OD":
        yield ImportCode("Z51", tooth)
    elif re.match("FS,[GC][CLO]$", treat):
        yield ImportCode("D40", tooth)
    elif re.match("CR/[MOD]{3}[PL],GO$", treat):
        yield ImportCode("F11", tooth)
    elif re.match("CR/[MODB]{4},GO$", treat):
        yield ImportCode("F12", tooth)
    elif re.match("[MODBPLI]{4,}(%s)?"% DEFAULT_MAT, treat):
        code = ImportCode("D13", tooth)
        surfs = re.match("([MODBPLI]{4,})", treat).groups()[0]
        code.setSurfaces(surfs)
        pinnable = True
        yield code
    elif re.match("[MODBPLI]{3}(%s)?"% DEFAULT_MAT, treat):
        code = ImportCode("D12", tooth)
        code.setSurfaces(treat[:3])
        pinnable = True
        yield code
    elif re.match("[MODBPLI]{2}(%s)?"% DEFAULT_MAT, treat):
        code = ImportCode("D11", tooth)
        code.setSurfaces(treat[:2])
        pinnable = True
        yield code
    elif re.match("[MODBPLI]{1}(%s)?"% DEFAULT_MAT, treat):
        code = ImportCode("D10", tooth)
        code.setSurfaces(treat[:1])
        pinnable = True
        yield code
    elif re.match("[MODBPLI]{2,},GL", treat):
        code = ImportCode("D21", tooth)
        surfs = re.match("([MODBPLI]{2,})", treat).groups()[0]
        code.setSurfaces(surfs)
        pinnable = True
        yield code
    elif re.match("[MODBPLI]{1},GL", treat):
        code = ImportCode("D20", tooth)
        code.setSurfaces(treat[:1])
        pinnable = True
        yield code
    elif re.match("GC/[MODBPLI]*", treat):
        code = ImportCode("D21", tooth)
        surfs = re.match("GC/([MODBPLI]*)", treat).groups()[0]
        code.setSurfaces(surfs)
        pinnable = True
        yield code
    elif re.match("GI/[MODBPLI]*", treat):
        code = ImportCode("G10", tooth)
        surfs = re.match("GI/([MODBPLI]*)", treat).groups()[0]
        code.setSurfaces(surfs)
        pinnable = True
        yield code
    elif re.match("PI/[MODBPLI]*", treat):
        code = ImportCode("G20", tooth)
        surfs = re.match("PI/([MODBPLI]*)", treat).groups()[0]
        code.setSurfaces(surfs)
        pinnable = True
        yield code
    elif re.match("CI/[MODBPLI]*", treat):
        code = ImportCode("G30", tooth)
        surfs = re.match("CI/([MODBPLI]*)", treat).groups()[0]
        code.setSurfaces(surfs)
        pinnable = True
        yield code
    elif treat == "FA":
        yield ImportCode("J40", tooth)
    elif treat.startswith("TR/D"):
         yield ImportCode("D51", tooth)
    elif treat.startswith("TR/M"):
         yield ImportCode("D50", tooth)
    elif treat == "SECTION_BRIDGE":
         yield ImportCode("I80", tooth)
    elif treat == "[ul][lr][1-8]PR$":  ### whoops OM1 introduced this :(
        pinnable = True
    else:
        print "UNHANDLED CHART INPUT", treat

    if pinnable:
        if re.search(",PR", treat):
            yield ImportCode("D70", tooth)


#bridges
bonded_unit = "([UL][LR][1-8][^(BR)]* \(?BR/(CR|P),[AV][12]\)?)"
other_unit = "([UL][LR][1-8][^(BR)]* \(?BR/(CR|P),OT\)?)"
gold_unit = "([UL][LR][1-8][^(BR)]* \(?BR/(CR|P),GO\)?)"
adhesive_pontic = "([UL][LR][1-8][^(BR)]* \(?BR/P,(MA|AE|RO)\)?)"
wing_retainer = "([UL][LR][1-8][^(BR)]* \(?BR/(MR|AE)\)?)"
temp_unit = "([UL][LR][1-8][^(BR)]* \(?BR(/P)?,T[12]\)?)"

recement =  "([UL][LR][1-8][^(BR)]* \(?BR(/P)?,R[AC]\)?)"
repair =  "([UL][LR][1-8][^(BR)]* \(?BR(/P)?,RE\)?)"

def decrypt_bridge_line(line):
    if not re.search("\(.*\)", line):
        return
    result = ""
    retainers, pontics = 0, 0

    bonded_units = re.findall(bonded_unit, line)
    for unit in bonded_units:
        if unit[1] == "CR":
            retainers += 1
        elif unit[1] == "P":
            pontics += 1

    gold_units = re.findall(gold_unit, line)
    for unit in gold_units:
        if unit[1] == "CR":
            retainers += 1
        elif unit[1] == "P":
            pontics += 1

    other_units = re.findall(other_unit, line)
    for unit in other_units:
        if unit[1] == "CR":
            retainers += 1
        elif unit[1] == "P":
            pontics += 1

    temp_units = re.findall(temp_unit, line)
    for unit in temp_units:
        if "P" in unit[1]:
            pontics += 1
        else:
            retainers += 1

    pontics += len(re.findall(adhesive_pontic, line))
    wings = re.findall(wing_retainer, line)

    if pontics + retainers == 0:
        if re.search(recement, line):
            return ImportCode("I70")
        if re.search(repair, line):
            return ImportCode("I72")

    span = retainers+pontics
    if retainers == 0 and wings != []:
        #br_type = "adhesive"
        om_code = ImportCode("I40")
        om_code.description = "%d pontics %d wings"% (pontics, len(wings))
    elif bonded_units != [] and gold_units == [] and other_units == []:
        #br_type = "bonded"
        try:
            code = ("I10","I11","I12","I13","I14")[span-2]
        except IndexError:
            code = "I14"
        om_code = ImportCode(code)
        om_code.description = "%d retainers %d pontics"% (retainers, pontics)
    elif bonded_units == [] and gold_units != [] and other_units == []:
        #br_type = "gold"
        try:
            code = ("I20","I21","I22","I23","I24")[span-2]
        except IndexError:
            code = "I24"
        om_code = ImportCode(code)
        om_code.description = "%d retainers %d pontics"% (retainers, pontics)
    elif bonded_units == [] and gold_units == [] and other_units != []:
        #br_type = "other"
        om_code = ImportCode("I00")
        om_code.description = "%d retainers %d pontics"% (retainers, pontics)
    elif temp_units != []:
        #br_type = "temporary"
        om_code = ImportCode("I60")
        om_code.description = "%d retainers %d pontics"% (retainers, pontics)
    else:
        #br_type = "complex"
        om_code = ImportCode("I00")
        om_code.description = "%d retainers %d pontics"% (retainers, pontics)

    return om_code


def handle_bridges(line):
    '''
    takes the line, and removes any bridgework found therein
    Note - their can be more than one bridge in  line,
    so this function calls itself to check
    also.. treatments can be hidden within the bridgework brackets.
    this is also handled.
    '''
    #print "checking line %s for bridgework" %line
    codes = []

    if re.search("\(.*\)", line):
        print "BRIDGE(S) FOUND", line
        if len(re.findall("\(", line))>1:
            lines = line.split("  ")
        else:
            lines = [line]
        for l in lines:
            result = decrypt_bridge_line(l)
            if result is not None:
                codes.append(result)

        line = line.replace("(","").replace(")","")

    return re.sub(" BR[/,][^ ]*", " ", line), codes

def convert(line):
    '''
    a generator which spits out om_codes for all treatments found
    '''
    global non_tooth_treatments

    line, bridge_codes = handle_bridges(line)

    for om_code in bridge_codes:
        yield om_code

    treatments = line.split("  ")
    #print treatments
    for tx in treatments:
        if tx.strip(" ") == "":
            continue
        m =  re.match(" ?([UL][LR][1-8A-E])(.*)", tx)
        if m:
            tooth = m.groups()[0]
            om_tooth = SETTINGS.convert_tooth_shortname(tooth)
            treatments = m.groups()[1].strip(" ").split(" ")
            #print "tooth '%s' treatment '%s'"% (tooth, treatments)
            for treat in treatments:
                for om_code in find_codes(treat, om_tooth):
                    yield om_code
        elif tx.lower().startswith("custo consult"):
            om_code = ImportCode("A10")
            yield om_code
        else:
            print tx
            non_tooth_treatments.add(tx.strip(" "))


def rogue_output():
    for tx_set in (non_tooth_treatments,):
        treatment_list = list(tx_set)
        treatment_list.sort()
        print "="*80
        print "%s Treatments found"% len(treatment_list)
        print "="*80

        for tx in treatment_list:
            print tx
        print


if __name__== "__main__":
    lines = '''UL2 RT
LL7 MO,CO
UR7 P,CO  UR5 MOD  UR4 DO
UL7 MO
UL7 P,GL
UR4 (BR/MR  UR2 BR/P,AE  UR1 BR/MR) PV  UL1 PV  UL2 (BR/P,AE  UL3 BR/MR MI  UL4 BR/MR)
UR2 CR,V1  UR1 CR,V1  LR6 B,GL
UR7 MOD  UR6 EX/S2  UR5 MOD  UR4 DO  UL5 DR  LL6 MOD  LL5 MOD  LL4 DO  LR6 MOD  LR7 MOD
UR5 B,GL  UR4 B,GL  UL2 M
UR3 DI  UR1 D  UL3 M  UL5 O
UL6 CR,V1,C3
UR2 CR,V1,C3
UR5 EX  URC EX  ULC EX  UL6 O  LL6 O  LL5 EX  LR5 EX
UR3 EX  UL3 EX
LR6 MO
UR8 OB,PR  UR6 B,CO  LR7 B,CO
UR3 (BR,RA  UR2 BR/P,RA  UR1 BR,RA)
UR7 EX
LL7 FS  LR5 FS
UR8 DOP,CO  UL5 DB,CO
UR5 EX
LL2 M  LR5 DB,CO
UL8 MODP,CO
LL7 MB  LR1 M  LR7 DL
UL4 MODP,PR,CO
ULE P
LL7 O
UR3 I  UL5 P,CO
UL5 MOD,CO
UL7 MOD  LL4 B,GL
ULE MO
UR2 M  LL6 (BR/CR,V1  LL5 BR/P,V1)  LR6 MOD
LR3 DI  LR4 MOD  LR5 OB,PR
UR4 MP,AM  UL7 MP
UR1 P
'''
    for line in lines.split("\n"):
        print "=" * 80
        for code in convert(line):
            print code
        print "=" * 80
