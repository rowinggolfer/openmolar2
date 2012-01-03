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
import sys
from PyQt4 import QtSql, QtCore

from lib_openmolar.common import SETTINGS
from lib_openmolar.admin.data_import.import_om1 import teeth_present

ps_query_comment = '''INSERT INTO static_comments
(patient_id, tooth, comment, checked_by)
VALUES (?, ?, ?, ?)'''

ps_query_crown = '''INSERT INTO static_crowns
(patient_id, tooth, type, comment)
VALUES (?, ?, ?, ?)'''

ps_query_fill = '''INSERT INTO static_fills
(patient_id, tooth, surfaces, material, comment)
VALUES (?, ?, ?, ?, ?)'''

ps_query_root = '''INSERT INTO static_roots
(patient_id, tooth, description, comment,
checked_by) VALUES (?, ?, ?, ?, ?)'''

ps_query_super = '''INSERT INTO static_supernumerary
(patient_id, mesial_neighbour, comment,
checked_by) VALUES (?, ?, ?, ?)'''

ps_query_dent_key = '''INSERT INTO teeth_present
(patient_id, dent_key, checked_by)
VALUES (?, ?, ?)'''

short_tooth_name_list = []
for arch in ("u","l"):
    for tooth in range(8,0,-1):
        short_tooth_name_list.append("%sr%d"% (arch,tooth))
    for tooth in range(1,9):
        short_tooth_name_list.append("%sl%d"% (arch,tooth))

