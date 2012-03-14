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

from PyQt4 import QtGui, QtCore

from lib_openmolar.common.qt4.postgres.postgres_session_widget import \
    PostgresSessionWidget

class ClientSessionWidget(QtGui.QStackedWidget, PostgresSessionWidget):
    '''
    This widget is both the central widget for the client gui,
    and a Session Widget.
    '''

    def __init__(self, parent=None):
        QtGui.QStackedWidget.__init__(self, parent)
        PostgresSessionWidget.__init__(self, parent)

    def setup_ui(self):
        pass

    def add(self, widget, session_name):
        '''
        the addTab method
        '''
        QtGui.QStackedWidget.addWidget(self, widget)
        LOGGER.debug("added widget %s for session %s"% (widget, session_name))

    def update_status(self):
        '''
        let the user know the connection state
        '''
        brief, verbose = self.get_session_status()
        try:
            self.parent().setWindowTitle(brief)
        except:
            LOGGER.warning("unable to set client session widget title")

    def set_session(self, session):
        PostgresSessionWidget.set_session(self, session)
        self.update_status()

def _test():
    from lib_openmolar.client.connect import DemoClientConnection
    app = QtGui.QApplication([])
    session = DemoClientConnection()
    session.connect()
    csw = ClientSessionWidget()
    csw.set_session(session)
    csw.show()
    app.exec_()

if __name__ == "__main__":
    import logging
    LOGGER = logging.getLogger()

    import gettext
    gettext.install("openmolar")
    _test()
