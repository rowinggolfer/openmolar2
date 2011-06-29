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
from lib_openmolar.client.qt4gui.client_widgets.chart_widgets import ChartWidgetBase

class ChartWidgetCompleted(ChartWidgetBase):
    '''
    ChartWidget as used on the summary page
    '''
    def __init__(self, model=None, parent=None):
        super(ChartWidgetCompleted, self).__init__(model, parent)

        self.add_key_press_function(
            QtCore.Qt.Key_F5, self.complete_treatment)

        self.treatment_addition_cat = "Completed"

    def complete_treatment(self):
        tooth = self.current_tooth
        QtGui.QMessageBox.information(self, "info",
        "edit completed treatment on %s?" %tooth.long_name)
        return tooth.tooth_id

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
    object = ChartWidgetCompleted(None, dl)

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(object)
    dl.exec_()
    app.closeAllWindows()