def convert(mysql_query, psql_query, sno_conditions=""):
    teeth_fields = ""
    for tooth_name in short_tooth_name_list:
        teeth_fields += "%sst, "% tooth_name

    query = '''select serialno, dent1, dent0, dent3, dent2,
    %s from patients'''% teeth.rstrip(", ")
    query += sno_conditions

    mysql_query.prepare(query)
    mysql_query.exec_()
    while mysql_query.next():
        urq = mysql_query.value(1).toInt()[0]
        ulq = mysql_query.value(2).toInt()[0]
        lrq = mysql_query.value(3).toInt()[0]
        llq = mysql_query.value(4).toInt()[0]

        bit_array = teeth_present.get_dent_key(urq, ulq, lrq, llq)

        i = 4 #offset to get to tooth values
        for tooth in short_tooth_name_list:
            i += 1
            val_str = str(mysql_query.value(i).toString())
            om_tooth = SETTINGS.REV_TOOTHGRID_SHORTNAMES[tooth]

            vals = set(val_str.split(" "))
            for val in vals:
                if val == '':
                    continue
                if val.startswith("-"):
                    print "IGNORING MOVED TOOTH", val
                    continue
                if val =='AT':  #TODO - prosthetics
                    print "IGNORING PROSTHETIC", val
                    continue
                if re.match("\(?BR", val):
                    print "IGNORING BRIDGE", val
                    continue
                if val == 'ST':
                    print "IGNORING STONING"
                    continue

                if val == "!IMPLANT":
                    val = "IMPLANT"

                if val.startswith("!"):
                    psql_query.prepare(ps_query_comment)
                    psql_query.addBindValue(mysql_query.value(0))
                    psql_query.addBindValue(om_tooth)
                    psql_query.addBindValue(val.strip("!"))
                    psql_query.addBindValue("imported")

                elif val == "+S":
                    psql_query.prepare(ps_query_super)
                    psql_query.addBindValue(mysql_query.value(0))
                    psql_query.addBindValue(om_tooth)
                    psql_query.addBindValue(val)
                    psql_query.addBindValue("imported")

                elif (val.startswith("CR,") or
                val.startswith("CR/") or val in ("PV",)):
                    #print "CROWN FOUND!", val
                    comment = ""

                    if re.match("CR/.*,GO$", val):
                        c_type == "GO"
                        comment = val
                    else:
                        c_type = val.replace("CR,","")

                    if c_type == "RC":
                        print "IGNORING RECEMENT"
                        continue

                    if "," in c_type:
                        multi_atts = c_type.split(",")
                        c_type = multi_atts[0]
                        for att in multi_atts[1:]:
                            comment += "%s "% att

                    if c_type == "OPALITE":
                        c_type = "OPAL"
                    elif c_type == "LAVA":
                        c_type = "LA"
                    elif c_type == "P1":
                        c_type = "SR"
                    elif c_type ==  "T1":
                        c_type = "TEMP"
                    elif c_type ==  "A1":
                        c_type = "V2"

                    psql_query.prepare(ps_query_crown)
                    psql_query.addBindValue(mysql_query.value(0))
                    psql_query.addBindValue(om_tooth)
                    psql_query.addBindValue(c_type)
                    psql_query.addBindValue(comment.strip(" "))

                elif val in ("TM", "AP", "AP,RR", "RT", "UE", "PE", "RP",
                "IMPLANT", "OE"):
                    #print "ROOT", val
                    comment = ""
                    if val == "TM":
                        bit_array.setBit(i-5+16, False)
                    if val == "IMPLANT":
                        val = "IM"
                    if val == "AP,RR":
                        val = "AP"
                        comment = "Retrograde Root Fill"
                    psql_query.prepare(ps_query_root)
                    psql_query.addBindValue(mysql_query.value(0))
                    psql_query.addBindValue(om_tooth)
                    psql_query.addBindValue(val)
                    psql_query.addBindValue(comment)
                    psql_query.addBindValue("imported")

                else:
                    #print "FILL", val
                    comment = ""
                    if val.startswith("TR/"):
                        val = val.replace("TR/","")
                        comment = "tunnel restoration"

                    if val.startswith("PI/"):
                        fill_info = val.split("/")
                        fill_info.reverse()
                        fill_info[1]="PO"
                    elif val.startswith("GI/"):
                        fill_info = val.split("/")
                        fill_info.reverse()
                        fill_info[1]="GO"
                    elif val == "DR":
                        fill_info = ["O","DR"]
                    elif val == "FS":
                        fill_info = ["O","FS"]
                    elif val.startswith('FS,'):
                        fill_info = val.split(",")
                        fill_info[0] = "O"
                        if fill_info[1] == "GC":
                            fill_info[1] = "CO"
                    else:
                        fill_info = val.split(",")

                    if "PR" in fill_info:
                        comment += "pinned "
                        fill_info.remove("PR")
                    if "CT" in fill_info:
                        comment += "cusp tip "
                        fill_info.remove("CT")

                    psql_query.prepare(ps_query_fill)
                    psql_query.addBindValue(mysql_query.value(0))
                    psql_query.addBindValue(om_tooth)

                    surfaces = fill_info[0]
                    surfaces = surfaces.replace("P","L")
                    surfaces = surfaces.replace("I","O")
                    psql_query.addBindValue(surfaces)

                    material = ""
                    try:
                        material = fill_info[1]
                    except IndexError:
                        pass

                    if material == "":
                        if om_tooth in SETTINGS.back_teeth:
                            material = "AM"
                        else:
                            material = "CO"

                    psql_query.addBindValue(material)
                    psql_query.addBindValue(comment)

                psql_query.exec_()
                if psql_query.lastError().isValid():
                    print "ERROR IMPORTING %s - %s %s"% (
                        mysql_query.value(0).toInt()[0],
                        val,
                        psql_query.lastError().text())


        dent_key = teeth_present.array_to_key(bit_array)

        psql_query.prepare(ps_query_dent_key)
        psql_query.addBindValue(mysql_query.value(0).toInt()[0])
        psql_query.addBindValue(dent_key)
        psql_query.addBindValue("imported")

        psql_query.exec_()
        if psql_query.lastError().isValid():
            print "ERROR IMPORTING DENT KEY %s - %s"% (
                mysql_query.value(0).toInt()[0],
                psql_query.lastError().text())
