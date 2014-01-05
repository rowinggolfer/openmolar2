#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
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

class Tooth(object):
    '''
    this simple class is initiated with an id, but will then be aware of
    how dentists may refer to it
    '''
    def __init__(self, tooth_id):
        '''
        :param: int should conform to :doc:`../../misc/tooth_notation`
        '''
        self.tooth_id = tooth_id

    @property
    def long_name(self):
        return SETTINGS.TOOTHGRID_LONGNAMES.get(self.tooth_id, "???")

    @property
    def short_name(self):
        return SETTINGS.TOOTHGRID_SHORTNAMES.get(self.tooth_id, "???")

    @property
    def is_deciduous(self):
        return (self.tooth_id !=0 and self.tooth_id in SETTINGS.DECIDUOUS)

    @property
    def is_upper(self):
        return (self.tooth_id in SETTINGS.TOOTH_GRID[0] or
            self.tooth_id in SETTINGS.TOOTH_GRID[1])

    @property
    def is_lower(self):
        return not self.is_upper

    @property
    def is_backtooth(self):
        return self.tooth_id in SETTINGS.back_teeth

    @property
    def is_fronttooth(self):
        return self.tooth_id in SETTINGS.front_teeth

    @property
    def is_rightside(self):
        for row in SETTINGS.TOOTH_GRID:
            if self.tooth_id in row and row.index(self.tooth_id) < 8:
                return True
        return False

    @property
    def default_material(self):
        if self.is_backtooth:
            return "AM"
        else:
            return "CO"

    @property
    def quadrant(self):
        '''
        property declaring which quadrant the tooth is in 1,2,3,4
        '''
        if self.is_upper:
            quad = 1 if self.is_rightside else 2
        else:
            quad = 4 if self.is_rightside else 3
        return quad


if __name__ == "__main__":
    tooth = Tooth(1)
    print tooth.quadrant
