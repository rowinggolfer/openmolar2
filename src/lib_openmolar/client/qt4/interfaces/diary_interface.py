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

from PyQt4 import QtCore, QtGui

from lib_openmolar.client.qt4.widgets import DiaryControl, DiaryWidget

from lib_openmolar.client.db_orm.diary import DiaryDataModel

class DiaryInterface(QtGui.QWidget):
    '''
    A composite widget containing all elements for viewing a patient record
    '''
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.diary_control = DiaryControl()
        self.diary_widget = DiaryWidget()

        self.model = DiaryDataModel()

        self.diary_widget.setModel(self.model)

        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.addWidget(self.diary_control)
        layout.addWidget(self.diary_widget)
        self.connect_signals()

    def sizeHint(self):
        return QtCore.QSize(500, 400)

    def connect_signals(self):
        self.diary_control.date_changed.connect(self.diary_widget.set_date)
        self.diary_control.view_changed.connect(self.diary_widget.setViewStyle)

    def refresh(self):
        '''
        usually called when the database has connected/changed
        '''
        self.diary_control.refresh_practitioners(SETTINGS.practitioners)
        self.diary_control.refresh_staff_members(SETTINGS.staff_members)
        self.model.load()
        self.diary_control.set_limits(self.model.start_date,
            self.model.end_date)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

if __name__ == "__main__":

    app = QtGui.QApplication([])
    mw = QtGui.QMainWindow()
    mw.setMinimumSize(500,300)

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    di = DiaryInterface(mw)
    di.refresh()

    mw.setCentralWidget(di)
    mw.show()
    app.exec_()