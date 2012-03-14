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

from PyQt4 import QtGui, QtCore


class ChartOptionsWidget(QtGui.QWidget):
    '''
    options when charts are visible.
    Used on summary page and charts page
    '''
    def __init__(self, parent): #note - MUST be parented for signal sending
        super(ChartOptionsWidget, self).__init__(parent)

        label = QtGui.QLabel(_("Chart Style"))
        label.setAlignment(QtCore.Qt.Alignment(
            QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter))

        self.combo_box = QtGui.QComboBox(self)
        for chart_style_name, chart_style_type in SETTINGS.chart_styles:
            self.combo_box.addItem(chart_style_name)

        self.combo_box.currentIndexChanged.connect(self.input)

        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(label)
        layout.addWidget(self.combo_box)

    def input(self, i):
        self.parent().emit(QtCore.SIGNAL("chart style"),
            SETTINGS.chart_styles[i][1])

    def clear(self):
        self.combo_box.setCurrentIndex(SETTINGS.default_chart_style-1)

class PatientInterfaceOptionsWidget(QtGui.QStackedWidget):
    '''
    a widget designed to be a corner widget for the patient interface
    tab widget. Offers options for the currently displayed tab.
    '''
    def __init__(self, parent=None):
        super(PatientInterfaceOptionsWidget, self).__init__(parent)

        self.chart_options = ChartOptionsWidget(self)
        self.addWidget(self.chart_options)

    def minimumSizeHint(self):
        return QtCore.QSize(200,20)

    def sizeHint(self):
        return QtCore.QSize(200, 30)

    def pt_loaded(self, options):
        self.chart_options.set_option(options.chart)

    def clear(self):
        for i in range(self.count()):
            widg = self.widget(i)
            try:
                widg.clear()
            except AttributeError:
                pass

    def tab_index_changed(self, i):
        '''
        this is connected to the patient interface tab widget's index changed
        signal.
        show the currect widget for the current tab
        '''
        # at current point this is as simple as showing the widget if
        # chart or clincal aummary page is chosen
        if i in (1,2):
            self.show()
        else:
            self.hide()

if __name__ == "__main__":
    
    

    def sig_catcher(*args):
        print args

    app = QtGui.QApplication([])
    object = PatientInterfaceOptionsWidget()
    object.clear()
    object.connect(object, QtCore.SIGNAL("chart style"), sig_catcher)
    object.show()
    app.exec_()