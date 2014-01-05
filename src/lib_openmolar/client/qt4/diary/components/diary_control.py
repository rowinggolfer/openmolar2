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


from PyQt4 import QtCore, QtGui

from lib_openmolar.client.qt4.diary.components import DiaryViewController
from lib_openmolar.client.qt4.diary.components import DiaryScheduleController

PADDING = 9

class DiaryControl(QtGui.QWidget):
    '''
    A widget to allow user choice of parameters to show what information
    is displayed on the diary (date, clinician etc...)
    '''

    date_changed = QtCore.pyqtSignal(object)
    '''
    signal indicating that the date has changed.
    supplies a QDate
    '''

    view_changed = QtCore.pyqtSignal(object)
    '''
    signal indicating that the user want to view a different style
    eg day, week, fortnight etc...
    '''

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.calendar = QtGui.QCalendarWidget()
        self.calendar.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.calendar.setVerticalHeaderFormat(self.calendar.NoVerticalHeader)
        self.calendar.setMaximumSize(self.calendar.minimumSizeHint())

        self.combo_box = QtGui.QComboBox(self)
        self.combo_box.addItems([_("Day"),_("Four Days"), _("Week"),
            _("Fortnight"), _("Month"), _("Year"), _("List"), ("Tasks")])

        #:
        self.diary_schedule_controller = DiaryScheduleController()

        #:
        self.diary_view_controller = DiaryViewController()

        layout = QtGui.QVBoxLayout(self)
        layout.setMargin(PADDING)
        layout.addWidget(self.combo_box)
        layout.addWidget(self.calendar)
        layout.addWidget(self.diary_schedule_controller)
        layout.addWidget(self.diary_view_controller)

        self.setMaximumWidth(self.calendar.width()+ PADDING*2)

        self.calendar.selectionChanged.connect(self.date_change)
        self.combo_box.currentIndexChanged.connect(self.view_change)

    def set_limits(self, start, end):
        self.calendar.setMinimumDate(start)
        self.calendar.setMaximumDate(end)

    def sizeHint(self):
        return QtCore.QSize(self.maximumWidth(), 400)

    def refresh(self):
        '''
        called if the database changes
        '''
        LOGGER.warning("DiaryControl.refresh called - not yet implemented")

    def date_change(self):
        date = self.calendar.selectedDate()
        self.date_changed.emit(date)

    def view_change(self, i):
        self.view_changed.emit(i)

if __name__ == "__main__":
    from lib_openmolar.common.qt4.widgets import SignallingApplication
    app = SignallingApplication("test_application")

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    mw = QtGui.QMainWindow()

    obj = DiaryControl()

    mw.setCentralWidget(obj)
    mw.show()

    app.exec_()