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

'''
Provides a data type to store how fields are presented in a dialogs
'''

class EditableField(object):
    '''
    custom data type
    '''
    def __init__(self, fieldname, readable_fieldname, required=False):
        self.fieldname = fieldname
        self.readable_fieldname = readable_fieldname
        self.required = required
        self.type = None
        self.advanced = False # set to true if field is hidden by default

    def set_type(self, type_):
        self.type = type_

    def set_advanced(self, advanced=True):
        self.advanced = advanced

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")

    ef = EditableField("addr1", _("Address Line 1"))
    print ef
