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
A custom datatype, capable of parsing conf files in the following format

'''

import ConfigParser

class ConnectionData(object):
    '''
    A custom data type to store information on how the application can connect
    to a postgres database.
    '''
    #:
    TCP_IP = 0
    #:
    SOCKET = 1

    CONNECTION_TYPE = TCP_IP
    '''
    the default connection is TCP/IP
    (ie. username and password connection to a specific database name
    on a known host and port)
    '''

    def __init__(self, connection_name="", user="", password="", host="",
    port=5432, db_name=""):

        self._connection_name = connection_name

        #:
        self.user = user
        #:
        self.password = password
        #:
        self.host = host
        #:
        self.port = port
        #:
        self.db_name = db_name

    def demo_connection(self):
        '''
        returns params for a TCP_IP connection on localhost:5432 to
        openmolar_demo with the default user and password.
        '''
        self.CONNECTION_TYPE = self.TCP_IP
        self._connection_name = "openmolar_demo"
        self.user = "om_demo"
        self.password = "password"
        self.host = "localhost"
        self.port = 5432
        self.db_name = "openmolar_demo"

    def from_conf_file(self, conffile):
        '''
        parse a conf_filefor connection params
        '''
        f = open(conffile)
        parser = ConfigParser.SafeConfigParser()
        parser.readfp(f)

        if parser.get("CONNECTION", "type") == "TCP/IP":
            self._from_tcpconf(parser)
        else:
            raise IOError("unable to parse %s"% f)

    def _from_tcpconf(self, parser):
        '''
        populate params from a config where the connection type is tcp/ip
        '''
        self.CONNECTION_TYPE = self.TCP_IP
        self._connection_name = parser.get("CONNECTION", "name")
        self.user = parser.get("CONNECTION", "user")
        self.password = parser.get("CONNECTION", "password")
        self.host = parser.get("CONNECTION", "host")
        self.port = parser.getInt("CONNECTION", "port")
        self.db_name = parser.get("CONNECTION", "db_name")

    @property
    def brief_name(self):
        '''
        a short, readable name for this connection.
        '''
        return "'%s'" % self._connection_name

    @property
    def connection_name(self):
        '''
        a detailed, readable name for this connection.
        '''
        if self.CONNECTION_TYPE == self.TCP_IP:
            return "'%s' %s on %s:%s"% (
                self._connection_name, self.user, self.host, self.port)
        return "?? connection type, %s"% self._connection_name

    def set_connection_name(self, name):
        '''
        set a readable name for this connection
        '''
        self._connection_name = name

    def __repr__(self):
        return "ConnectionData - '%s'"% self.connection_name

    def __cmp__(self, other):
        def str_atts(obj):
            return "%s%s%s%s%s%s%s"% (
            obj.connection_name,
            obj.user,
            obj.password,
            obj.host,
            obj.port,
            obj.db_name,
            obj.CONNECTION_TYPE)

        return cmp(str_atts(self), str_atts(other))

def _test():
    import gettext
    gettext.install("")

    obj = ConnectionData()
    obj.demo_connection()

    obj2 = ConnectionData()
    obj2.from_confile("/home/neil/.openmolar2/connections-enabled/demo.conf")

    print obj == obj2

if __name__ == "__main__":
    _test()
