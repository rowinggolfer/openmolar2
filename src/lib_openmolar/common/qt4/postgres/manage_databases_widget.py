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

from multiple_database_widget import MultipleDatabaseWidget

class ManageDatabasesWidget(MultipleDatabaseWidget):
    '''
    a widget, added at runtime to the preferences dialog.
    '''
    def __init__(self, parent):
        MultipleDatabaseWidget.__init__(self, parent)

        self.toplabel.setText(_("Known connections"))

        self.grid_layout.addWidget(self.list_widget, 0, 0)
        self.grid_layout.addWidget(self.details_browser,0, 1)

    def sizeHint(self):
        return QtCore.QSize(500,300)

if __name__ == "__main__":
    import gettext

    def advise(*args):
        print args

    from lib_openmolar.common.datatypes import ConnectionData

    app = QtGui.QApplication([])

    gettext.install("")

    dl = QtGui.QDialog()
    dl.advise = advise

    cd1, cd2 = ConnectionData(), ConnectionData()
    cd1.demo_connection()
    cd2.demo_connection()

    cd1.is_default = True
    obj = ManageDatabasesWidget(dl)
    obj.set_connections([cd1, cd2])

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(obj)

    dl.exec_()
