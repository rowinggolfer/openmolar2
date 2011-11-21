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

CSS = '''
body {
    background-color:#cccccc;
    }

.database ul{
    padding-left: 0px;
    }
.database li{
    padding-left: 20px;
    }

.database li.header{
    width:100%;
    background-color:#333;
    color:white;
    list-style-type: none;
    padding-left: 0px;
    }
'''

HEADER = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Server Message</title>
<style type="text/css">
%s
</style>
</head>
<body>
'''% CSS

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
        %s
        {DATABASE LIST}
        %s'''% (HEADER,
            _("Welcome to Openmolar"),
            _("The following databases are at your disposal"),
            FOOTER)

        return html

    def no_databases_message(self):
        return '''%s
        <h1>%s</h1>
        <p>
            <i>%s</i><br />
        </p>
        <br />
        <p>%s<br />
        %s <a href="install_demo">%s</a>.<br />
        </p>
        <br />
        <p>
        %s
        </p>
        %s'''%(HEADER,
        _("Welcome to Openmolar"),
        _("Connection to the Server Controller has been established."),
        _("You do not appear to have any openmolar databases installed."),
        _("To install a demo database now"), _("Click Here"),
        _("Other options are available from the menu above"),
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
