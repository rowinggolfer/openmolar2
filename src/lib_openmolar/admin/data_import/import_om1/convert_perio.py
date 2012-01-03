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

import struct
from lib_openmolar.common import SETTINGS

class PerioDict(object):
    recession = {}
    pocketing = {}
    plaque = {}
    bleeding = {}
    other = {}
    suppuration = {}
    furcation = {}
    mobility = {}

    def __repr__(self):
        return '''PERIO DATA
recession = %s
pocketing = %s
plaque = %s
bleeding = %s
other = %s
suppuration = %s
furcation = %s
mobility = %s''' % (self.recession, self.pocketing, self.plaque,
self.bleeding, self.other, self.suppuration, self.furcation, self.mobility)

def get_perioData(data):

    perio_dict = PerioDict()

    i = 0

    #for tooth in (
    #'ur8','ur7','ur6','ur5','ur4','ur3','ur2','ur1',
    #'ul1','ul2','ul3','ul4','ul5','ul6','ul7','ul8',
    #'lr8','lr7','lr6','lr5','lr4','lr3','lr2','lr1',
    #'ll1','ll2','ll3','ll4','ll5','ll6','ll7','ll8'
    #):
    for tooth in SETTINGS.TOOTH_GRID[1] + SETTINGS.TOOTH_GRID[2]:
        d = struct.unpack_from('b'*45,data,i)
        perio_dict.recession[tooth] = (d[0],d[1],d[2],d[3],d[4],d[5])
        perio_dict.pocketing[tooth] = (d[6],d[7],d[8],d[9],d[10],d[11])
        perio_dict.plaque[tooth] = (d[12],d[13],d[14],d[15],d[16],d[17])
        perio_dict.bleeding[tooth] = (d[18],d[19],d[20],d[21],d[22],d[23])
        perio_dict.other[tooth] = (d[24],d[25],d[26],d[27],d[28],d[29])
        perio_dict.mobility[tooth] = d[34]
        perio_dict.furcation[tooth] = (d[30],d[31],d[32],d[33])
        perio_dict.suppuration[tooth] = (d[35],d[36],d[37],d[38],d[39],d[40])

        i+=45


    return perio_dict