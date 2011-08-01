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

'''
this module provides one class, ProcCode

ProcCode is a class which encapsulates a treatment procedure known to openmolar

as an example, such an object may represent a 3 surface amalgam filling.

this only becomes a treatment item, when it is planned or performed on a
specific tooth on a specific patient.
'''

import re

class ProcCode(object):
    #:
    SIMPLE = 0
    #:
    TOOTH = 1
    #:
    ROOT = 2
    #:
    FILL = 3
    #:
    CROWN = 4
    #:
    BRIDGE = 5
    #:
    PROSTHETICS = 6
    #:
    OTHER = 7

    def __init__(self, element, category):
        #:
        self.category = category

        self.element = element
        '''
        A pointer to the minidom element which holds the info about this code
        '''

        self._category = None
        self._type = None
        self._description = None
        self._code = None

    @property
    def is_chartable(self):
        '''
        can this procedure be displayed on a dental chart?
        note::
            this needs more work!

        '''
        return self.type in (self.FILL, self.CROWN, self.ROOT)

    @property
    def type(self):
        if self._type is None:
            type = self.element.attributes["type"].value
            if type == "simple":
                self._type = self.SIMPLE
            elif type == "tooth":
                self._type = self.TOOTH
            elif type == "teeth":
                self._type = self.TOOTH
                self._multi_teeth = True
            elif type == "root":
                self._type = self.ROOT
            elif type == "fill":
                self._type = self.FILL
            elif type == "crown":
                self._type = self.CROWN
            elif type == "prosthetics":
                self._type = self.PROSTHETICS
            elif type == "bridge":
                self._type = self.BRIDGE
            else:
                print "WARNING - illegal proc-code type", type

        return self._type

    @property
    def code(self):
        if self._code is None:
            self._code = self.element.getElementsByTagName(
                "id")[0].childNodes[0].data
        return self._code

    @property
    def description(self):
        if self._description is None:
            self._description = self.element.getElementsByTagName(
                "description")[0].childNodes[0].data

        return self._description

    @property
    def is_fill(self):
        return self.type == self.FILL

    @property
    def is_crown(self):
        return self.type == self.CROWN

    @property
    def is_root(self):
        return self.type == self.ROOT

    @property
    def is_tooth(self):
        return (
            self.is_bridge or
            self.is_crown or
            self.is_fill or
            self.is_root or
            self.type == self.TOOTH
            )

    @property
    def is_bridge(self):
        return self.type == self.BRIDGE

    @property
    def is_prosthetics(self):
        return self.type == self.PROSTHETICS

    @property
    def description_required(self):
        '''
        some items require an extra description from the user when
        converting to a :doc:`TreatmentItem`
        eg. "other treatment" code needs embellishing
        '''
        return "description" in self.treatment_item_requirements

    @property
    def treatment_item_requirements(self):
        '''
        the xml config sheet can speculate what is needed to create a valid
        :doc:`TreatmentItem` from this code
        '''
        require_nodes = self.element.getElementsByTagName("ti_requires")
        if require_nodes == []:
            return []
        return require_nodes[0].childNodes[0].data.strip().split(",")

    @property
    def tooth_required(self):
        '''
        this is a property indicating that to become a treatment item
        a tooth is required.
        this is, for example, the case with an MOD filling,
        but not needed for an examination
        '''
        return self.is_tooth

    @property
    def multi_tooth(self):
        return self._multi_teeth

    @property
    def surfaces_required(self):
        return self.no_surfaces != "0"

    @property
    def _surface_node(self):
        surface_nodes = self.element.getElementsByTagName("surfaces")
        if surface_nodes != []:
            return surface_nodes[0]

    @property
    def no_surfaces(self):
        surf_node = self._surface_node
        if surf_node is None:
            return "0"
        return surf_node.attributes["n"].value

    @property
    def pontics_required(self):
        return self.no_pontics != "0"

    @property
    def _pontics_node(self):
        pontics_nodes = self.element.getElementsByTagName("pontics")
        if pontics_nodes != []:
            return pontics_nodes[0]

    @property
    def no_pontics(self):
        pontics_node = self._pontics_node
        if pontics_node is None:
            return "0"
        return pontics_node.attributes["n"].value

    @property
    def allowed_pontics(self):
        '''
        a list of teeth which can be replaced with this procedure
        (eg upper teeth only for a P/-)
        '''
        if self._allowed_pontics != None:
            return self._allowed_pontics
        return SETTINGS.all_teeth

    @property
    def _span_node(self):
        span_nodes = self.element.getElementsByTagName("span")
        if span_nodes != []:
            return span_nodes[0]

    @property
    def total_span(self):
        '''
        returns the span of a bridge
        this is a string, so as to allow values like "3+"
        '''
        if self.is_bridge:
            span_node = self._span_node
            if span_node is None:
                return "0"
            return span_node.attributes["n"].value

    @property
    def material(self):
        if not self.is_fill:
            return
        if "fissure sealant" in self.description.lower():
            return "FS"
        if "amalgam" in self.description.lower():
            return "AM"
        if "composite" in self.description.lower():
            return "CO"
        if "gold" in self.description.lower():
            return "GO"
        if "glass" in self.description.lower():
            return "GL"
        if "porc" in self.description.lower():
            return "PO"
        return "OT"

    @property
    def crown_type(self):
        '''
        the code expected by a :doc:`ToothData` object so that an item
        of this type can be drawn correctly
        '''
        if not self.is_crown:
            return
        return "GO"

    @property
    def further_info_needed(self):
        return (self.tooth_required or
            self.surfaces_required or
            self.description_required or
            self.pontics_required)

    @property
    def allowed_teeth(self):
        print "ProcCode.allowed_teeth called"
        return range(1,33)

    def __repr__(self):
        return "ProcCode - %s"% self.__str__()

    def __str__(self):
        return  u"%s %s %s"% (
            self.category.ljust(28), self.code, self.description.ljust(40))

    def __cmp__(self, other):
        try:
            return cmp(self.code, other.code)
        except AttributeError as e:
            return -1
