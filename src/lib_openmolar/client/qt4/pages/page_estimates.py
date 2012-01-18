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


from PyQt4 import QtCore, QtGui, QtSql


class EstimatesPage(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.button = QtGui.QPushButton("Calculate Estimate")

        self.label = QtGui.QLabel("")

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        self.clear()
        self.connect_signals()

    def sizeHint(self):
        return QtCore.QSize(400,400)

    def minimumSizeHint(self):
        return QtCore.QSize(300,300)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def connect_signals(self, connect=True):
        self.button.clicked.connect(self.calculate_estimates)

    def clear(self):
        self.label.setText("no estimate loaded")

    def load_patient(self):
        pass

    def calculate_estimates(self):
        '''
        price the current treatment plan under all available feescales
        '''
        html = ""
        for fee_scale in SETTINGS.fee_scales:
            html += "<h4>%s</h4>"% fee_scale.name
            try:
                html += fee_scale.get_estimate(SETTINGS.current_patient)
            except Exception as e:
                self.Advise("FEE SCALE ERROR<hr /><pre>%s</pre>"%e)
                html+="Error - %s"% e
            html += "<hr />"

        if html == "":
            html = "No fee scales available. Have you installed any?"

        self.label.setText(html)

if __name__ == "__main__":
    
    

    app = QtGui.QApplication([])

    ep = EstimatesPage()

    dl = QtGui.QDialog()
    dl.setMinimumSize(400,200)
    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(ep)
    dl.exec_()
