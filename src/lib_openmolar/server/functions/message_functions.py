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
import socket

CSS = '''
body {
    background-color:#ffffff;
    }

.database ul{
    padding-left: 0px;
    }
.database li{
    padding-left: 28px;
    }

.database li.header{
    list-style-type: none;
    padding-left: 12px;
    }

h1, h2, h3, h4 {color:#59212f;
	padding-bottom:0px;}

a {color:#2f2159;}
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

FOOTER = None

def get_footer():
    global FOOTER
    if FOOTER is None:

        logger = logging.getLogger("openmolar_server")

        try:
            from lib_openmolar.server import version
            VERSION = "2.0.1~hg%s"% (
                version.revision_number)
            logger.info("SERVER VERSION %s"% VERSION)
            logger.debug("VERSION DATE %s"% version.date)
            logger.debug("REVISION %s"% version.revision_id)
        except ImportError:
            VERSION = "Unknown"
            logger.exception("unable to parse for server versioning")

        FOOTER = '''\n<br /><br />
        <i>server library version %s</i></body>\n</html>'''% VERSION

    return FOOTER

class MessageFunctions(object):
    '''
    A class whose functions will be inherited by the server
    '''
    @property
    def location_header(self):
        '''
        an html header giving information about the server.
        '''
        header = "<h3>%s %s '%s'</h3>"% (_("Connected to Openmolar-Server"),
            _("on host"), socket.gethostname())
        return header

    def admin_welcome_template(self):
        '''
        return the html shown at admin_startup
        '''
        html = u'''%s
        %s
        %s
        {DATABASE LIST}
        %s'''% (HEADER, self.location_header,
            _("The following openmolar schemas are at your disposal on this postgres server"),
            get_footer())

        return html

    def no_databases_message(self):
        return '''%s
        %s
        <p>%s<br />
        %s <a href="install_demo">%s</a>.
        </p>
        <br />
        %s'''%(HEADER, self.location_header,
        _("You do not appear to have any openmolar databases installed."),
        _("To install a demo database now"), _("Click Here"),
        get_footer())

    def postgres_error_message(self):
        return '''%s
        %s
        <p>
        <b>%s</b>
        <pre>ERROR</pre>
        </p>
        <br />
        %s'''%(HEADER, self.location_header,
        _("Cannot connect to the postgres server on this machine!"),
        get_footer())

def _test():
    '''
    test the ShellFunctions class
    '''
    logging.basicConfig(level=logging.DEBUG)
    sf = MessageFunctions()
    logging.debug(sf.admin_welcome_template())
    logging.debug(sf.no_databases_message())
    logging.debug(sf.postgres_error_message())

if __name__ == "__main__":
    from gettext import gettext as _
    _test()
