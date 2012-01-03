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

from PyQt4 import QtGui, QtCore

class Colours(object):
    @property
    def CHARTTEXT(self):
        return QtGui.QColor("#111111")

    @property
    def TOOTHLINES(self):
        return QtGui.QColor("#aaaaaa")

    @property
    def IVORY(self):
        return QtGui.QColor("#ffeedd")

    @property
    def UNKNOWN(self):
        return QtGui.QColor("purple")

    @property
    def GLASS(self):
        GI_ = "#75d185"
        return QtGui.QColor(GI_)

    @property
    def GOLD(self):
        GOLD_ = "#ffff00"
        return QtGui.QColor(GOLD_)

    @property
    def COMPOSITE(self):
        COMP_ = "#ffffff"
        return QtGui.QColor(COMP_)

    @property
    def PORCELAIN(self):
        PORC_ = "#ddffff"
        return QtGui.QColor(PORC_)

    @property
    def AMALGAM(self):
        AMALGAM_ = "#666666"
        return QtGui.QColor(AMALGAM_)

    @property
    def FISSURE(self):
        return QtGui.QColor("#bbd0d0")

    @property
    def METAL(self):
        return QtGui.QColor("#000075")

    @property
    def DRESSING(self):
        return QtGui.QColor("magenta")

    @property
    def GUTTA_PERCHA(self):
        return QtGui.QColor("#bb0000")

    @property
    def FILL_OUTLINE(self):
        return QtGui.QColor("#333333")  #used to be blue

    @property
    def TRANSPARENT(self):
        return QtCore.Qt.transparent

    @property
    def REQUIRED_FIELD(self):
        return QtGui.QColor("#ffffaa")

    @property
    def BOLD_TEXT(self):
        return QtGui.QColor("red")


colours = Colours()

if __name__ == "__main__":
    pass
