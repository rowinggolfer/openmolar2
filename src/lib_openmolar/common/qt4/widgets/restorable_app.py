#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
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

import sys
from PyQt4 import QtCore, QtGui

class Signaller(QtCore.QObject):
    notification_signal = QtCore.pyqtSignal(object, object)
    def __init__(self, parent=None):
        QtCore.QObject.__init__(self, parent)
        self.emit = self.notification_signal.emit
        self.connect = self.notification_signal.connect

class RestorableApplication(QtGui.QApplication):
    '''
    A subclass which play ball if app state is to be remembered by an X11
    Session manager.
    Will write settings to ~/.config/application_name on linux systems
    '''
    def __init__(self, name):
        '''
        the name given here is important as is used in saving the settings
        '''
        #super(RestorableApplication, self).__init__(sys.argv)
        QtGui.QApplication.__init__(self, sys.argv)
        self.setOrganizationName(name)
        self.setApplicationName(name)

    def commitData(self, session):
        '''re-implement this method, called on quit'''
        pass

    def saveState(self, session):
        '''re-implement this method, called on run'''
        pass

class SignallingApplication(RestorableApplication):
    '''
    RestorableApplication with an extra attribute db_signaller
    '''
    def __init__(self, name='test_signalling_application'):
        RestorableApplication.__init__(self, name)
        self.db_signaller = Signaller(self)


if __name__ == "__main__":
    app = RestorableApplication("test_organisation_name")
    app.closeAllWindows()
    def sig_catcher(*args):
        print (args)

    app = SignallingApplication("test_organisation_name")
    app.db_signaller.connect(sig_catcher)
    app.db_signaller.emit("foo", "bar")
    app.closeAllWindows()
