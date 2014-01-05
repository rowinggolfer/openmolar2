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

'''
provides the ProxyUser class.
'''
import socket
import time
import xmlrpclib

class ProxyUser(object):
    '''
    a custom data type to hold the user details for connection to the
    openmolar-server.
    Will expire permission after 10 minutes.
    '''
    _creation_time = None

    #:
    timeout = 600

    def __init__(self, name=None, psword=None):
        if name is None and psword is None:
            name, psword = "default", "eihjfosdhvpwi"
        else:
            self._creation_time = int(time.time())
        self.name = name
        self.psword = psword

    @property
    def has_expired(self):
        '''
        privileged users get logged out after a timeout (default is 10 minutes)
        '''
        if self._creation_time is None:
            return False
        return time.time() > self._creation_time + self.timeout

