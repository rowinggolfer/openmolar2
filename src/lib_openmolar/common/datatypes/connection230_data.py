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
A custom datatype, capable of parsing conf files
'''

import ConfigParser
import os

class Connection230Data(object):
    '''
    A custom data type to store information on how applications can connect
    to the 230server.
    '''
    name = ""
    host = ""
    port = 230

    def default_connection(self):
        '''
        returns params for a TCP_IP connection on localhost:5432 to
        openmolar_demo with the default user and password.
        '''
        self.name = "defaulting to localhost"
        self.host = "localhost"
        self.port = 230

    def from_conf_file(self, conf_file):
        '''
        parse a conf_filefor connection params
        '''
        f = open(conf_file)
        parser = ConfigParser.SafeConfigParser()
        parser.readfp(f)

        self.name = os.path.basename(conf_file)
        self.host = parser.get("CONNECTION", "host")
        self.port = parser.getint("CONNECTION", "port")
        f.close()

    def __repr__(self):
        return "Connection230Data - '%s' %s %s"% (
            self.name, self.host, self.port)

    def __cmp__(self, other):
        def str_atts(obj):
            return "%s%s"% (obj.host, obj.port)

        return cmp(str_atts(self), str_atts(other))

def _test():
    import gettext
    gettext.install("")

    obj = Connection230Data()
    obj.default_connection()
    print obj

    obj2 = Connection230Data()
    obj2.from_conf_file("/etc/openmolar/admin/230connections/localhost")

    print obj2

    #check cmp function
    obj == obj2

if __name__ == "__main__":
    _test()
