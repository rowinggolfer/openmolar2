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
provides one 'private' class DiaryAppointment
'''

class DiaryAppointment(object):
    def __init__(self, record): #date, hour, minute, length, name):
        self.start = record.value("start").toDateTime()
        self.finish =  record.value("finish").toDateTime()
        self.type = record.value('type').toString()
        self.comments = record.value('comments').toString()
        self.rect = None

    @property
    def message(self):
        return u"%s %s"% (self.type, self.comments)

    @property
    def full_details(self):
        return u"%s %s %s"% (self.start.toString(), self.type, self.comments)

    def __repr__(self):
        return "appointment %s %s %s %s"% (
            self.start, self.finish, self.type, self.comments)


