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

class DiaryPeriodControl(QtGui.QWidget):
    '''
    '''
    index_changed = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        icon = QtGui.QIcon()
        day_button = QtGui.QPushButton(icon, "day")
        day_button.setFocusPolicy(QtCore.Qt.NoFocus)
        day_button.setToolTip(_( u"Day View (24 hours)"))

        work_day_button = QtGui.QPushButton(icon, "workday")
        work_day_button.setFocusPolicy(QtCore.Qt.NoFocus)
        work_day_button.setToolTip(
            _( u"Work Day View (determined by sessions)"))

        week_button = QtGui.QPushButton(icon, "week")
        week_button.setFocusPolicy(QtCore.Qt.NoFocus)
        week_button.setToolTip(_( u"week View (24 hours)"))

        work_week_button = QtGui.QPushButton(icon, "workweek")
        work_week_button.setFocusPolicy(QtCore.Qt.NoFocus)
        work_week_button.setToolTip(
            _( u"Work week View (determined by sessions)"))

        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(2)
        layout.addWidget(day_button)
        layout.addWidget(work_day_button)
        layout.addWidget(week_button)
        layout.addWidget(work_week_button)

    def sizeHint(self):
        return QtCore.QSize(200,60)

if __name__ == "__main__":

    def sig_catcher(*args):
        print args, cp.sender()

    from gettext import gettext as _

    app = QtGui.QApplication([])
    cp = DiaryPeriodControl()
    cp.show()
    app.exec_()
