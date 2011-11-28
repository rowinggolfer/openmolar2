#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011, Neil Wallace <rowinggolfer@googlemail.com>               ##
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

import random
import string
from hashlib import md5

def md5hash(str):
    '''
    returns a hash of a string.
    '''
    return md5(str).hexdigest()

def new_password(length=20):
    '''
    returns a new password
    '''
    chars = string.letters + string.digits
    return ''.join([random.choice(chars) for i in xrange(length)])

def pass_hash(length=20):
    '''
    returns a new password and its hash
    '''
    p = new_password(length)
    return (p, md5hash(p))

def _test():
    for i in range (10,30):
        print pass_hash(i)

if __name__ == "__main__":
    _test()
