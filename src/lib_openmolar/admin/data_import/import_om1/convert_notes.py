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


import re, sys, copy
from PyQt4 import QtCore

'''
CHART = {
136:"UR8", 135:"UR7", 134:"UR6", 133:"UR5",
132:"UR4", 131:"UR3", 130:"UR2", 129:"UR1",
144:"UL1", 145:"UL2", 146:"UL3", 147:"UL4",
148:"UL5", 149:"UL6", 150:"UL7", 151:"UL8",
166:"LL8", 165:"LL7", 164:"LL6", 163:"LL5",
162:"LL4", 161:"LL3", 160:"LL2", 159:"LL1",
174:"LR1", 175:"LR2", 176:"LR3", 177:"LR4",
178:"LR5", 179:"LR6", 180:"LR7", 181:"LR8",
142:"URE", 141:"URD", 140:"URC", 139:"URB",
138:"URA", 153:"ULA", 154:"ULB", 155:"ULC",
156:"ULD", 157:"ULE", 172:"LLE", 171:"LLD",
170:"LLC", 169:"LLB", 168:"LLA", 183:"LRA",
184:"LRB", 185:"LRC", 186:"LRD", 187:"LRE"}
'''

CHART = {
710:"UR8", 8225:"UR7", 8224:"UR6", 8230:"UR5",
8222:"UR4", 402:"UR3", 8218:"UR2", 129:"UR1",
144:"UL1", 8216:"UL2", 8217:"UL3", 8220:"UL4",
8221:"UL5", 8226:"UL6", 8211:"UL7", 8212:"UL8",
166:"LL8", 165:"LL7", 164:"LL6", 163:"LL5",
162:"LL4", 161:"LL3", 160:"LL2", 376:"LL1",
174:"LR1", 175:"LR2", 176:"LR3", 177:"LR4",
178:"LR5", 179:"LR6", 180:"LR7", 181:"LR8",
381:"URE", 141:"URD", 338:"URC", 8249:"URB",
352:"URA", 8482:"ULA", 353:"ULB", 8250:"ULC",
339:"ULD", 157:"ULE", 172:"LLE", 171:"LLD",
170:"LLC", 169:"LLB", 168:"LLA", 183:"LRA",
184:"LRB", 185:"LRC", 186:"LRD", 187:"LRE"}

class NoteLineClass(object):
    '''
    A custom datatype to store data from the old openmolar notes string
    '''
    type = ""
    note = ""
    operator1 = ""
    operator2 = ""
    NULL_TIME = QtCore.QDateTime(1900,1,1,0,0)
    time = NULL_TIME
    commit_time = QtCore.QDateTime(1900,1,1,0,0)

    def __init__(self):
        pass

    @property
    def is_clerical(self):
        return self.operator1 == "REC" and self.om_type != "treatment"

    @property
    def ops(self):
        return "%s/%s"% (self.operator1, self.operator2)

    def set_note(self, note):
        '''
        convenience function to check encoding
        '''
        self.note = note.encode("ascii", "replace")

    @property
    def om_type(self):
        return "treatment" if "TC" in self.note else "observation"

    def __repr__(self):
        if self.time == self.NULL_TIME:
            rep = " " * 20
        else:
            rep = str(self.time.toString(4)).ljust(20)
                #QtCore.Qt.SystemLocaleShortDate)).ljust(20)
        rep += self.type.ljust(30)
        if self.operator1 is None:
            rep += " " * 10
        else:
            rep += self.ops.ljust(10)

        return rep + self.note

def log_ignore(nlc):
    print "IGNORING", nlc

def notes(lines):
    '''
    lines is a list of om1 note "strings"
    ["/0xc1 foobar","0xc1 etc...",....]
    '''
    nlcs = []
    for line in lines:
        nlc = decipher_old_noteline(line)
        if nlc:
            #print nlc      #print the lines old style!
            nlcs.append(nlc)

    last_ops = None
    yield_nlc = None

    for i, nlc in enumerate(nlcs):
        try:
            next_nlc = nlcs[i+1]
        except IndexError:
            next_nlc = None

        if nlc.type == "opened":
            if yield_nlc is None:
                yield_nlc = copy.copy(nlc)
                last_ops = nlc.ops

        elif nlc.type == "closed":
            if (next_nlc is None or
            yield_nlc.time.secsTo(next_nlc.time) > 3600 or
            last_ops != next_nlc.ops):
                yield_nlc.commit_time = nlc.time
                yield yield_nlc
                yield_nlc = None

        else:
            if nlc.type.startswith("TC"):
                log_ignore(nlc)
                #yield_nlc.note = "%s %s\n%s"% (
                #    nlc.type,
                #    nlc.note.strip("\n"),
                #    yield_nlc.note)
            elif nlc.type.startswith("STATIC"):
                pass
                #log_ignore(nlc)
            elif nlc.type == "COURSE CLOSED":
                pass
                #log_ignore(nlc)
            elif nlc.type.startswith("UPDATED"):
                log_ignore(nlc)
            elif nlc.type != "NOTE":
                yield_nlc.note += "%s %s\n"% (nlc.type, nlc.note.strip("\n"))
            else:
                if nlc.note.strip("\n") != "":
                    yield_nlc.note += nlc.note + "\n"

