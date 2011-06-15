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


###############################################################################
##                                                                           ##
##  I have chosen to use the following numbering system a the core reference ##
##  to teeth.                                                                ##
##                                                                           ##
##    the notation is as follows.                                            ##
##                                                                           ##
##    ADULT (this is the same as the universal numering system               ##
##                                                                           ##
##    1  2  3  4  5  6  7  8  | 9  10 11 12 13 14 15 16                      ##
##    _________________________________________________________              ##
##    32 31 30 29 28 27 26 25 | 24 23 22 21 20 19 18 17                      ##
##                                                                           ##
##    DECIDUOUS (UNS)                    (OPENMOLAR)                         ##
##                                                                           ##
##    A B C D E | F G H I J              65 66 67 68 69 | 70 71 72 73 74     ##
##    _____________________              _______________________________     ##
##    T S R Q P | O N M L K              85 84 83 82 81 | 80 79 78 76 75     ##
##                                                                           ##
##    It holds the advantage of being only 1 byte per tooth (!)              ##
##    For presentation to the user,                                          ##
##    This is translated to various other formats via use of dictionary.     ##
##                                                                           ##
##                                                                           ##
###############################################################################

from __future__ import division

from PyQt4 import QtGui, QtCore
import chart_widget_base

class TreatmentChartWidget(chart_widget_base.ChartWidgetBase):
    '''
    ChartWidget as used on the summary page
    '''
    def __init__(self, model=None, parent=None):
        super(TreatmentChartWidget, self).__init__(model, parent)

        self.treatment_addition_cat = "Treatment"

        self.add_key_press_function(
            QtCore.Qt.Key_F5, self.complete_treatment)

    def add_data(self, tooth_data):
        '''
        add a tooth_data object to the chart
        '''
        self.tooth_data_model.add_property(tooth_data)

    def complete_treatment(self):
        tooth = self.current_tooth
        QtGui.QMessageBox.information(self, "info",
        "complete treatment on %s" %tooth.long_name)
        return tooth.ref

    def draw_tooth(self, tooth, painter):
        '''
        overwrite this function so that no teeth are drawn by default,
        only if they have some treatment....
        '''

        if tooth.has_properties:
            tooth.draw_structure(painter)


if __name__ == "__main__":
    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    object = TreatmentChartWidget(None, dl)

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(object)
    dl.exec_()
    app.closeAllWindows()
