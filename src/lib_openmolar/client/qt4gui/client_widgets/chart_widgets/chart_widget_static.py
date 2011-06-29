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

import chart_widget_base
import perio_data

class ChartWidgetStatic(chart_widget_base.ChartWidgetBase):
    '''
    ChartWidget as used on the summary page
    '''
    def __init__(self, model=None, parent=None):
        chart_widget_base.ChartWidgetBase.__init__(self, model, parent)

        self.add_key_press_function(
            QtCore.Qt.Key_Minus, self.toggle_tooth_present)

    def toggle_tooth_present(self):
        self.current_tooth.toggle_is_present()
        self.emit(QtCore.SIGNAL("teeth present changed"), self.known_teeth_key)
        return self.current_tooth.ref_next

    @property
    def known_teeth_key(self):
        '''
        returns a 64bit integer key of which teeth are present
        '''
        bit_array = QtCore.QBitArray(64)
        i = 0
        for row in SETTINGS.TOOTH_GRID:
            for tooth_id in row:
                tooth = self.teeth.get(tooth_id)
                if tooth and tooth.is_present:
                    bit_array.setBit(i)
                i += 1
        return SETTINGS.tooth_decoder.encode(bit_array)


    def resizeEvent(self, event=None):
        chart_widget_base.ChartWidgetBase.resizeEvent(self, event)

        ur8root = self.teeth[1].root
        ul8root = self.teeth[16].root
        lr8root = self.teeth[17].root
        ll8root = self.teeth[32].root

        #this next calulation gives a value for a 1mm depth
        self.perio_mm = ur8root.rect.height() * 0.035

        self.upper_perio_lines, self.lower_perio_lines = [], []

        for row_no in range(1,9):

            offset = row_no * self.perio_mm * 2
            line = QtCore.QLine(    ur8root.rect.x(),
                                    ur8root.rect.y() + offset,
                                    ul8root.rect.topRight().x(),
                                    ul8root.rect.topRight().y() + offset)
            self.upper_perio_lines.append(line)

            line = QtCore.QLine(    ll8root.rect.x(),
                                    ll8root.rect.bottomLeft().y() - offset,
                                    lr8root.rect.topRight().x(),
                                    lr8root.rect.bottomRight().y() - offset)
            self.lower_perio_lines.append(line)

    @property
    def perio_lines(self):
        for line in self.upper_perio_lines:
            yield line
        for line in self.lower_perio_lines:
            yield line

    def draw_perio_lines(self):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))

        for line in self.perio_lines:
            painter.drawLine(line)

    def paintEvent(self, event=None):
        '''
        overrides the paint event so that we can draw our grid
        note - other charts will re-implement this!
        '''
        chart_widget_base.ChartWidgetBase.paintEvent(self, event)
        if self.draw_perio:
            self.draw_perio_lines()
            self.draw_perio_data()

    def draw_perio_data(self):
        if not self.draw_roots:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        perio_upper_polygon = QtGui.QPolygon()
        perio_lower_polygon = QtGui.QPolygon()

        for tooth in self.iterate_teeth(visible_only=True):
            if tooth.root:
                for perio_datas in tooth.root.perio_properties:
                    off_x = tooth.root.rect.bottomLeft().x()
                    if tooth.is_upper:
                        off_y = self.upper_perio_lines[7].y1()
                        direction = -1
                        perio_polygon = perio_upper_polygon
                    else:
                        off_y = self.lower_perio_lines[7].y1()
                        direction = 1
                        perio_polygon = perio_lower_polygon
                    width = tooth.root.rect.width()

                    #print perio_datas
                    if perio_datas.type == perio_data.PerioData.POCKETING:
                        db, b, mb, mp, p, dp = perio_datas.data
                        db = db *self.perio_mm * direction
                        b = b *self.perio_mm * direction
                        mb = mb *self.perio_mm * direction
                        mp = mp *self.perio_mm * direction
                        p = p *self.perio_mm * direction
                        dp = dp *self.perio_mm * direction

                        #verticaldepths (buccal)
                        pen = QtGui.QPen(QtCore.Qt.blue, 2)
                        painter.setPen(pen)
                        x1 = off_x + width*.2
                        painter.drawLine(x1, off_y, x1, off_y+db)
                        x2 = off_x + width/2
                        painter.drawLine(x2, off_y, x2, off_y+b)
                        x3 = off_x + width*.8
                        painter.drawLine(x3, off_y, x3, off_y+mb)

                        #verticaldepths (palatal)
                        pen = QtGui.QPen(QtCore.Qt.darkBlue, 2)
                        painter.setPen(pen)
                        painter.drawLine(x1+2, off_y, x1+2, off_y+dp)
                        painter.drawLine(x2+2, off_y, x2+2, off_y+p)
                        painter.drawLine(x3+2, off_y, x3+2, off_y+mp)

                        for point in (
                            QtCore.QPoint(x1, off_y+(db+dp)/2),
                            QtCore.QPoint(x2, off_y+(b+p)/2),
                            QtCore.QPoint(x3, off_y+(mb+mp)/2)):

                            perio_polygon.append(point)



            #thin wiggly horizontal line
            pen = QtGui.QPen(QtCore.Qt.darkCyan, 1)
            painter.setPen(pen)
            painter.drawPolyline(perio_upper_polygon)
            painter.drawPolyline(perio_lower_polygon)


class _TestDialog(QtGui.QDialog):
    '''
    this class is for testing purposes only
    '''
    from random import randint

    def __init__(self, model, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("ChartWidgetStatic Tester")
        self.label = QtGui.QLabel()

        self.model = model
        self.chart = ChartWidgetStatic(self.model)

        self.connect(self.chart, QtCore.SIGNAL("selection changed"),
            self.sig_catcher)
        self.connect(self.chart, QtCore.SIGNAL("DoubleClicked"),
            self.sig_catcher)

        but_frame = QtGui.QFrame()
        layout = QtGui.QHBoxLayout(but_frame)

        for chart_style_name, chart_style_type in SETTINGS.chart_styles:
            but = QtGui.QPushButton(chart_style_name)
            but.enum = chart_style_type
            but.clicked.connect(self.but_clicked)
            layout.addWidget(but)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.chart)
        layout.addWidget(but_frame)

        self.model.load_test_data()

    def but_clicked(self):
        self.chart.setStyle(self.sender().enum)

    def sig_catcher(self, arg):
        try:
            tooth_name = self.chart.current_tooth.long_name
        except AttributeError: #current_tooth can be None
            tooth_name = ""
        self.label.setText(tooth_name)

    def populate_fills(self):

        self.tp_line_edit = QtGui.QLineEdit()
        self.tp_line_edit.setReadOnly(True)
        tp_button = QtGui.QPushButton("teeth present key")
        tp_button.clicked.connect(self.show_teeth_key)
        self.connect(self.chart, QtCore.SIGNAL("teeth present changed"),
            self.show_teeth_key)

        teeth_present_frame = QtGui.QFrame()
        layout = QtGui.QHBoxLayout(teeth_present_frame)
        layout.addWidget(self.tp_line_edit)
        layout.addWidget(tp_button)

        self.layout().addWidget(teeth_present_frame)

    def show_teeth_key(self, key):
        if key == False: #function has been called by button click
            key = self.chart.known_teeth_key
        self.tp_line_edit.setText(str(key))


if __name__ == "__main__":
    from lib_openmolar.client.qt4gui import client_widgets

    model = client_widgets.ChartDataModel()
    app = QtGui.QApplication([])
    dl = _TestDialog(model)
    dl.exec_()
    app.closeAllWindows()
