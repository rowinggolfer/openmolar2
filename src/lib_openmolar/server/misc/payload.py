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

class PayLoad(object):
    '''
    A wrapper for any server response.
    '''
    def __init__(self, method):
        self.method = method
        self.permission = False
        self._payload = None
        self._exception = None

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

    def set_exception(self, exc):
        self._exception = exc
    
    @property
    def exception(self):
        return self._exception
    
    @property
    def exception_message(self):
        if self.exception:
            return str(self._exception)
        return None
    
    @property
    def error_message(self):
        if self.exception_message is not None:
            return self.exception_message
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
    pl = PayLoad(method)
    LOGGER.debug("payload = '%s'"% pl.payload)
    pl.permission=True
    pl.set_payload(method())
    LOGGER.debug("payload = '%s'"% pl.payload)

if __name__ == "__main__":
    from gettext import gettext as _
    import logging
    logging.basicConfig(level = logging.DEBUG)
    
    LOGGER = logging.getLogger("test")
    
    _test()
