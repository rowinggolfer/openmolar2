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

import re
import socket

HEADER = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Server Message</title>
</head>
<body>
'''

FOOTER = None

def get_footer():
    global FOOTER
    if FOOTER is None:

        try:
            from lib_openmolar.server import version
            VERSION = "%s~hg%s"% (version.VERSION, version.revision_number)
            LOGGER.info("SERVER VERSION %s"% VERSION)
            LOGGER.debug("VERSION DATE %s"% version.date)
            LOGGER.debug("REVISION ID %s"% version.revision_id)
        except ImportError:
            VERSION = "Unknown"
            LOGGER.exception("unable to parse for server versioning")
    
        try:
            f = open("/etc/openmolar/manager_password.txt", "r")
            PASSWORD='''
                <em>Your admin password on this server is %s</em>
                    '''% re.search("PASSWORD = (.*)", f.read()).groups()[0]
            f.close()
            
        except IOError:
            PASSWORD="admin password file unreadable. Good!"
            
        FOOTER = '''
            <div class = "footer">
            <br /><br />
            <i>server library version %s</i>
            <ul>
                <li><a href="show server log">Show Server Log</a></li>
            </ul>
            %s
            </div>
            </body>
            </html>
            '''% (VERSION, PASSWORD)

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
        header = "<div class='loc_header'><h3>%s %s '%s'</h3></div>"% (
            _("Connected to Openmolar-Server"),
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
        return u'''%s
        %s
        <p>
        <b>%s</b>
        <br />
        %s <a href="show server log">%s</a>
        
        </p>
        <br />
        %s'''%(HEADER, self.location_header,
        _("Cannot connect to the postgres server on this machine!"),
        _("further information may be found in the"),
        _("Server Log File"),
        get_footer())

    
    def message_link(self, url):
        '''
        the "url" here will be text of a link that has been displayed as
        part of the html from the server.
        '''
        
        if url == "show server log":
            f = open("/var/log/openmolar/server.log", "r")
            data = f.read()
            f.close()
            return "<html><body><pre>%s</pre></body></html>"% data
        
        return None

def _test():
    '''
    test the ShellFunctions class
    '''
    sf = MessageFunctions()
    LOGGER.debug(sf.admin_welcome_template())
    LOGGER.debug(sf.no_databases_message())
    LOGGER.debug(sf.postgres_error_message())

if __name__ == "__main__":
    from gettext import gettext as _
    import logging
    logging.basicConfig(level = logging.DEBUG)
    
    LOGGER = logging.getLogger("test")
    
    _test()
