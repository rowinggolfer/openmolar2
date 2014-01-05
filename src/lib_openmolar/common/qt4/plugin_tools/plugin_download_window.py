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

from PyQt4 import QtGui, QtCore

from lib_openmolar.common.qt4.plugin_tools.online_plugins_widget \
    import OnlinePluginsWidget

class PluginDownloadWindow(QtGui.QMainWindow):
    '''
    A dialog to download plugins
    '''
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        widg = OnlinePluginsWidget()

        self.setCentralWidget(widg)

def _test():
    from lib_openmolar import client

    app = QtGui.QApplication([])
    mw = PluginDownloadWindow()
    mw.show()
    app.exec_()

if __name__ == "__main__":
    _test()
