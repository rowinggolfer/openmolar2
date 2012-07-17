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
provides one 'private' class _DiarySettings
'''

class _DiarySettings(object):
    '''
    this class provides a base class with useful attributes, and is
    intended to be subclassed.
    '''
    DAY = 0
    FOUR_DAY = 1
    WEEK = 2
    FORTNIGHT = 3
    MONTH = 4
    YEAR = 5
    AGENDA = 6
    TASKS = 7

    DAY_VIEWS = (DAY, FOUR_DAY, WEEK, FORTNIGHT)

    def __init__(self):
        self._style = self.DAY

    def set_style(self, style):
        assert style>=self.DAY and style<=self.TASKS, \
            "unknown diary style type"
        self._style = style
