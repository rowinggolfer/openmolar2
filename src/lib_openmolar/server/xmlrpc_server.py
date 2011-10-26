#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011, Neil Wallace <rowinggolfer@googlemail.com>               ##
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


from SimpleXMLRPCServer import SimpleXMLRPCServer

import commands
import datetime
import subprocess

HOST = commands.getoutput("hostname -I").split(" ")[0]

PORT = 42230

LOG = "/var/log/openmolar2/server_log"

def pretty(title, data):
    if len(title)//2 == 1:
        title += " "
    i = 39 - len(title)//2
    header = "%s %s %s"% ("="*i, title, "="*i)
    return "%s\n%s\n%s\n\n"% (header, data, "="*80) 

class MyFuncs(object):
    '''
    A class whose functions will be inherited by the server
    '''
    def last_backup(self):
        '''
        returns a iso formatted datetime string showing when the
        last backup was made
        '''
        return datetime.datetime.now().isoformat()

    def init_db(self):
        '''
        initialises the database, creating a demo database, and default users
        '''
        f = open(LOG, "a")
        f.write("init_db called")
        f.flush()
        p = subprocess.Popen(["openmolar_initdb"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        p.wait()
        
        data = "%s%s"% (
            pretty("OUTPUT", p.stdout.read()),
            pretty("ERRORS", p.stderr.read()))
        f.write(data)
        f.close()
        
        return data


def main():

    server = SimpleXMLRPCServer((HOST, PORT))
    print "listening on %s:%d"% (HOST, PORT)

    server.register_instance(MyFuncs())

    server.serve_forever()

if __name__ == "__main__":

    main()
