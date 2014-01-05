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

from __future__ import division

from PyQt4 import QtGui, QtCore
import chart_widget_base

class ChartWidgetTreatment(chart_widget_base.ChartWidgetBase):
    '''
    ChartWidget as used on the summary page
    '''
    def __init__(self, model=None, parent=None):
        super(ChartWidgetTreatment, self).__init__(model, parent)

        self.treatment_addition_cat = "Treatment"

        self.add_key_press_function(
            QtCore.Qt.Key_F5, self.complete_treatment)

    def complete_treatment(self):

        print self.chart_data_model

        tooth = self.current_tooth
        QtGui.QMessageBox.information(self, "info",
            "complete treatment on %s" %tooth.long_name)
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

    model = SETTINGS.treatment_model.plan_tx_chartmodel
    model.load_test_data()

    object = ChartWidgetTreatment(model, dl)

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(object)
    dl.exec_()
    app.closeAllWindows()