def decipher_old_noteline(noteline):
    '''
    changes an old noteline into the custom datatype NoteLineClass
    '''
    if len(noteline) == 0:  #sometimes a line is blank
        return

    nlc = NoteLineClass()

    if noteline[0] == chr(1):
        nlc.type = "opened"
        operator = ""
        i = 1
        while noteline[i] >= "A" or noteline[i] == "/":
            operator += noteline[i]
            i += 1

        try:
            nlc.operator1, nlc.operator2 = operator.split("/")
        except ValueError:
            nlc.operator1 = operator

        nlc.time = QtCore.QDateTime(1900+ord(noteline[i+2]),
                    ord(noteline[i+1]), ord(noteline[i]),
                    ord(noteline[i+6]), ord(noteline[i+7]))

    elif noteline[0] == chr(2):   #
        nlc.type = "closed"
        operator = ""
        i = 1
        while noteline[i] >= "A" or noteline[i] == "/":
            operator += noteline[i]
            i += 1

        nlc.time = QtCore.QDateTime(1900+ord(noteline[i+2]),
                    ord(noteline[i+1]), ord(noteline[i]),
                    ord(noteline[i+3]), ord(noteline[i+4]))

    elif noteline[0] == chr(3):
        #-- hidden nodes start with chr(3) then another character
        code_char = ord(noteline[1])
        if code_char == 97:
            nlc.type="COURSE CLOSED"
            nlc.set_note("")
        elif code_char == 100:
            nlc.type="UPDATED:"
            nlc.set_note("Medical Notes "+noteline[2:])
        elif code_char == 101:
            nlc.type="UPDATED:"
            nlc.set_note("Perio Chart")
        elif code_char == 104:
            nlc.type="TC: XRAY"
            nlc.set_note(noteline[2:])
        elif code_char == 105:
            nlc.type="TC: PERIO"
            nlc.set_note(noteline[2:])
        elif code_char == 106:
            nlc.type="TC: ANAES"
            nlc.set_note(noteline[2:])
        elif code_char == 107:
            nlc.type="TC: OTHER"
            nlc.set_note(noteline[2:])
        elif code_char == 108:
            nlc.type="TC: NEW Denture Upper"
            nlc.set_note(noteline[2:])
        elif code_char == 109:
            nlc.type="TC: NEW Denture Lower"
            nlc.set_note(noteline[2:])
        elif code_char == 110:
            nlc.type="TC: Existing Denture Upper"
            nlc.set_note(noteline[2:])
        elif code_char == 111:
            nlc.type="TC: Existing Denture Lower"
            nlc.set_note(noteline[2:])
        elif code_char == 112:
            nlc.type="TC: EXAM"
            nlc.set_note(noteline[2:])
        elif code_char == 113:
            nlc.type="TC:"
            nlc.set_note(tooth(noteline[2:]))
        elif code_char == 114:
            nlc.type="STATIC: " #1st line of static
            nlc.set_note(tooth(noteline[2:]))
        elif code_char == 115:
            nlc.type="PRINTED: "
            nlc.set_note("GP17(A)")
        elif code_char == 116:
            nlc.type="PRINTED: "
            nlc.set_note("GP17(C)")
        elif code_char == 117:
            nlc.type="PRINTED: "
            nlc.set_note("GP17(DC)")
        elif code_char == 118:
            nlc.type="PRINTED: "
            nlc.set_note(noteline[2:])
        elif code_char in (119, ):
            nlc.type="RECEIVED: "
            nlc.set_note(noteline[2:])
        elif code_char == 120:
            nlc.type="REVERSE PAYMENT:"
            nlc.set_note(noteline[2:])
        elif code_char == 121:
            nlc.type="STATIC (cont): "   #additional line of static
            nlc.set_note(tooth(noteline[2:]))
        elif code_char == 123:
            nlc.type="PRINTED: "
            nlc.set_note("GP17")
        elif code_char == 124:
            nlc.type="PRINTED: "
            nlc.set_note("GP17PR")
        elif code_char in (130, 8218):
            nlc.type="ESTIMATE: "
            nlc.set_note(noteline[2:])
        elif code_char in (131, 402):
            nlc.type="INTERIM: "
            nlc.set_note(noteline[2:])
        elif code_char in (132, 8222): #QtString handles this different to MySQLdb?
            nlc.type="FINAL: "
            nlc.set_note(noteline[2:])
        elif code_char == 133:
            nlc.type="ACTUAL: "
            nlc.set_note(tooth(noteline[2:]))
        elif code_char in (134, 710):
            nlc.type="FILED: "
            nlc.set_note("Claim")
        elif code_char == 136:
            nlc.type="FILED: "
            nlc.set_note("Registration")
        else:
            nlc.type='UNKNOWN LINE(codechar %d):'% code_char
            nlc.set_note(noteline[2:])

    else:
        nlc.type="NOTE"
        nlc.set_note(noteline.strip("\t\n "))

    return nlc

def tooth(data_string):
    retarg=""
    for data in data_string.split(" "):
        data = data.strip("\t ")
        if data == "":
            continue

        i = ord(data[0])

        spec = data[1:]

        if CHART.has_key(i):
            retarg += " | %s "% CHART[i]
            retarg += spec.replace("\n","")
        else:
            retarg += " %s "% data.replace("\n","")

    return retarg.lstrip(" |")

