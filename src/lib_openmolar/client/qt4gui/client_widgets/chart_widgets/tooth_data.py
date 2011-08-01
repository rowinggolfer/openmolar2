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
from lib_openmolar.client.classes import Tooth


class ToothDataError(Exception):
    '''
    a custom exception
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ToothData(object):
    '''
    a custom object which holds information about a filling, crown or comment
    NOTE - filled surfaces are stored as MODBL -
    so I and P surfaces are translated if used for user interaction.

    This class can be displayed by a variety of views, namely
    :doc:`ChartWidgetBase` (and it's ancestors)
    or :doc:`ToothDataEditor`
    '''
    #:
    FILLING = 0
    #:
    CROWN = 1
    #:
    ROOT = 2
    #:
    COMMENT = 3

    #: default is None
    type = None

    def __init__(self, tooth_id):
        '''
        :param: int

        .. note::
            tooth id should comply with :doc:`../../misc/tooth_notation`

        '''
        #:
        self.tooth_id = tooth_id
        self._tooth = None
        #:
        self.in_database = False
        #:
        self.error_message = ""

        #attributes when data is a filling
        self._surfaces = ''
        self._material = ''
        self._surfaces_to_draw = None #private attribute

        #attributes when data is a crown
        self._crown_type = ''
        self._technition = ''

        self.root_type = ''
        '''attributes when data is a root'''

        #common to all types
        self._comment = ''
        #:
        self.proc_code = None
        #:
        self.svg = None

    @property
    def tooth(self):
        '''
        the :doc:`Tooth` for this data
        '''
        if self._tooth is None:
            self._tooth = Tooth(self.tooth_id)
        return self._tooth

    @property
    def surfaces(self):
        return self._surfaces

    @property
    def material(self):
        return self._material

    def set_material(self, material):
        self._material = material

    @property
    def crown_type(self):
        return self._crown_type

    @property
    def technition(self):
        return self._technition

    def set_technition(self, technition):
        self._technition = technition

    @property
    def comment(self):
        return self._comment

    def set_comment(self, comment):
        self._comment = comment

    @property
    def is_valid(self):
        if self.is_fissure_sealant:
            return True
        elif self.type == self.FILLING:
            return self.surfaces != ""
        elif self.type == self.CROWN:
            return self.crown_type !=""
        return False

    def set_type(self, type):
        self.type = type

    @property
    def is_fissure_sealant(self):
        return self.type == self.FILLING and self.material == "FS"

    @property
    def is_fill(self):
        return self.type == self.FILLING

    @property
    def is_crown(self):
        return self.type == self.CROWN

    @property
    def is_root(self):
        return self.type == self.ROOT

    @property
    def is_comment(self):
        return self.type == self.COMMENT

    def set_crown_type(self, crown_type):
        if not self.is_crown:
            raise ToothDataError("This is not a crown")
        self._crown_type = crown_type

    def set_root_type(self, root_type):
        if not self.is_root:
            raise ToothDataError("This is not a root")
        self.root_type = root_type

    def set_surfaces(self, surfaces):
        if not self.is_fill:
            raise ToothDataError("This is not a filling")
        self._surfaces = surfaces

    def set_material(self, material):
        self._material = material

    @property
    def surfaces_to_draw(self):
        '''
        this value is the surfaces mirrored to allow quadrant agnostic
        values.

        essentially this converts the surfaces to what they would be if the
        tooth were in the upper right quadrant.
        '''
        if self._surfaces_to_draw:
            return self._surfaces_to_draw

        #only do this once.
        ds = self.surfaces[:]
        if self.tooth.quadrant in (2,3):  #mirror left/right
            ds = ds.replace("M","m").replace("D","M").replace("m","D")
        if self.tooth.quadrant in (3,4):  #mirror up/down
            ds = ds.replace("B","b").replace("L","B").replace("b","L")

        self._surfaces_to_draw = ds
        return ds

    @property
    def brush(self):
        '''
        a QtGui.QBrush instance
        '''
        if self.is_fill:
            return QtGui.QApplication.instance().palette().buttonText()
        else:
            return QtGui.QApplication.instance().palette().dark()

    @property
    def icon(self):
        if self.is_fissure_sealant:
            return QtGui.QIcon(":icons/fissure_sealant.png")
        elif self.is_fill:
            return QtGui.QIcon(":icons/filling.png")
        elif self.is_root:
            return QtGui.QIcon(":icons/root.png")
        elif self.is_crown:
            return QtGui.QIcon(":icons/crown.png")
        elif self.is_comment:
            return QtGui.QIcon(":icons/openmolar.png")

        return QtGui.QIcon(":icons/openmolar.png")

    @property
    def text(self):
        '''
        a human readable description of this data
        '''
        text = "unknown item!"
        if self.is_fissure_sealant:
            return _("fissure sealant")
        elif self.type == self.FILLING:
            text = "%s,%s"% (self.display_surfaces, self.material)
        elif self.type == self.CROWN:
            # lookup the crown in known types.. else give it straight
            crown_dict = SETTINGS.OM_TYPES["crowns"].readable_dict
            text = crown_dict.get(self.crown_type, self.crown_type)
        elif self.type == self.ROOT:
            root_dict = SETTINGS.OM_TYPES["root_description"].readable_dict
            text = root_dict.get(self.root_type, self.root_type)
        elif self.type == self.COMMENT:
            text = self.comment

        return text

    def from_fill_string(self, fill_string):
        '''
        :param: fill_string (string)

        takes "MOD,CO" and converts it to a property
        '''
        if fill_string.startswith("FS"):
            self.set_type(self.FILLING)
            self._material = "FS"
            return

        try:
            surfaces, self._material = fill_string.split(",")
            self.set_type(self.FILLING)
            self.set_surfaces(surfaces)
        except TypeError:
            pass
        except ValueError:
            pass

    def from_user_input(self, input):
        '''
        :param: input (QString)

        this input has come from a line edit.. so has to be checked for sanity
        '''

        SETTINGS.debug_log("from_user_input", input)

        if input.startsWith("CR"):
            self.parse_crown_input(input)
        elif input.startsWith("R"):
            if input == "RT": # a shortcut for the lazy
                input = "R,RT"
            self.parse_root_input(input)
        elif input.startsWith("#"):
            self.parse_comment_input(input)
        elif input == "FS":
            self.from_fill_string("FS")
        else:
            input = self.parse_fill_input(input)

        self.proc_code = SETTINGS.PROCEDURE_CODES.convert_user_shortcut(input)

    def from_treatment_item(self, treatment_item):
        '''
        this input has come from a treatment_item
        (which is a class generated by a dialog which adds necessary data to
        a procedure code)
        '''
        self.proc_code = treatment_item.code
        if treatment_item.is_fill:
            self.set_type(self.FILLING)
            self.set_surfaces(treatment_item.surfaces)
            self.set_material(treatment_item.material)

        elif treatment_item.is_crown:
            self.set_type(self.CROWN)
            self.set_crown_type(self.proc_code.crown_type)

        elif treatment_item.is_root:
            self.set_type(self.ROOT)
            self.set_root_type("unknown")
            #TODO - this should be more comprehensive
        else:
            SETTINGS.log("unknown ToothData type during from_treatment_item")
            raise ToothDataError("unable to create ToothData from %s"% (
                treatment_item))

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

        self.set_type(self.FILLING)
        self._surfaces = surf
        try:
            material = input_list[1]
            if not material in SETTINGS.allowed_fill_materials:
                raise IndexError
            self._material = material
        except IndexError:
            self._material = self.tooth.default_material

        return "%s,%s"% (self.surfaces, self.material)

    def parse_crown_input(self, input):
        input_list = input.split(",")

        surfs = input_list[0].split("/")
        input_list[0] = surfs[0]
        if len(surfs) > 1:
            self._surfaces = surfs[1]
        if input_list[0] != "CR":
            raise ToothDataError(
            "bad crown input, format is CR[/surfaces],[type]")
        self.set_type(self.CROWN)
        try:
            crown_type = input_list[1]
            if not crown_type in SETTINGS.allowed_crown_types:
                raise IndexError
        except IndexError:
            crown_type = SETTINGS.allowed_crown_types[-1]

        self._crown_type = unicode(crown_type)

    def parse_root_input(self, input):
        input_list = input.split(",")
        if input_list[0] != "R":
            raise ToothDataError("bad root input, format is R,[type]")

        self.set_type(self.ROOT)
        try:
            root_type = input_list[1]
            if not root_type in SETTINGS.allowed_root_types:
                raise IndexError

        except IndexError:
            root_type = SETTINGS.allowed_root_types[-1]

        self.root_type = unicode(root_type)

    def parse_comment_input(self, input):
        self.set_type(self.COMMENT)
        self.set_comment(unicode(input).strip("#"))

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


    def __repr__(self):
        if self.is_fill:
            return "ToothData FILLING tooth_id=%s surfaces=%s material=%s"% (
                self.tooth_id, self.surfaces, self.material)
        if self.is_crown:
            return "ToothData CROWN tooth_id=%s type=%s"% (
                self.tooth_id, self.type)

        return "ToothData Instance tooth_id=%s"% self.tooth_id
