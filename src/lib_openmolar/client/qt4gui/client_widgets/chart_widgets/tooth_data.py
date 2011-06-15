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

from PyQt4 import QtGui, QtCore

class ToothDataError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ToothData(object):
    '''
    a custom object which holds information about a filling, crown or comment
    NOTE - filled surfaces are stored as MODBL -
    so I and P surfaces are translated if used for user interaction
    '''
    Filling = 0
    Crown = 1
    Root = 2
    Comment = 3

    #attributes when data is a filling
    surfaces = ''
    material = ''
    _draw_surfaces = None #private attribute

    #attributes when data is a crown
    crown_type = ''
    technition = ''

    #attributes when data is a root
    has_rct = False
    root_type = ''

    #common to all types
    comment = ''
    proc_code = None
    svg = None

    def __init__(self, tooth=None):
        self.tooth = tooth
        self.in_database = False
        self.error_message = ""
        self.type = self.Filling #default "type" is a Filling

    @property
    def is_valid(self):
        if self.type == self.Filling:
            return self.surfaces != ""
        elif self.type == self.Crown:
            return self.crown_type !=""
        return False

    def set_type(self, type):
        self.type = type

    def set_crown_type(self, crown_type):
        if not self.type == self.Crown:
            raise ToothDataError("This is not a crown")
        self.crown_type = crown_type

    def set_root_type(self, root_type):
        if not self.type == self.Root:
            raise ToothDataError("This is not a root")
        self.root_type = root_type

    def set_surfaces(self, surfaces):
        if not self.type == self.Filling:
            raise ToothDataError("This is not a filling")
        self.surfaces = surfaces

    @property
    def draw_surfaces(self):
        # a "mirrored" version of surfaces, allowing for quadrant
        if self._draw_surfaces:
            return self._draw_surfaces

        #only do this once.
        ds = self.surfaces[:]
        if self.tooth.quadrant in (2,3):  #mirror left/right
            ds = ds.replace("M","m").replace("D","M").replace("m","D")
        if self.tooth.quadrant in (3,4):  #mirror up/down
            ds = ds.replace("B","b").replace("L","B").replace("b","L")

        self._draw_surfaces = ds
        return ds

    @property
    def brush(self):
        if self.type == self.Filling:
            return QtGui.QApplication.instance().palette().buttonText()
        else:
            return QtGui.QApplication.instance().palette().dark()

    @property
    def icon(self):
        if self.type == self.Filling:
            return QtGui.QIcon(":icons/filling.png")
        elif self.type == self.Root:
            return QtGui.QIcon(":icons/root.png")
        elif self.type == self.Crown:
            return QtGui.QIcon(":icons/crown.png")
        elif self.type == self.Comment:
            return QtGui.QIcon(":icons/openmolar.png")

        return QtGui.QIcon(":icons/openmolar.png")

    @property
    def text(self):
        text = "unknown item!"
        if self.type == self.Filling:
            text = "%s,%s"% (self.display_surfaces, self.material)
        elif self.type == self.Crown:
            # lookup the crown in known types.. else give it straight
            crown_dict = SETTINGS.OM_TYPES["crowns"].readable_dict
            text = crown_dict.get(self.crown_type, self.crown_type)
        elif self.type == self.Root:
            if self.has_rct:
                text = _("Root Treated")
            else:
                root_dict = SETTINGS.OM_TYPES["root_description"].readable_dict
                text = root_dict.get(self.root_type, self.root_type)
        elif self.type == self.Comment:
            return self.comment

        return text

    def from_fill_string(self, arg):
        '''
        takes "MOD,CO" and converts it to a property
        '''
        try:
            surfaces, self.material = arg.split(",")
            self.set_surfaces(surfaces)
        except TypeError:
            pass
        except ValueError:
            pass

    def from_user_input(self, input, find_code=True):
        '''
        this input has come from a line edit.. so has to be checked for sanity
        '''

        if input.startsWith("CR"):
            self.parse_crown_input(input)
        elif input.startsWith("R"):
            if input == "RT": # a shortcut for the lazy
                input = "R,RT"
            self.parse_root_input(input)
        elif input.startsWith("#"):
            self.parse_comment_input(input)
        else:
            input = self.parse_fill_input(input)

        if find_code:
            self.proc_code = \
                SETTINGS.PROCEDURE_CODES.convert_user_shortcut(input)

    def from_proc_code(self, code):
        '''
        this input has come from a procedure code
        '''
        self.proc_code = code
        shortcut = SETTINGS.PROCEDURE_CODES.convert_to_user_shortcut(code)
        self.from_user_input(shortcut, False)

    def from_treatment_item(self, treatment_item):
        '''
        this input has come from a treatment_item
        (which is a class generated by a dialog which adds necessary data to
        a procedure code)
        '''
        if treatment_item.is_fill:
            self.proc_code = treatment_item.code
            input = QtCore.QString(treatment_item.surfaces)
            self.parse_fill_input(input)
        else:
            self.from_proc_code(treatment_item.code)


    def parse_fill_input(self, input, decode=True):
        input_list = input.split(",")

        surf = input_list[0]
        if decode:
            if self.tooth.is_upper:
                surf = surf.replace("L","X") #garbage entered.. ensure error fires
                surf = surf.replace("P","L")
            if self.tooth.is_fronttooth:
                surf = surf.replace("O","X") #garbage entered.. ensure error fires
                surf = surf.replace("I","O")
        if not re.match("[MODBL]{1,5}$", surf):
            raise ToothDataError("one or more invalid filling surface")
        if len(set(surf)) != len(surf):
            raise ToothDataError("duplicate surfaces found")
        self.surfaces = surf
        try:
            material = input_list[1]
            if not material in SETTINGS.allowed_fill_materials:
                raise IndexError
            self.material = material
        except IndexError:
            self.material = self.tooth.default_material

        return "%s,%s"% (self.surfaces, self.material)

    def parse_crown_input(self, input):
        input_list = input.split(",")

        surfs = input_list[0].split("/")
        input_list[0] = surfs[0]
        if len(surfs) > 1:
            self.surfaces = surfs[1]
        if input_list[0] != "CR":
            raise ToothDataError(
            "bad crown input, format is CR[/surfaces],[type]")
        self.set_type(self.Crown)
        try:
            crown_type = input_list[1]
            if not crown_type in SETTINGS.allowed_crown_types:
                raise IndexError
        except IndexError:
            crown_type = SETTINGS.allowed_crown_types[-1]

        self.crown_type = unicode(crown_type)

    def parse_root_input(self, input):
        input_list = input.split(",")
        if input_list[0] != "R":
            raise ToothDataError("bad root input, format is R,[type]")

        self.set_type(self.Root)
        try:
            root_type = input_list[1]
            if not root_type in SETTINGS.allowed_root_types:
                raise IndexError
            self.has_rct = root_type == "RT"

        except IndexError:
            root_type = SETTINGS.allowed_root_types[-1]

        self.root_type = unicode(root_type)

    def parse_comment_input(self, input):
        self.set_type(self.Comment)
        self.comment = unicode(input).strip("#")

    @property
    def display_surfaces(self):
        '''
        convert from om_datatype
        (where P and I are stored as L and O respcetively)
        '''
        surf = self.surfaces[:]
        if self.tooth:
            if self.tooth.is_upper:
                surf = surf.replace("L","P")
            if self.tooth.is_fronttooth:
                surf = surf.replace("O","I")
        return surf

    @property
    def fill_material(self):
        return self.material


if __name__ == "__main__":
    prop = ToothData()
    print dir(prop)