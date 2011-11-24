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

import logging
import re

from PyQt4 import QtGui, QtCore

from lib_openmolar.client.classes import Tooth
from lib_openmolar.client.qt4gui.colours import colours


class ChartTooth(Tooth):
    '''
    custom class which acts as a view to the data stored in
    :doc:`ChartDataModel` for a tooth
    '''
    def __init__(self, tooth_id, model):
        '''
        :param: int (should conform to :doc:`../../misc/tooth_notation`)
        :param: :doc:`ChartDataModel`

        '''
        Tooth.__init__(self, tooth_id)
        self.data_model = model

        self.rect = QtCore.QRectF()
        self.under_mouse = False
        self.is_selected = False
        self.is_root = False
        self.is_present = True
        self.fill_shapes = []
        self.fill_shapes_current = True
        self.crowns = []
        self.ignore = False

        self.root = None

    def __repr__(self):
        return "tooth om_id=%d, shortname='%s' longname='%s' root='%s'"% (
            self.tooth_id, self.short_name, self.long_name, self.is_root)

    def __cmp__(self, other):
        try:
            return cmp( "%s%s"%(self.tooth_id, self.is_root),
                    "%s%s"%(other.tooth_id, other.is_root))
        except AttributeError:
            return -1

    @property
    def has_properties(self):
        return self.data_model.has_properties(self.tooth_id)

    @property
    def properties(self):
        return self.data_model.get_properties(self.tooth_id)

    @property
    def restorations(self):
        return self.data_model.get_restorations(self.tooth_id)

    def set_ignore(self, boolean):
        self.ignore = boolean

    def set_selected(self, boolean):
        self.is_selected = boolean

    def toggle_selection(self):
        self.set_selected(not self.is_selected)

    def set_is_present(self, boolean):
        self.is_present = boolean

    def toggle_is_present(self):
        self.set_is_present(not self.is_present)
        if self.root:
            self.root.toggle_is_present()

    def add_property(self, prop):
        '''
        convience method to add data to the underlying model
        '''
        self.data_model.add_property(prop)
        self.data_model.endResetModel()

    def set_rect(self, rect):
        '''
        update the rectangle of the tooth
        '''
        self.rect = rect
        if self.is_deciduous:
            h = rect.height()*.08
            w = rect.width()*.08
            self.rect = self.rect.adjusted(w,h,-w,-h)
        self.set_graphics_points()
        self.fill_shapes_current = False

    def select_rect(self, include_root = False):
        if not self.root or not include_root:
            rect = self.rect
        elif self.is_upper:
            rect = QtCore.QRectF(self.root.rect.topLeft(),
                self.rect.bottomRight())
        else:
            rect = QtCore.QRectF(self.rect.topLeft(),
                self.root.rect.bottomRight())

        return rect.adjusted(0 ,0, -1, -1)

    @property
    def properties_as_string(self):
        prop_str = u""
        for prop in self.properties:
            prop_str += prop.text
        return prop_str

    @property
    def ref_next(self):
        '''
        returns the next tooth in a forward direction
        (eg if return is pressed)
        '''
        if self.tooth_id == 32:
            return 1
        if self.tooth_id == 84:
            return 65
        return self.tooth_id + 1

    @property
    def ref_prev(self):
        '''
        returns the next tooth in a backward direction
        '''
        if self.tooth_id == 1:
            return 32
        if self.tooth_id == 65:
            return 84
        return self.tooth_id - 1

    @property
    def ref_left(self):
        '''
        returns the appropriate ref for the left arrow_key
        '''
        if self.is_upper:
            return self.ref_prev
        else:
            return self.ref_next

    @property
    def ref_right(self):
        '''
        returns the appropriate ref for the left arrow_key
        '''
        if self.is_upper:
            return self.ref_next
        else:
            return self.ref_prev

    @property
    def row_down(self):
        '''
        returns the appropriate tooth in a downwards direction
        '''
        found = False
        for row in SETTINGS.visible_chart_rows:
            if self.tooth_id in SETTINGS.TOOTH_GRID[row]:
                index = SETTINGS.TOOTH_GRID[row].index(self.tooth_id)
                found = True
                break

        if not found:
            print "not found!"
            return

        if row == SETTINGS.visible_chart_rows[-1]:
            return self.tooth_id

        i = SETTINGS.visible_chart_rows.index(row)
        row_down = SETTINGS.visible_chart_rows[i+1]

        new_val = SETTINGS.TOOTH_GRID[row_down][index]
        if new_val == 0:
            return self.tooth_id
        return new_val

    @property
    def row_up(self):
        '''
        returns the appropriate tooth in a downwards direction
        '''
        found = False
        for row in reversed(SETTINGS.visible_chart_rows):
            if self.tooth_id in SETTINGS.TOOTH_GRID[row]:
                index = SETTINGS.TOOTH_GRID[row].index(self.tooth_id)
                found = True
                break

        if not found:
            print "not found!"
            return

        if row == SETTINGS.visible_chart_rows[0]:
            return self.tooth_id

        i = SETTINGS.visible_chart_rows.index(row)
        row_up = SETTINGS.visible_chart_rows[i-1]

        new_val = SETTINGS.TOOTH_GRID[row_up][index]
        if new_val == 0:
            return self.tooth_id
        return new_val

    @property
    def line_edit_text(self):
        return self.properties_as_string

    def set_graphics_points(self):
        toothdimen = self.rect.width()
        x = self.rect.topLeft().x()
        y = self.rect.topLeft().y()
        if self.is_backtooth:
            self.ax = x + toothdimen * 0.05
            self.bx = x + toothdimen * 0.15
            self.cx = x + toothdimen * 0.2
            self.dx = x + toothdimen * 0.35
            self.ex = x + toothdimen * 0.5
            self.fx = x + toothdimen * 0.65
            self.gx = x + toothdimen * 0.8
            self.hx = x + toothdimen * 0.85
            self.ix = x + toothdimen * 0.95
            toothdimen = self.rect.height()
            self.ay = y + toothdimen * 0.05
            self.by = y + toothdimen * 0.15
            self.cy = y + toothdimen * 0.2
            self.dy = y + toothdimen * 0.35
            self.ey = y + toothdimen * 0.5
            self.fy = y + toothdimen * 0.65
            self.gy = y + toothdimen * 0.8
            self.hy = y + toothdimen * 0.85
            self.iy = y + toothdimen * 0.95
        else:
            #--front tooth - different patterns
            self.ax = x + toothdimen * 0.05
            self.bx = x + toothdimen * 0.15
            self.cx = x + toothdimen * 0.2
            self.dx = x + toothdimen * 0.3
            self.ex = x + toothdimen * 0.5
            self.fx = x + toothdimen * 0.7
            self.gx = x + toothdimen * 0.8
            self.hx = x + toothdimen * 0.85
            self.ix = x + toothdimen * 0.95
            toothdimen = self.rect.height()
            self.ay = y + toothdimen * 0.05
            self.by = y + toothdimen * 0.15
            self.cy = y + toothdimen * 0.2
            self.dy = y + toothdimen * 0.3
            self.ey = y + toothdimen * 0.5
            self.fy = y + toothdimen * 0.7
            self.gy = y + toothdimen * 0.8
            self.hy = y + toothdimen * 0.85
            self.iy = y + toothdimen * 0.95

        #--the occlusal surface (for backteeth)
        #--or incisal edge for front teeth..
        #-- is given a width here.
        #-- irw = inner rectangle width
        irw = self.rect.width() * 0.25

        if self.is_backtooth:
            irh = self.rect.height() * 0.25
        else:
            irh = self.rect.height() * 0.45
        self.innerRect = self.rect.adjusted(irw, irh, -irw, -irh)

    def init_restoration_shapes(self):
        # check to see whether this LONG procedure is necessary
        if self.fill_shapes_current:
            pass
        self.fill_shapes = []
        self.crowns = []
        for prop in self.restorations:
            if prop.type == prop.CROWN:
                self.crowns.append(prop)
                continue

            surfaces, material = prop.surfaces_to_draw, prop.material

            brush, shape = None, None

            #--set filling color
            if material in ("CO", "FS"):
                brush = colours.COMPOSITE
            elif material == "GL":
                brush = colours.GLASS
            elif material == "GO":
                brush = colours.GOLD
            elif material == "PO":
                brush = colours.PORCELAIN
            elif material == "AM":
                brush = colours.AMALGAM
            else:
                print "unhanded material colour", material

            if self.is_backtooth:
                if prop.is_fissure_sealant:
                    shape = QtGui.QPolygon([self.dx-2, self.ey-2, self.fx+2, self.ey-2, self.fx+2, self.ey+2, self.dx-2, self.ey+2])
                elif re.match("[MODBL]{5}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.by, self.cx, self.dy, self.dx, self.dy, self.dx, self.by,
                    self.fx, self.by, self.fx, self.dy, self.gx, self.dy, self.ix, self.by, self.ix, self.hy, self.gx, self.fy, self.fx,
                    self.fy, self.fx, self.hy, self.dx, self.hy, self.dx, self.fy, self.cx, self.fy, self.ax, self.hy])
                elif re.match("[MODB]{4}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.by, self.dx, self.dy, self.dx, self.by, self.fx, self.by,
                    self.fx, self.dy, self.ix, self.by, self.ix, self.hy, self.fx, self.fy, self.dx, self.fy, self.ax, self.hy])
                elif re.match("[MODL]{4}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.by, self.dx, self.dy, self.fx, self.dy, self.ix, self.by,
                    self.ix, self.hy, self.fx, self.fy, self.fx, self.hy, self.dx, self.hy, self.dx, self.fy, self.ax, self.hy])
                elif re.match("[MOD]{3}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.by, self.dx, self.dy, self.fx, self.dy, self.ix, self.by,
                    self.ix, self.hy, self.fx, self.fy, self.dx, self.fy, self.ax, self.hy])
                elif re.match("[MOB]{3}", surfaces):
                    shape = QtGui.QPolygon([self.dx, self.dy, self.ex, self.dy, self.ex, self.by, self.fx, self.by,
                    self.fx, self.dy, self.gx, self.dy, self.ix, self.cy, self.ix, self.gy, self.gx, self.fy, self.dx, self.fy])
                elif re.match("[MOL]{3}", surfaces):
                    shape = QtGui.QPolygon([self.dx, self.dy, self.gx, self.dy, self.ix, self.cy, self.ix, self.gy,
                    self.gx, self.fy, self.fx, self.fy, self.fx, self.hy, self.ex, self.hy, self.ex, self.fy, self.dx, self.fy])
                elif re.match("[DOB]{3}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.cy, self.cx, self.dy, self.dx, self.dy, self.dx, self.by,
                    self.ex, self.by, self.ex, self.dy, self.fx, self.dy, self.fx, self.fy, self.cx, self.fy, self.ax, self.gy])
                elif re.match("[DOL]{3}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.cy, self.cx, self.dy, self.fx, self.dy, self.fx, self.fy,
                    self.ex, self.fy, self.ex, self.hy, self.dx, self.hy, self.dx, self.fy, self.cx, self.fy, self.ax, self.gy])
                elif re.match("[MBD]{3}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.by, self.dx, self.ay, self.fx, self.ay, self.ix, self.by,
                    self.ix, self.ey, self.hx, self.ey, self.hx, self.cy, self.bx, self.cy, self.bx, self.ey, self.ax, self.ey])
                elif re.match("[MLD]{3}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.ey, self.bx, self.ey, self.bx, self.hy, self.hx, self.hy,
                    self.hx, self.ey, self.ix, self.ey, self.ix, self.gy, self.gx, self.iy, self.bx, self.iy, self.ax, self.gy])
                elif re.match("[OB]{2}", surfaces):
                    shape = QtGui.QPolygon([self.cx, self.ay, self.gx, self.ay, self.fx, self.cy, self.fx, self.fy,
                    self.dx, self.fy, self.dx, self.cy])
                elif re.match("[OL]{2}", surfaces):
                    shape = QtGui.QPolygon([self.dx, self.dy, self.fx, self.dy, self.fx, self.gy, self.gx, self.iy,
                    self.cx, self.iy, self.dx, self.gy])
                elif re.match("[MB]{2}", surfaces):
                    shape = QtGui.QPolygon([self.dx, self.ay, self.fx, self.ay, self.ix, self.by, self.ix, self.ey,
                    self.hx, self.ey, self.hx, self.dy, self.fx, self.cy, self.dx, self.cy, self.bx, self.by])
                elif re.match("[ML]{2}", surfaces):
                    shape = QtGui.QPolygon([self.dx, self.iy, self.fx, self.iy, self.ix, self.hy, self.ix, self.ey,
                    self.hx, self.ey, self.hx, self.fy, self.fx, self.gy, self.dx, self.gy, self.bx, self.hy])
                elif re.match("[DB]{2}", surfaces):
                    shape = QtGui.QPolygon([self.fx, self.ay, self.dx, self.ay, self.ax, self.by, self.ax, self.ey,
                    self.bx, self.ey, self.bx, self.dy, self.dx, self.cy, self.fx, self.cy, self.hx, self.by])
                elif re.match("[DL]{2}", surfaces):
                    shape = QtGui.QPolygon([self.fx, self.iy, self.dx, self.iy, self.ax, self.hy, self.ax, self.ey,
                    self.bx, self.ey, self.bx, self.fy, self.dx, self.gy, self.fx, self.gy, self.hx, self.hy])
                elif re.match("[MO]{2}", surfaces):
                    shape = QtGui.QPolygon([self.dx, self.dy, self.gx, self.dy, self.ix, self.cy, self.ix, self.gy,
                    self.gx, self.fy, self.dx, self.fy])
                elif re.match("[DO]{2}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.cy, self.cx, self.dy, self.fx, self.dy, self.fx, self.fy,
                    self.cx, self.fy, self.ax, self.gy])
                elif "O" in surfaces:
                    shape = QtGui.QPolygon([self.dx, self.dy, self.fx, self.dy, self.fx, self.fy, self.dx, self.fy])
                elif "M" in surfaces:
                    shape = QtGui.QPolygon([self.gx, self.dy, self.ix, self.by, self.ix, self.hy, self.gx, self.fy])
                elif "D" in surfaces:
                    shape = QtGui.QPolygon([self.ax, self.by, self.cx, self.dy, self.cx, self.fy, self.ax, self.hy])
                elif "L" in surfaces:
                    shape = QtGui.QPolygon([self.bx, self.iy, self.dx, self.gy, self.fx, self.gy, self.hx, self.iy])
                elif "B" in surfaces:
                    shape = QtGui.QPolygon([self.bx, self.ay, self.hx, self.ay, self.fx, self.cy, self.dx, self.cy])

            else: #front tooth
                if re.match("[MBD]{3}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.by, self.dx, self.ay, self.fx, self.ay, self.ix, self.by,
                    self.ix, self.ey, self.hx, self.ey, self.hx, self.cy, self.bx, self.cy, self.bx, self.ey, self.ax, self.ey])
                elif re.match("[MLD]{3}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.ey, self.bx, self.ey, self.bx, self.hy, self.hx, self.hy,
                    self.hx, self.ey, self.ix, self.ey, self.ix, self.gy, self.gx, self.iy, self.bx, self.iy, self.ax, self.gy])
                elif re.match("[OB]{2}", surfaces):
                    shape = QtGui.QPolygon([self.cx, self.ay, self.gx, self.ay, self.fx, self.cy, self.fx, self.fy,
                    self.dx, self.fy, self.dx, self.cy])
                elif re.match("[OL]{2}", surfaces):
                    shape = QtGui.QPolygon([self.dx, self.dy, self.fx, self.dy, self.fx, self.gy, self.gx, self.iy,
                    self.cx, self.iy, self.dx, self.gy])
                elif re.match("[MB]{2}", surfaces):
                    shape = QtGui.QPolygon([self.dx, self.ay, self.fx, self.ay, self.ix, self.by, self.ix, self.ey,
                    self.hx, self.ey, self.hx, self.dy, self.fx, self.cy, self.dx, self.cy, self.bx, self.by])
                elif re.match("[ML]{2}", surfaces):
                    shape = QtGui.QPolygon([self.dx, self.iy, self.fx, self.iy, self.ix, self.hy, self.ix, self.ey,
                    self.hx, self.ey, self.hx, self.fy, self.fx, self.gy, self.dx, self.gy, self.bx, self.hy])
                elif re.match("[DB]{2}", surfaces):
                    shape = QtGui.QPolygon([self.fx, self.ay, self.dx, self.ay, self.ax, self.by, self.ax, self.ey,
                    self.bx, self.ey, self.bx, self.dy, self.dx, self.cy, self.fx, self.cy, self.hx, self.by])
                elif re.match("[DL]{2}", surfaces):
                    shape = QtGui.QPolygon([self.fx, self.iy, self.dx, self.iy, self.ax, self.hy, self.ax, self.ey,
                    self.bx, self.ey, self.bx, self.fy, self.dx, self.gy, self.fx, self.gy, self.hx, self.hy])
                elif re.match("[MOD]{3}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.cy, self.cx, self.dy,
                    self.innerRect.topLeft().x(),self.innerRect.topLeft().y(),
                    self.innerRect.topRight().x(),self.innerRect.topRight().y(),
                    self.gx, self.dy, self.ix, self.cy, self.ix, self.gy, self.gx, self.fy,
                    self.innerRect.bottomRight().x(),
                    self.innerRect.bottomRight().y(),
                    self.innerRect.bottomLeft().x(),
                    self.innerRect.bottomLeft().y(),self.cx, self.fy, self.ax, self.gy])
                elif re.match("[MO]{2}", surfaces):
                    shape = QtGui.QPolygon([self.innerRect.topLeft().x(),
                    self.innerRect.topLeft().y(),
                    self.innerRect.topRight().x(),self.innerRect.topRight().y(),
                    self.gx, self.dy, self.ix, self.cy, self.ix, self.gy, self.gx, self.fy,
                    self.innerRect.bottomRight().x(),
                    self.innerRect.bottomRight().y(),
                    self.innerRect.bottomLeft().x(),
                    self.innerRect.bottomLeft().y(),
                    ])
                elif re.match("[DO]{2}", surfaces):
                    shape = QtGui.QPolygon([self.ax, self.cy, self.cx, self.dy,
                    self.innerRect.topLeft().x(),self.innerRect.topLeft().y(),
                    self.innerRect.topRight().x(),self.innerRect.topRight().y(),
                    self.innerRect.bottomRight().x(),
                    self.innerRect.bottomRight().y(),
                    self.innerRect.bottomLeft().x(),
                    self.innerRect.bottomLeft().y(),
                    self.cx, self.fy, self.ax, self.gy])
                elif "O" in surfaces:
                    shape = QtGui.QPolygon([self.innerRect.topLeft().x(),
                    self.innerRect.topLeft().y(),
                    self.innerRect.topRight().x(),
                    self.innerRect.topRight().y(),
                    self.innerRect.bottomRight().x(),
                    self.innerRect.bottomRight().y(),
                    self.innerRect.bottomLeft().x(),
                    self.innerRect.bottomLeft().y()])
                elif "M" in surfaces:
                    shape = QtGui.QPolygon(
                    [self.hx, self.dy, self.ix, self.dy, self.ix, self.fy, self.hx, self.fy, self.gx, self.ey])
                elif "D" in surfaces:
                    shape = QtGui.QPolygon(
                    [self.ax, self.dy, self.bx, self.dy, self.cx, self.ey, self.bx, self.fy, self.ax, self.fy])
                elif "L" in surfaces:
                    shape = QtGui.QPolygon([self.cx, self.hy, self.cx, self.gy, self.ex, self.fy,
                    self.gx, self.gy, self.gx, self.hy, self.fx, self.iy, self.dx, self.iy])
                elif "B" in surfaces:
                    shape = QtGui.QPolygon([self.cx, self.cy, self.cx, self.ay, self.ex, self.ay,
                    self.gx, self.ay, self.gx, self.cy, self.fx, self.dy, self.dx, self.dy])

            if shape:
                self.fill_shapes.append((shape, brush))
            else:
                logging.debug ("shape error! '%s'"% surfaces)

        self.fill_shapes_current = True

    def draw_structure(self, painter):
        if self.is_present:
            self.init_restoration_shapes()
            xpad, ypad = 6, 6

            painter.save()
            painter.setBrush(colours.IVORY)
            painter.drawRoundedRect(self.rect, xpad, ypad)
            painter.drawRect(self.innerRect)

            outer_rect = self.rect.adjusted(xpad/3,ypad/3, -xpad/3, -ypad/3)
            painter.drawLine(outer_rect.topLeft(), self.innerRect.topLeft())
            painter.drawLine(outer_rect.topRight(), self.innerRect.topRight())
            painter.drawLine(outer_rect.bottomLeft(), self.innerRect.bottomLeft())
            painter.drawLine(outer_rect.bottomRight(), self.innerRect.bottomRight())

            painter.restore()

        else:
            xpad, ypad = 6, 6
            painter.save()
            painter.setOpacity(0.6)
            painter.drawRoundedRect(self.rect, xpad, ypad)

            painter.restore()

    def draw_restorations(self, painter):
        if self.is_present:
            self.init_restoration_shapes()

            for crown in self.crowns:
                painter.save()
                option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
                painter.setPen(QtGui.QPen(QtCore.Qt.black))
                painter.drawEllipse(self.rect)
                painter.drawText(self.rect, crown.crown_type, option)
                painter.restore()

            for shape, brush in self.fill_shapes:
                painter.save()
                #--put an outline around the filling
                painter.setPen(QtGui.QPen(colours.FILL_OUTLINE, 1))
                if brush:
                    painter.setBrush(brush)
                painter.drawPolygon(shape)
                painter.restore()

    def _test_draw_graphics_points(self, painter):
        '''
        test code
        '''
        painter.save()
        painter.setPen(QtGui.QPen(QtGui.QColor('red')))

        for xpoint in ( self.ax,
                        self.bx,
                        self.cx,
                        self.dx,
                        self.ex,
                        self.fx,
                        self.gx,
                        self.hx,
                        self.ix):

            for ypoint in ( self.ay,
                            self.by,
                            self.cy,
                            self.dy,
                            self.ey,
                            self.fy,
                            self.gy,
                            self.hy,
                            self.iy):
                painter.drawPoint(QtCore.QPointF(xpoint, ypoint))
        painter.restore()

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)
    from lib_openmolar.client.qt4gui.client_widgets import chart_widgets

    def paintEvent(event):
        painter = QtGui.QPainter(widg)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        for tooth in teeth:
            tooth.draw_structure(painter)
            tooth.draw_restorations(painter)
            tooth._test_draw_graphics_points(painter)

    app = QtGui.QApplication([])
    widg = QtGui.QWidget()
    widg.setFixedSize(600,600)

    teeth = []

    model = chart_widgets.ChartDataModel()

    rects = [
        widg.rect().adjusted(0,0,-widg.width()/2, -widg.height()/2),
        widg.rect().adjusted(widg.width()/2, 0, 0, -widg.height()/2),
        widg.rect().adjusted(0,widg.height()/2, -widg.width()/2, 0),
        widg.rect().adjusted(widg.width()/2, widg.height()/2, 0, 0)
        ]

    ids = [1,16,17,32]
    for rect in rects:
        tooth = ChartTooth(ids[rects.index(rect)], model)
        tooth.set_rect(rect)
        tooth.set_graphics_points()
        teeth.append(tooth)

    for fill in ("O,CO", "FS,AM"): #("ODB,CO", "B,GL", "DL,AM", "OL,CO", "FS"):
        for tooth_id in ids:
            prop = chart_widgets.ToothData(tooth_id)
            prop.from_fill_string(fill)
            model.add_property(prop)

    #model.endResetModel()

    widg.paintEvent = paintEvent
    widg.show()
    app.exec_()