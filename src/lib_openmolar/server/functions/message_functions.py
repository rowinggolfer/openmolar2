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

HEADER = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Server Message</title>
</head>
<body>
'''

FOOTER = '''\n</body>\n</html>'''

class MessageFunctions(object):
    '''
    A class whose functions will be inherited by the server
    '''
    def admin_welcome_template(self):
        '''
        return the html shown at admin_startup
        '''
        html = u'''%s
        <h1>%s</h1>
        <h2>%s</h2>
        %s
        <ul>{DATABASE LIST}</ul>%s'''% (HEADER,
            _("Welcome"),
            _("Connection to the Server Controller has been established."),
            _("The following databases are at your disposal"),
            FOOTER)

        return html

    def no_databases_message(self):
        return '''%s
        <h1>%s</h1>
        <h2>%s</h2>
        %s<br />%s<br />

        %s <a href="install_demo">%s</a>.<br />

        some other function <a href="function">Some other function</a>.

        %s'''%(HEADER,
        _("Welcome!"),
        _("Connection to the Server Controller has been established."),
        _("You do not appear to have any openmolar databases installed."),
        _("Would you like to install a demo database now?"),
        _("If so, please"), _("Click here"),
        FOOTER)

def _test():
    '''
    test the ShellFunctions class
    '''
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger("openmolar_server")
    sf = MessageFunctions()
    log.debug(sf.admin_welcome_template())
    log.debug(sf.no_databases_message())

if __name__ == "__main__":
    from gettext import gettext as _
    _test()
