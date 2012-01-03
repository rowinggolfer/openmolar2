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

class ConnectionData(object):
    '''
    A custom data type to store connection information
    '''
    def __init__(self, human_name="", username="", password="", host="",
    port="", db_name=""):
        self.human_name = human_name
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.is_default = False
        self.remember = False
        self.remember_pass = False

    def demo_connection(self):
        self.human_name = "demo"
        self.username = "om_demo"
        self.password = "password"
        self.host = "localhost"
        self.port = 5432
        self.db_name = "openmolar_demo"
        self.is_default = False
        self.remember = True
        self.remember_pass = True

    @property
    def name(self):
        name = u"%s"% self.name_  #a copy
        try:
            if self.is_default:
                name += " (%s)"% _("default")
        except AttributeError:
            pass
        return name

    @property
    def name_(self):
        val = u"%s %s@%s:%s"% (
            self.db_name, self.username, self.host, self.port)
        return val.strip()

    def __repr__(self):
        return self.name_

    def __cmp__(self, other):
        return cmp(self.name_, other.name_)

if __name__ == "__main__":
    import gettext
    gettext.install("")

    obj = ConnectionData()
    print obj