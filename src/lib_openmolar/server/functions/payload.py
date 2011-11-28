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

import logging

class PayLoad(object):
    '''
    A wrapper for any server response.
    '''
    def __init__(self, method):
        self.method = method
        self.permission = False
        self._payload = None

    def __repr__(self):
        return "PAYLOAD - permission='%s', method='%s', payload_type=%s"% (
            self.permission, self.method, type(self.payload))

    @property
    def payload(self):
        if not self.permission:
            return None
        return self._payload

    def set_payload(self, payload):
        self._payload = payload

    @property
    def error_message(self):
        if not self.permission:
            return "You do not have sufficient privileges to call %s"% (
                self.method)
        return ""

def _test():
    '''
    test the PayloadClass
    '''
    def method():
        return "success"
    logging.basicConfig(level=logging.DEBUG)
    pl = PayLoad(method)
    logging.debug("payload = '%s'"% pl.payload)
    pl.permission=True
    pl.set_payload(method())
    logging.debug("payload = '%s'"% pl.payload)

if __name__ == "__main__":
    from gettext import gettext as _
    _test()
