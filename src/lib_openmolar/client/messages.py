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


import re

class Messages(object):
    '''
    this is simply a holder for a few translatable messages displayed to the 
    user.
    It's a class so to ensure that gettext is initiated before the messages
    are constructed.
    '''
    def __init__(self):
        pass

    @property
    def wide_welcome_html(self):
        str = '''<html><body><div align='center'>
        <img align='left' height='100' width='100'
        src='qrc:/icons/openmolar-server.png' />
        <img align='right' height='100' width='100'
        src='qrc:/icons/openmolar.png' />
        '''
        str += _('Welcome to OpenMolar')
        str += '</div></body></html>'''

        return str

    def welcome_html(self, width=400):
        if width < 400:
            return re.sub("<img[^>]*>","", self.wide_welcome_html, 1)
        else:
            return self.wide_welcome_html

messages = Messages()

if __name__ == "__main__":
    
    print messages.welcome_html()
