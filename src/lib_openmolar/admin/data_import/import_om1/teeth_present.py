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

from PyQt4 import QtCore
from lib_openmolar.client.scripts.dent_key import TeethPresentDecoder

DECODER = TeethPresentDecoder()

def from_signed_byte(val):
    '''
    this returns a bit by bit representation of a signed byte -
    used for deciduous tooth
    this is used to decrypt the way that wysdom IT saved the deciduous teeth
    of patients.(obscure by design?)
    '''
    if val >= 0:
        base = (128,64,32,16,8,4,2,1)
        bstring = []
        for b in base:
            if val >= b:
                bstring.append("1")
                val -= b
            else:
                bstring.append("0")
    else:
        base = (-64,-32,-16,-8,-4,-2,-1)
        bstring = ["1"] #set the negative bit
        for b in base:
            if val < b:
                bstring.append("0")
                val -= b
            else:
                bstring.append("1")

    adult_string = []
    for b in bstring:
        if b == "1":
            adult_string.append("0")
        else:
            adult_string.append("1")

    return bstring, adult_string

def get_dent_key(urq, ulq, lrq, llq):
    '''
    convert to new format
    '''
    bit_array = QtCore.QBitArray(64)

    urq_dec_bits, urq_bits = from_signed_byte(urq)
    ulq_dec_bits, ulq_bits = from_signed_byte(ulq)
    lrq_dec_bits, lrq_bits = from_signed_byte(lrq)
    llq_dec_bits, llq_bits = from_signed_byte(llq)

    for molar in [0,1,2]:
        urq_dec_bits[molar] = "0"
        lrq_dec_bits[molar] = "0"
    for molar in [5,6,7]:
        ulq_dec_bits[molar] = "0"
        llq_dec_bits[molar] = "0"


    bstring = ( urq_dec_bits + ulq_dec_bits +
                urq_bits + ulq_bits +
                lrq_bits + llq_bits +
                lrq_dec_bits + llq_dec_bits
                )
    i = 0
    for bit in bstring:
        bit_array.setBit(i, bit=="1")
        i += 1

    return bit_array

def array_to_key(bit_array):
    return DECODER.encode(bit_array)


if __name__ == "__main__":
    #example - all teeth are adult except the urB
    dent0, dent1, dent2, dent3 = 0,2,0,0

    #order they used was 1,0,3,2 (no idea why.....)
    print from_signed_byte(dent1)[0],
    print from_signed_byte(dent0)[0]
    print from_signed_byte(dent1)[1],
    print from_signed_byte(dent0)[1]
    print from_signed_byte(dent2)[1],
    print from_signed_byte(dent2)[1]
    print from_signed_byte(dent3)[0],
    print from_signed_byte(dent2)[0]

    print get_dent_key(dent1, dent0, dent3, dent2)