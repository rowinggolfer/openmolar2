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

'''
this module provides the ChartWidgetBase class, which is inherited by all
other charts.
'''

from __future__ import division

import types

from PyQt4 import QtGui, QtCore

import teeth
import roots

import chart_data_model

from lib_openmolar.client.qt4gui.client_widgets.chart_widgets import tooth_data

from lib_openmolar.client.qt4gui.client_widgets.chart_widgets import perio_data

class ChartWidgetBase(QtGui.QWidget):
    '''
    a custom widget to show a standard UK dental chart
    allows for user navigation with mouse and/or keyboard
    '''
    #:
    CHART_STYLE_MIXED = 1
    #:
    CHART_STYLE_DECIDUOUS = 2
    #:
    CHART_STYLE_SIMPLE = 3
    #:
    CHART_STYLE_COMPLEX = 4
    #:
    CHART_STYLE_COMPLEX_PLUS = 4.5
    #:
    CHART_STYLE_ROOTS = 5
    #:
    CHART_STYLE_PERIO = 6

    def __init__(self, model=None, parent=None):
        super(ChartWidgetBase, self).__init__(parent)

        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
        QtGui.QSizePolicy.Expanding))
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.setMinimumSize(self.minimumSizeHint())
        #:
        self.show_LR = True
        #:
        self.show_selected = False
        #:
        self.setMouseTracking(True)
        #:
        self.draw_deciduous = True
        #:
        self.draw_permanent = True
        #:
        self.draw_roots = False
        #:
        self.draw_perio = False
        #:relative width of the inner rows
        self.inner_percentage = 0.6
        #: populated during resize event
        self.teeth = {}
        self._current_tooth = None
        #:
        self.focused = False
        #:
        self.borderX = 4    #shadow border width
        #:
        self.borderY = 4
        #:
        self.key_press_dict = {}

        if model is None:
            model = chart_data_model.ChartDataModel()
        #: the relevant :doc:`ChartDataModel`
        self.chart_data_model = model
        self.chart_data_model.register_view(self)

        self.init_teeth_and_roots()
        self.setStyle(SETTINGS.default_chart_style)

        #:
        self.allow_multi_select = True

    def minimumSizeHint(self):
        return QtCore.QSize(200,90)

    def sizeHint(self):
        return QtCore.QSize(500, 200)

    def model_changed(self):
        '''
        called when underlying model has altered
        '''
        self.resizeEvent() # <- faciliates the graphics loading of fillings.
        self.update()

    def setStyle(self, enum):
        if enum == self.CHART_STYLE_DECIDUOUS:
            self.deciduous_style()
        elif enum == self.CHART_STYLE_MIXED:
            self.mixed_style()
        elif enum == self.CHART_STYLE_SIMPLE:
            self.simple_style()
        elif enum == self.CHART_STYLE_COMPLEX:
            self.complex_style()
        elif enum == self.CHART_STYLE_COMPLEX_PLUS:
            self.complex_style()
            self.draw_perio = True
        elif enum == self.CHART_STYLE_ROOTS:
            self.roots_style()
        elif enum == self.CHART_STYLE_PERIO:
            self.perio_style()
        else:
            print "unknown chart style called!!"
        self.set_current_tooth(None)
        self.resizeEvent()
        self.update()

    def deciduous_style(self):
        self._style = self.CHART_STYLE_DECIDUOUS
        SETTINGS.visible_chart_rows = (0,3)
        self.draw_deciduous = True
        self.draw_permanent = False
        self.draw_roots = False
        self.draw_perio = False
        self.inner_percentage = 0.2 #relative width of the inner rows

    def mixed_style(self):
        self._style = self.CHART_STYLE_MIXED
        SETTINGS.visible_chart_rows = (0,1,2,3)
        self.draw_deciduous = True
        self.draw_permanent = True
        self.draw_roots = False
        self.draw_perio = False
        self.inner_percentage = 0.6 #relative width of the inner rows

    def simple_style(self):
        self._style = self.CHART_STYLE_MIXED
        SETTINGS.visible_chart_rows = (1,2)
        self.draw_deciduous = False
        self.draw_permanent = True
        self.draw_roots = False
        self.draw_perio = False
        self.inner_percentage = 0.8 #relative width of the inner rows

    def complex_style(self):
        self._style = self.CHART_STYLE_COMPLEX
        SETTINGS.visible_chart_rows = (1,2)
        self.draw_deciduous = False
        self.draw_permanent = True
        self.draw_roots = True
        self.draw_perio = False
        self.inner_percentage = 0.5 #relative width of the inner rows

    def roots_style(self):
        self._style = self.CHART_STYLE_ROOTS
        SETTINGS.visible_chart_rows = (1,2)
        self.draw_deciduous = False
        self.draw_permanent = False
        self.draw_roots = True
        self.draw_perio = False
        self.inner_percentage = 0.1 #relative width of the inner rows

    def perio_style(self):
        self._style = self.CHART_STYLE_PERIO
        SETTINGS.visible_chart_rows = (1,2)
        self.draw_deciduous = False
        self.draw_permanent = False
        self.draw_roots = True
        self.draw_perio = True
        self.inner_percentage = 0 #relative width of the inner rows

    def clear(self):
        '''
        refreshes the chart (and underlying data model)
        '''
        self.set_current_tooth(None)
        for tooth in self.iterate_teeth():
            tooth.set_is_present(True)
            tooth.is_selected = False
            if tooth.root:
                tooth.root.set_is_present(True)
        self.chart_data_model.clear()
        self.update()

    def add_key_press_function(self, key, function):
        '''
        used by widgets which inherit from this class  eg.
        widg.add_key_press_function(QtCore.Qt.Key_ControlA, widg.do_something)
        '''
        self.key_press_dict[key] = function

    def init_teeth_and_roots(self):
        for row in (1,2,0,3) : #  upper, lower, upper dec, lower dec
            for col in range(len(SETTINGS.TOOTH_GRID[row])): # number of teeth!
                tooth_id = SETTINGS.TOOTH_GRID[row][col]
                if tooth_id != 0:
                    tooth = teeth.ChartTooth(tooth_id, self.chart_data_model)
                    if row in (1,2):  #adult teeth have roots
                        root = roots.ChartRoot(tooth_id, self.chart_data_model)
                        tooth.root = root
                    self.teeth[tooth_id] = tooth

    def set_known_teeth(self, key):
        '''
        sets which teeth are present from a 64bit integer key
        opposite function is found in the static chart subclass
        '''
        dent_key = SETTINGS.tooth_decoder.decode(key)
        i = 0
        for row in SETTINGS.TOOTH_GRID:
            for tooth_id in row:
                tooth = self.teeth.get(tooth_id)
                if tooth:
                    tooth.set_is_present(dent_key.at(i))
                    if tooth.root:
                        tooth.root.set_is_present(dent_key.at(i))

                i += 1
        self.update()

    def tooth_from_ref(self, ref):
        for tooth in self.iterate_teeth():
            if tooth.tooth_id == ref:
                return tooth

    def choose_teeth(self):
        for tooth in self.iterate_teeth():
            if tooth.is_deciduous:
                tooth.set_ignore(not self.draw_deciduous)
            else:
                tooth.set_ignore(not self.draw_permanent)
            if tooth.root:
                tooth.root.set_ignore(not self.draw_roots)

    def iterate_teeth(self, visible_only=False):
        for row in SETTINGS.TOOTH_GRID:
            for tooth_id in row:
                tooth = self.teeth.get(tooth_id)
                if tooth:
                    if visible_only:
                        if not tooth.ignore:
                            yield tooth
                        elif tooth.root and not tooth.root.ignore:
                            yield tooth
                    else:
                        yield tooth

    def clear_selection(self):
        '''
        set every tooth to is_selected =False
        '''
        for tooth in self.iterate_teeth():
            tooth.is_selected = False
            if tooth.root:
                tooth.root.is_selected = False


    @property
    def current_tooth(self):
        return self._current_tooth

    def set_current_tooth(self, new_tooth=None, set_as_selected=True):
        '''
        overloaded function,
        tooth can be either a reference, or a tooth object,
        or NoneType to deselect all
        NOTE - if a reference is sent, all other selections will be cleared!
        '''
        ## case where new_tooth is an integer
        if type(new_tooth) == types.IntType:
            ref = new_tooth
            self.clear_selection()
            return self.set_current_tooth(self.tooth_from_ref(new_tooth))

        ## case where new_tooth is of type "Tooth"
        if self._current_tooth != new_tooth:
            self._current_tooth = new_tooth
            if new_tooth and set_as_selected:
                new_tooth.is_selected = True
                if new_tooth.root:
                    new_tooth.root.is_selected = True

            return True

    @property
    def selected_teeth(self):
        selected = []
        for tooth in self.iterate_teeth():
            if tooth.is_selected:
                selected.append(tooth.tooth_id)
        if not selected:
            self.set_current_tooth(None)
        return selected

    def resizeEvent(self, event=None):
        '''
        initiate/update allsizes
        '''
        ho_padding = 6 #horizontal padding (around the midline)
        ve_padding = 15 #vertical padding (around the midline)
        ve_half_pad = ve_padding/2

        row_padding = 2 #between the deciduous and perm row

        ## allow for a border
        self.contents_rect = self.rect().adjusted(
            self.borderX, self.borderY, -self.borderX, -self.borderY)

        cell_width = (self.contents_rect.width()- ho_padding) / 16
        cell_height = (self.contents_rect.height()- ve_padding -
                        (2*row_padding)) / 2

        outer_height = cell_height * self.inner_percentage
        perm_height = cell_height - outer_height
        row_heights = (outer_height, perm_height, perm_height, outer_height)

        for row in range(len(SETTINGS.TOOTH_GRID)): # upper dec, upper, lower, lower dec
            for col in range(len(SETTINGS.TOOTH_GRID[row])): # number of teeth!

                top_y =  0 if row < 2 else cell_height + ve_padding

                row_height = row_heights[row]

                # QRectF.__init__(topLeft, topright, width, height)
                full_cell = QtCore.QRectF(self.borderX + col * cell_width,
                                    self.borderY + top_y,
                                    cell_width,
                                    cell_height)

                if row == 0 and col < 8:    # upper right deciduous
                    cell =  full_cell.adjusted(  0,
                                            0,
                                            0,
                                            -row_height)

                elif row == 0 and col > 7:  # upper left deciduous
                    cell =  full_cell.adjusted(  ho_padding,
                                            0,
                                            ho_padding,
                                            -row_height)


                elif row == 1 and col < 8:  # upper right permanent
                    cell =  full_cell.adjusted(  0,
                                            row_height + row_padding,
                                            0,
                                            0)

                elif row == 1 and col > 7:  # upper left permanent
                    cell =  full_cell.adjusted(  ho_padding,
                                            row_height + row_padding,
                                            ho_padding,
                                            0)

                elif row == 2 and col > 7:  # lower left permanent
                    cell =  full_cell.adjusted( ho_padding,
                                            0,
                                            ho_padding,
                                            -row_height)

                elif row == 2 and col < 8:  # lower right permanent
                    cell =  full_cell.adjusted(  0,
                                            0,
                                            0,
                                            -row_height)

                elif row == 3 and col > 7:  # lower left deciduous
                    cell =  full_cell.adjusted( ho_padding,
                                            row_height + row_padding,
                                            ho_padding,
                                            0)

                elif row == 3 and col < 8:  # lower right deciduous
                    cell =  full_cell.adjusted(  0,
                                            row_height + row_padding,
                                            0,
                                            0)

                else:
                    continue

                tooth_id = SETTINGS.TOOTH_GRID[row][col]
                if tooth_id != 0:
                    self.teeth[tooth_id].set_rect(cell)

                if row in (0,3):
                    root_row = 1 if row == 0 else 2
                    tooth_id = SETTINGS.TOOTH_GRID[root_row][col]
                    self.teeth[tooth_id].root.set_rect(cell)

        self.choose_teeth()


    def focusInEvent(self, event):
        self.focused = True
        self.update()

    def focusOutEvent(self, event):
        self.focused = False
        self.update()

    def mouseMoveEvent(self, event):
        redraw_needed = False
        point = QtCore.QPointF(event.pos())
        for tooth in self.iterate_teeth():
            if tooth.root and not tooth.root.ignore:
                under_mouse = tooth.root.rect.contains(point)
                if tooth.root.under_mouse != under_mouse:
                    tooth.root.under_mouse = under_mouse
                    redraw_needed = True

            if not tooth.ignore:
                under_mouse = tooth.rect.contains(point)
                if under_mouse != tooth.under_mouse:
                    tooth.under_mouse = under_mouse
                    redraw_needed = True

        if redraw_needed:
            self.update()

    def leaveEvent(self, event):
        redraw_needed = False
        for tooth in self.iterate_teeth():
            if tooth.root and tooth.root.under_mouse:
                tooth.root.under_mouse = False
                redraw_needed = True
            if tooth.under_mouse:
                tooth.under_mouse = False
                redraw_needed = True

        if redraw_needed:
            self.update()

    def _shift_select(self, next_tooth):
        current_selection = self.selected_teeth
        if current_selection == []:
            next_tooth.set_selected(True)
            return

        newly_selected = []

        min_selected = min(current_selection)
        max_selected = max(current_selection)
        if next_tooth.tooth_id < min_selected:
            newly_selected += range(min_selected, next_tooth.tooth_id, -1)
        if next_tooth.tooth_id > max_selected:
            newly_selected += range(next_tooth.tooth_id, max_selected, -1)

        for ref in newly_selected:
            tooth = self.tooth_from_ref(ref)
            if tooth:
                tooth.set_selected(True)

    def mouseDoubleClickEvent(self, event):
        if not self.current_tooth:
            self.mousePressEvent(event)
        self.emit(QtCore.SIGNAL("DoubleClicked"), self._current_tooth)

    def mousePressEvent(self, event):
        current_tooth = self.current_tooth
        current_selection = self.selected_teeth

        ctrl_mod = (self.allow_multi_select and
            event.modifiers() == QtCore.Qt.ControlModifier)

        shift_mod = (self.allow_multi_select and
            event.modifiers() == QtCore.Qt.ShiftModifier)

        point = QtCore.QPointF(event.pos())
        next_tooth = None
        for tooth in self.iterate_teeth():
            if tooth.under_mouse or (
            tooth.root and tooth.root.under_mouse):
                next_tooth = tooth
                break

        if not (ctrl_mod or shift_mod):
            self.clear_selection()
            self.set_current_tooth(next_tooth)
        else:
            if next_tooth:
                if shift_mod:
                    self._shift_select(next_tooth)
                    self.set_current_tooth(next_tooth)
                else: #(ctrl_mod)
                    self.set_current_tooth(next_tooth, False)
                    next_tooth.toggle_selection()

        self.redraw_check(current_selection, current_tooth)

    def keyPressEvent(self, event):
        key = event.key()

        current_tooth = self.current_tooth

        ctrl_mod = (self.allow_multi_select and
            event.modifiers() == QtCore.Qt.ControlModifier)

        shift_mod = (self.allow_multi_select and
            event.modifiers() == QtCore.Qt.ShiftModifier)

        # check to see if 1st key pressed .. no tooth selected
        if not current_tooth:
            if not event.key() in (QtCore.Qt.Key_Control, QtCore.Qt.Key_Shift):
                new_ref = 1 if self.draw_permanent else 65
            else:
                QtGui.QWidget.keyPressEvent(self, event)
                return
        elif event.key() in self.key_press_dict.keys():
            new_ref = self.key_press_dict[key]()  ## call inherited functions.
        elif event.key() == QtCore.Qt.Key_Return:
            new_ref = current_tooth.ref_next
        elif event.key() == QtCore.Qt.Key_Right:
            new_ref = current_tooth.ref_right
        elif event.key() == QtCore.Qt.Key_Left:
            new_ref = current_tooth.ref_left
        elif event.key() == QtCore.Qt.Key_Up:
            new_ref = current_tooth.row_up
        elif event.key() == QtCore.Qt.Key_Down:
            new_ref = current_tooth.row_down
        else:
            self.emit(QtCore.SIGNAL("key_press"), event)
            QtGui.QWidget.keyPressEvent(self, event)
            return

        next_tooth = self.tooth_from_ref(new_ref)
        if next_tooth == current_tooth:
            return
        current_selection = self.selected_teeth

        if not (ctrl_mod or shift_mod):
            self.clear_selection()
            self.set_current_tooth(next_tooth)
        else:
            if next_tooth:
                if shift_mod:
                    self._shift_select(next_tooth)
                    self.set_current_tooth(next_tooth)
                else: #(ctrl_mod)
                    self.set_current_tooth(next_tooth, False)
                    next_tooth.toggle_selection()

        self.redraw_check(current_selection, current_tooth)

    def redraw_check(self, previous_selection, previous_current_tooth):
        redraw_needed = False

        if self.current_tooth != previous_current_tooth:
            self.emit(QtCore.SIGNAL("current tooth changed"))
            redraw_needed = True

        new_selection = self.selected_teeth
        if new_selection != previous_selection:
            self.emit(QtCore.SIGNAL("selection changed"), new_selection)
            redraw_needed = True

        if redraw_needed:
            self.update()

    def paintEvent(self, event=None):
        '''
        overrides the paint event so that we can draw our grid
        note - other charts will re-implement this!
        '''
        self.draw_background()
        self.draw_mid_lines()
        self.draw_grid()

    def draw_background(self):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        if self.focused:
            painter.setBrush(self.palette().light())
        else:
            painter.setBrush(self.palette().mid())

        painter.setPen(painter.brush().color())
        painter.drawRoundedRect(self.rect(), 6,6)

        painter.setBrush(self.palette().window())
        painter.setPen(painter.brush().color())
        painter.drawRoundedRect(self.rect().adjusted(
                    self.borderX/2,
                    self.borderY/2,
                    -self.borderX/2,
                    -self.borderY/2), 6,6)

    def draw_mid_lines(self):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        #-- enable/disable differences
        if self.isEnabled():
            c = QtGui.QColor(QtCore.Qt.red)
            if not self.focused:
                c.setAlpha(100)
            pen = QtGui.QPen(c, 2)
            painter.setPen(pen)
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.gray, 2))

        if self.show_LR:
            fm = QtGui.QFontMetrics(self.font())
            right_pad = self.borderX + fm.width("Right ")
            left_pad = self.borderX + fm.width(" Left")
        else:
            right_pad, left_pad = 0, 0

        #--big horizontal dissection of entire widget
        painter.drawLine(right_pad,
                        self.height() / 2,
                        self.width() - left_pad,
                        self.height() / 2)

        #--vertical dissection of entire widget
        painter.drawLine(self.width() / 2,
                        self.borderY,
                        self.width() / 2,
                        self.contents_rect.height())

        if self.show_LR:
            if self.isEnabled():
                c = QtGui.QColor(QtCore.Qt.black)
                if not self.focused:
                    c.setAlpha(100)
                pen = QtGui.QPen(c, 2)
                painter.setPen(pen)
            else:
                painter.setPen(QtGui.QPen(QtCore.Qt.gray, 1))

            align = QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter
            painter.drawText(self.contents_rect, align, _("Left"))

            align = QtCore.Qt.AlignLeft| QtCore.Qt.AlignVCenter
            painter.drawText(self.contents_rect, align, _("Right"))

    def draw_tooth(self, tooth, painter):
        '''
        often overwritten by charts which inherits from this one
        '''
        if not tooth.ignore:
            tooth.draw_structure(painter)

    def draw_selections(self, tooth, painter):
        if (not self.isEnabled() or tooth.ignore or
        tooth.is_root and self._style != self.CHART_STYLE_ROOTS):
            return

        if tooth == self._current_tooth:
            colour, pen_width = QtCore.Qt.darkBlue , 2
        elif tooth.is_selected:
            colour, pen_width = QtCore.Qt.blue, 2
        elif tooth.under_mouse:
            colour, pen_width = QtCore.Qt.cyan, 1
        else:
            return

        c = QtGui.QColor(colour)
        if not self.focused:
            c.setAlpha(100)

        include_root = not self._style == self.CHART_STYLE_MIXED

        pen = QtGui.QPen(c, pen_width)
        painter.setPen(pen)
        painter.drawRoundedRect(tooth.select_rect(include_root), 6 ,6)

    def draw_grid(self):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        for tooth in self.iterate_teeth(visible_only=True):
            pen = QtGui.QPen(QtCore.Qt.gray, 1)
            painter.setPen(pen)
            self.draw_tooth(tooth, painter)
            tooth.draw_restorations(painter)
            self.draw_selections(tooth, painter)

            if self.draw_roots and tooth.root:
                self.draw_tooth(tooth.root, painter)
                self.draw_selections(tooth.root, painter)

class __TestDialog(QtGui.QDialog):
    '''
    this class is for testing purposes only
    '''
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("ChartWidgetBase Tester")
        self.label = QtGui.QLabel()

        self.chart = ChartWidgetBase()
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


    def but_clicked(self):
        self.chart.setStyle(self.sender().enum)

    def sig_catcher(self, arg):
        try:
            tooth_name = self.chart.current_tooth.long_name
        except AttributeError: #current_tooth can be None
            tooth_name = ""
        self.label.setText(tooth_name)


if __name__ == "__main__":

    app = QtGui.QApplication([])
    dl = __TestDialog()
    dl.exec_()
