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

from lib_openmolar.common import SETTINGS
from PyQt4 import QtCore

class TeethPresentDecoder(object):
    def __init__(self):
        key = []
        for i in xrange(63, -1, -1):
            key.append(2**i)

        self.DENT_KEY = tuple(key)

    def encode(self, bit_array):
        int_val = 0
        for i in range(64):
            if bit_array.at(i):
                int_val += self.DENT_KEY[i]
        return int_val

    def decode(self, int_val):
        bit_array = QtCore.QBitArray(64)
        i = 0
        for exp in self.DENT_KEY:
            if exp <= int_val:
                bit_array.setBit(i)
                int_val -= exp
            i += 1
        return bit_array

    def to_ascii_art(self, int_val):
        ascii = ""
        bit_array = self.decode(int_val)
        for row, start in ((0,0),(1,16),(2,32),(3,48)):
            for i in range(16):
                pos = start + i
                if bit_array.at(pos):
                    tooth_id = SETTINGS.TOOTH_GRID[row][i]
                    ascii += " %s "% (
                        SETTINGS.TOOTHGRID_SHORTNAMES.get(tooth_id, "???"))
                else:
                    ascii += "  -  "
                if i== 7:
                    ascii += "|"

            if row ==1 :
                ascii += "\n" + "-----" * 16 +"\n"
            else:
                ascii += "\n"

        return ascii


if __name__=="__main__":
    def chart(bit_array):
        ret_str = "chart ="
        for i in range(bit_array.count()):
            if bit_array.at(i):
                ret_str +=  "X"
            else:
                ret_str += "-"

    tp = TeethPresentDecoder()

    full_bit_array = QtCore.QBitArray(64)

    adult_bit_array = QtCore.QBitArray(64)
    for i in xrange(16,48):
        adult_bit_array.setBit(i)
        full_bit_array.setBit(i)

    child_bit_array = QtCore.QBitArray(64)
    for start in (3, 51):
        for i in xrange(10):
            child_bit_array.setBit(i+start)
            full_bit_array.setBit(i+start)

    for bit_array in (full_bit_array, child_bit_array, adult_bit_array):
        key = tp.encode(bit_array)
        print key
        if chart(bit_array) != chart(tp.decode(key)):
            print "ENCODE/DECODE ERROR!"
        else:
            print tp.to_ascii_art(key)
