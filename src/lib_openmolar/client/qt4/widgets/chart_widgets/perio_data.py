#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
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

from PyQt4 import QtGui, QtCore
from lib_openmolar.client.classes import Tooth


class PerioDataError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PerioData(object):
    '''
    data about the root's periodontal status.
    pocketing, bleeding, furcation etc...
    '''
    POCKETING = 0
    RECESSION = 1
    BLEEDING = 2
    SUPURATION = 3
    FURCATION = 4

    type = POCKETING

    def __init__(self, tooth_id):
        self._data = None
        self.tooth_id = tooth_id
        self.in_database = False
        self._tooth = None

    @property
    def tooth(self):
        if self._tooth is None:
            self._tooth = Tooth(self.tooth_id)
        return self._tooth

    def __repr__(self):
        return "perio_data for %s Type %s Values%s"% (
            self.tooth, self.type, self.data)

    def set_type(self, type):
        self.type = type

    def set_values(self, values):
        if self.type == self.POCKETING:
            self.set_pockets(values)
        elif self.type == self.BLEEDING:
            self.set_bleeding(values)
        else:
            raise PerioDataError(
        "no perio type set for perio data of tooth %s"% self.tooth)

    def set_pockets(self, values):
        assert len(values) == 6, "we need 6 values for set_pockets"
        self._data = []
        for val in values:
            self._data.append(val)

    def set_bleeding(self, values):
        assert len(values) == 6, "we need 6 values for set_pockets"
        self._data = []
        for val in value:
            self._data.append(val)

    @property
    def data(self):
        return self._data

    @property
    def brush(self):
        if self.type == self.FILLING:
            return QtGui.QApplication.instance().palette().buttonText()
        else:
            return QtGui.QApplication.instance().palette().dark()

    @property
    def icon(self):
        ##todo
        return QtGui.QIcon(":icons/openmolar.png")

    @property
    def text(self):
        ##TODO
        text = "unknown item!"
        return text

if __name__ == "__main__":
    data = PerioData(1)
    print dir(data)

    data.set_values((1,2,3,4,5,6))

    print data.data