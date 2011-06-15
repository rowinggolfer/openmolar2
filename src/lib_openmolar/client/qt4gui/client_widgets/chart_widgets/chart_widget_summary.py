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

from __future__ import division

from PyQt4 import QtGui, QtCore

import chart_widget_static

class SummaryChartWidget(chart_widget_static.StaticChartWidget):
    '''
    ChartWidget as used on the summary page
    '''
    def __init__(self, model, parent=None):
        chart_widget_static.StaticChartWidget.__init__(self, model, parent)
        self.focused = True

if __name__ == "__main__":

    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    object = SummaryChartWidget({1:[]}, dl)
    object.add_fill_from_string(1, "MOD,AM")

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(object)

    dl.exec_()
    app.closeAllWindows()
