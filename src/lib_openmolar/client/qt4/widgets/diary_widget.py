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
from PyQt4 import QtCore, QtGui
from random import randint

from lib_openmolar.client.db_orm.diary import _DiarySettings, DiaryDataModel

###############################################################################
#            temporary globals                                                #
###############################################################################

SESSION_COLOUR = QtGui.QColor("yellow")
SESSION_COLOUR.setAlpha(100)
APPOINTMENT_COLOUR = QtGui.QColor("blue")


class DiaryWidget(QtGui.QWidget, _DiarySettings):
    '''
    A widget comprising a header and a canvas
    '''
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        _DiarySettings.__init__(self)

        self.date = QtCore.QDate.currentDate()
        self._style = self.DAY

        self.canvas = DiaryCanvas(self.date, self)
        self.vscroll_bar = QtGui.QScrollBar()
        self.connect_scrollbars()

        layout = QtGui.QHBoxLayout(self)
        layout.setSpacing(2)
        layout.addWidget(self.canvas)
        layout.addWidget(self.vscroll_bar)

        self.connect(self.canvas, QtCore.SIGNAL("resized"),
            self.set_scroll_values)

    def setModel(self, model):
        self.model =  model
        self.canvas.setModel(model)

    def connect_scrollbars(self, connect=True):
        if connect:
            self.vscroll_bar.valueChanged.connect(self.vscroll)
        else:
            self.vscroll_bar.valueChanged.disconnect(self.vscroll)

    def set_date(self, date):
        self.date = date
        self.canvas.set_date(date)
        self.set_scroll_values()

    def set_scroll_values(self):
        #self.connect_scrollbars(False)

        if self._style in (self.DAY, self.FOUR_DAY, self.WEEK):
            height = (self.canvas.left_margin.total_height
                        - self.canvas.canvas_rect.height())
            self.vscroll_bar.setRange(0, height)
            self.vscroll_bar.setValue(height/3)  #ie. 8pm 1/3 = 8/24
            return
        max = self.model.rowCount(self._style) - self.canvas.row_count + 1
        self.vscroll_bar.setRange(0, max)

        if self._style in (self.AGENDA, self.TASKS):
            self.vscroll_bar.setValue(1)
        else:
            row_id = self.model.row_from_date(self.date, self._style)
            self.vscroll_bar.setValue(row_id)

        #self.connect_scrollbars()

    def vscroll(self, int):
        self.canvas.vscroll(int)

    def setViewStyle(self, style):
        '''
        set the style as day, fourday, week, fortnight, month or year
        '''
        _DiarySettings.set_style(self, style)
        self.set_scroll_values()
        self.canvas.set_style(style)

class DiaryCanvasTopMargin(_DiarySettings):
    '''
    the left hand column of the canvas(if required)
    '''
    def __init__(self, date):
        _DiarySettings.__init__(self)
        self.date = date
        self.width = 0
        self.calc_height()
        self._rect = None
        self._headers = None

    def set_date(self, date):
        self.date = date
        self._headers = None

    def calc_height(self):
        self.fm = QtGui.QFontMetrics(QtGui.QApplication.instance().font())
        self.height = self.fm.height()

    def reset_width(self, width):
        self.width = width
        self._rect = None

    @property
    def rect(self):
        if self._rect == None:
            self._rect = QtCore.QRectF(0, 0, self.width, self.height)
        return self._rect

    @property
    def headers(self):
        if self._headers == None:
            if self._style == self.DAY:
                self._headers = [self.date.toString()]
            elif self._style == self.FOUR_DAY:
                self._headers = []
                for i in range(4):
                    self._headers.append(self.date.addDays(i).toString())
            elif self._style == self.WEEK:
                self._headers = []
                dayno = self.date.dayOfWeek()
                for i in range(1,8):
                    d = self.date.addDays(i-dayno)
                    self._headers.append(u"%s %s"% (d.shortDayName(i), d.toString("d/MM")))
            elif self._style in (self.FORTNIGHT, self.MONTH):
                self._headers = []
                for i in range(1,8):
                    self._headers.append(self.date.shortDayName(i))
            elif self._style == self.YEAR:
                labels = []
                for i in range(1,8):
                    labels.append(self.date.shortDayName(i)[0])
                self._headers = (labels * 6)[:37]
            elif self._style == self.AGENDA:
                self._headers = [_("Agenda")]
            elif self._style == self.TASKS:
                self._headers = [_("Tasks")]
            else:
                self._headers = ["whoops!"]

        return self._headers

    def draw_headers(self, painter):
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        cell_width = self.width / len(self.headers)
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        x = 0
        for label in self.headers:
            rect = QtCore.QRectF(x, 0, cell_width, self.height)
            painter.drawText(rect, label, option)
            x += cell_width

    def set_style(self, style):
        '''
        overwrite the base class
        '''
        _DiarySettings.set_style(self, style)
        self.calc_height()
        self._headers = None

class DiaryCanvasLeftMargin(_DiarySettings):
    '''
    the left hand column of the canvas(if required)
    '''
    def __init__(self):
        _DiarySettings.__init__(self)
        self.fm = QtGui.QApplication.instance().fontMetrics()
        self.zoom = 3
        self._tick_positions = []
        self.reset_height(0)
        self.calc_width()
        self._months = None
        self._rect = None

    def calc_width(self):
        if self._style == self.YEAR:
            self.width = self.fm.width("8888")
        elif self._style in (self.MONTH, self.FORTNIGHT):
            self.width = 0
        else:
            self.width = self.fm.width(" 88:88 ")

    def reset_height(self, height):
        self.height = height
        self._rect = None
        self.cell_height = self.fm.height() * self.zoom
        self.total_height = self.cell_height * 48
        self.viewable_cells = self.height // self.cell_height

    @property
    def rect(self):
        if self._rect == None:
            self._rect = QtCore.QRectF(0, 0, self.width, self.height)
        return self._rect

    @property
    def tick_positions(self):
        '''
        return a list of y- co-ordinate where the times are
        '''
        return self._tick_positions

    def draw_headers(self, painter, scroll_value):
        self._tick_positions = []
        def draw_time_headers():
            option = QtGui.QTextOption(QtCore.Qt.AlignRight)

            for i in range(48):
                hour, minute = i//2, i%2*30
                y = i * self.cell_height
                rect = QtCore.QRectF(0, y, self.width, self.cell_height)
                painter.drawText(rect, "%d:%02d"% (hour, minute), option)
                self._tick_positions.append(y)

        if self._style in (self.DAY, self.FOUR_DAY, self.WEEK):
            draw_time_headers()

        elif self._style == self.YEAR:
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            cell_height = self.height / 12
            option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
            for i in range(12):
                month = self.model.header_data(scroll_value+i, self.YEAR)
                rect = QtCore.QRectF(0, i * cell_height, self.width, cell_height)
                painter.drawText(rect, month, option)

        elif self._style in (self.TASKS, self.AGENDA):
            cell_height = self.fm.height()
            option = QtGui.QTextOption(QtCore.Qt.AlignRight)

            i, y = scroll_value, 0
            while y < self.height:
                rect = QtCore.QRectF(0, y, self.width, self.cell_height)
                painter.drawText(rect, "%s" %i, option)
                self._tick_positions.append(y)
                y += cell_height
                i += 1


    def set_style(self, style):
        _DiarySettings.set_style(self, style)
        self.calc_width()

class DayCell(QtCore.QRectF, _DiarySettings):
    '''
    the cell containing data
    '''
    def __init__(self, rectf):
        QtCore.QRectF.__init__(self, rectf)
        self.time_cells = []
        self.date = None

    @property
    def is_valid(self):
        return self.date != None

    @property
    def has_time_data(self):
        return self.time_cells != []

class DiaryCanvas(QtGui.QWidget, _DiarySettings):
    '''
    The Canvas of the diary
    '''
    def __init__(self, date, parent = None):
        QtGui.QWidget.__init__(self, parent)
        _DiarySettings.__init__(self)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding))
        self.date = date
        self.model = None
        self.left_margin = DiaryCanvasLeftMargin()
        self.top_margin = DiaryCanvasTopMargin(date)
        self.apply_style()
        self.mouse_pos = QtCore.QPointF()
        self.setMouseTracking(True)
        self._year_start_day = 0 #monday
        self.scroll_value = 0
        self.painter_offset_y = 0
        self.is_resized = True

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def mouseMoveEvent(self, event):
        self.mouse_pos = QtCore.QPointF(event.pos())
        self.update()

    def mousePressEvent(self, event):
        for cell in self.day_cells:
            if cell.contains(self.mouse_pos):
                message = u""
                if cell.has_time_data:
                    for tc in cell.time_cells:
                        mp = QtCore.QPointF(self.mouse_pos)
                        mp.setY(mp.y() - self.painter_offset_y)

                        if tc.contains(mp):
                            message = "%s minutes past midnight<br />"% tc.mpm
                if cell.is_valid:
                    day_data = self.model.data(cell.date, self._style)
                    QtGui.QMessageBox.information(self,
                        "date", message + day_data.message)
                break

    def leaveEvent(self, event):
        self.mouse_pos = QtCore.QPointF()
        self.update()

    def resizeEvent(self, event=None):
        canvas_width = self.width() - self.left_margin.width
        canvas_height = self.height() - self.top_margin.height

        self.left_margin.reset_height(canvas_height)
        self.top_margin.reset_width(canvas_width)
        self.canvas_rect = QtCore.QRectF(   0,
                                            self.top_margin.height,
                                            self.width(),
                                            canvas_height)
        self.verticals = []
        if self.no_main_cols > 0:
            x = self.left_margin.width
            col_width = canvas_width/self.no_main_cols
            while x < self.width():
                self.verticals.append(
                    QtCore.QLine(x, 0, x, self.height()))
                x += col_width

        self.horizontals = []
        if self.no_rows > 0:
            y = self.top_margin.height
            row_height = canvas_height/self.no_rows
            while y < self.height():
                y += row_height
                self.horizontals.append(QtCore.QLine(0, y, self.width(), y))

        self.day_cells = []
        for row in range(self.no_rows):
            for col in range(self.no_main_cols):
                rect = QtCore.QRectF(
                            col*col_width + self.left_margin.width,
                            row*row_height + self.top_margin.height,
                            col_width,
                            row_height
                            )
                cell = DayCell(rect.adjusted(2,2,-2,-2))
                self.day_cells.append(cell)

        self.set_cell_dates()

        if self._style in (self.DAY, self.FOUR_DAY, self.WEEK):
            self.get_time_cells()
        self.is_resized = True
        self.emit(QtCore.SIGNAL("resized"))

    def set_cell_dates(self):
        if self._style in (self.AGENDA, self.TASKS):
            for cell in self.day_cells:
                cell.date = None
        elif self._style in (self.DAY, self.FOUR_DAY):
            i = 0
            for cell in self.day_cells:
                cell.date = self.date.addDays(i)
                i += 1
        elif self._style in (self.WEEK,):
            dayno = self.date.dayOfWeek()
            i = 1
            for cell in self.day_cells:
                cell.date = self.date.addDays(i-dayno)
                i += 1
        elif self._style in (self.MONTH, self.FORTNIGHT):
            startdate = self.model.start_date.addDays(self.scroll_value*7)
            dayno = startdate.dayOfWeek()
            i = 1
            for cell in self.day_cells:
                cell.date = startdate.addDays(i-dayno)
                i += 1
        elif self._style == self.YEAR:
            for cell in self.day_cells:
                cell.date = None
            for row in range(12):
                months_from_start = self.scroll_value + row
                monthdate = self.model.start_date.addMonths(months_from_start)
                monthdate = QtCore.QDate(monthdate.year(), monthdate.month(),1)
                dayno = monthdate.dayOfWeek()
                for i in range(self.no_main_cols):
                    days_to_add = i +1 - dayno
                    date = monthdate.addDays(days_to_add)
                    if date.month() == monthdate.month():
                        self.day_cells[row*37 + i].date = date

    def get_time_cells(self):
        for cell in self.day_cells:
            cell.time_cells = []
            cell_height = self.left_margin.total_height/48
            for i in range(48):
                tr = QtCore.QRectF( cell.topLeft().x(),
                                    i*cell_height,
                                    cell.width(),
                                    cell_height)
                tr.mpm = i*30
                cell.time_cells.append(tr)

    def setModel(self, model):
        self.model = model
        self.left_margin.model = model

    @property
    def row_count(self):
        '''
        return the number of rows that are visible
        '''
        if self._style in (self.DAY, self.FOUR_DAY, self.WEEK):
            return self.left_margin.viewable_cells
        return self.no_rows

    def set_date(self, date):
        self.date = date
        self.top_margin.set_date(date)
        self.year_start_date = date
        self.resizeEvent()
        self.update()

    def apply_style(self):
        self.top_margin.set_style(self._style)
        self.left_margin.set_style(self._style)
        self.text_align_option = option = QtGui.QTextOption(
            QtCore.Qt.AlignRight)

        if self._style == self.DAY:
            self.no_rows = 1
            self.no_main_cols = 1
        elif self._style == self.FOUR_DAY:
            self.no_rows = 1
            self.no_main_cols = 4
        elif self._style == self.WEEK:
            self.no_rows = 1
            self.no_main_cols = 7
        elif self._style == self.FORTNIGHT:
            self.no_rows = 2
            self.no_main_cols = 7
        elif self._style == self.MONTH:
            self.no_rows = 6
            self.no_main_cols = 7
        elif self._style == self.YEAR:
            self.no_rows = 12
            self.no_main_cols = 37
            self.text_align_option = option = QtGui.QTextOption(
                QtCore.Qt.AlignCenter)
        elif self._style in  (self.AGENDA, self.TASKS):
            self.no_rows = 1
            self.no_main_cols = 1
            self.text_align_option = option = QtGui.QTextOption(
                QtCore.Qt.AlignLeft)

    def set_style(self, style):
        '''
        set the style as day, fourday, week, fortnight, month or year
        '''
        _DiarySettings.set_style(self, style)
        self.apply_style()
        self.resizeEvent()
        self.update()

    def vscroll(self, val):
        self.scroll_value = val
        if self._style in (self.FORTNIGHT, self.MONTH, self.YEAR):
            self.set_cell_dates()
        self.update()

    def paintEvent(self, event=None):
        palette = self.palette()
        painter = QtGui.QPainter(self)

        painter.fillRect(self.rect(), palette.base().color())

        year_rect = QtCore.QRectF(0, 0,
            self.left_margin.width, self.top_margin.height)

        painter.fillRect(year_rect, palette.highlight().color())

        painter.save()
        painter.translate(self.left_margin.width, 0)
        painter.fillRect(self.top_margin.rect, palette.highlight())
        painter.restore()

        painter.save()
        painter.translate(0, self.top_margin.height)
        if self._style == self.YEAR:
            painter.fillRect(self.left_margin.rect, palette.highlight())
        else:
            painter.fillRect(self.left_margin.rect, palette.alternateBase())
        painter.restore()

        painter.save()
        painter.setPen(palette.highlightedText().color())
        painter.drawText(year_rect, str(self.date.year()),
            QtGui.QTextOption(QtCore.Qt.AlignCenter))
        painter.restore()

        #top header texts  (never scrolls)
        painter.save()
        painter.translate(self.left_margin.width, 0)
        painter.setPen(palette.highlightedText().color())
        self.top_margin.draw_headers(painter)
        painter.restore()

        self.painter_offset_y = 0

        ## the time windows

        if self._style in (self.DAY, self.FOUR_DAY, self.WEEK):
            #left header texts
            painter.save()
            painter.setClipRect(self.canvas_rect)
            self.painter_offset_y = self.top_margin.height-self.scroll_value
            painter.translate(0, self.painter_offset_y)
            self.left_margin.draw_headers(painter, 0)#self.scroll_value)

            for cell in self.day_cells:
                self.draw_date_cell(cell, painter)
                if cell.contains(self.mouse_pos):
                    for tr in cell.time_cells:
                        mp = QtCore.QPointF(self.mouse_pos)
                        mp.setY(mp.y() - self.painter_offset_y)

                        if tr.contains(mp):
                            painter.save()
                            pen = QtGui.QPen(QtGui.QColor("blue"))
                            pen.setWidth(2)
                            painter.setPen(pen)
                            painter.drawRect(tr)
                            painter.restore()
                            break

            #minor lines
            painter.setPen(palette.alternateBase().color())
            for tick in self.left_margin.tick_positions:
                painter.drawLine(0, tick, self.width(), tick)


            painter.restore()
            #major lines
            painter.setPen(palette.windowText().color())
            for line in self.verticals:
                painter.drawLine(line)
            for line in self.horizontals:
                painter.drawLine(line)


        ## the lists

        elif  self._style in (self.TASKS, self.AGENDA):
            #left header texts
            painter.save()
            painter.translate(0, self.top_margin.height)
            self.left_margin.draw_headers(painter, self.scroll_value)
            painter.restore()

            #minor lines
            painter.setPen(palette.alternateBase().color())
            for tick in self.left_margin.tick_positions:
                painter.drawLine(0, tick, self.width(), tick)

            cell = self.day_cells[0]

            appts = self.model.data(self.date).entries

            y = self.mouse_pos.y()

            lines = self.left_margin.tick_positions
            for i in range(len(lines)-1):
                if lines[i] < y < lines[i+1]:
                    painter.save()
                    pen = QtGui.QPen(QtGui.QColor("blue"))
                    pen.setWidth(2)
                    painter.setPen(pen)
                    topLeft = QtCore.QPointF(cell.x(), lines[i])
                    botRight = QtCore.QPointF(cell.bottomRight().x(),
                        lines[i+1])

                    cell_rect = QtCore.QRectF(topLeft, botRight)
                    painter.drawRect(cell_rect)
                    painter.restore()

                try:
                    if i != 0:
                        details = appts[i-1].full_details
                        topLeft = QtCore.QPointF(cell.x(), lines[i])
                        botRight = QtCore.QPointF(cell.bottomRight().x(),
                            lines[i+1])

                        cell_rect = QtCore.QRectF(topLeft, botRight)
                        painter.save()
                        painter.setPen(QtGui.QColor('black'))
                        painter.drawText(cell_rect, details)
                        painter.restore()
                except IndexError:
                    pass

        ## the cell views

        else:
            #left header texts
            painter.save()
            painter.translate(0, self.top_margin.height)
            if self._style == self.YEAR:
                painter.setPen(palette.highlightedText().color())
            self.left_margin.draw_headers(painter, self.scroll_value)
            painter.restore()

            #major lines
            painter.setPen(palette.windowText().color())
            for line in self.verticals:
                painter.drawLine(line)
            for line in self.horizontals:
                painter.drawLine(line)

            for cell in self.day_cells:
                if cell.date != None and cell.contains(self.mouse_pos):
                    painter.save()
                    pen = QtGui.QPen(QtGui.QColor("blue"))
                    pen.setWidth(2)
                    painter.setPen(pen)
                    painter.drawRect(cell.adjusted(-1,-1,1,1))
                    painter.restore()

                self.draw_date_cell(cell, painter)

        self.is_resized = False

    def draw_date_cell(self, cell, painter):
        '''
        this is the meat of the paint operation.
        at this point the cell contents are drawn
        '''

        if cell.date == None:
            if self._style == self.YEAR:
                painter.fillRect(cell.adjusted(-1,-1,1,1),
                    self.palette().background())
            return

        painter.save()
        if self._style == self.MONTH:
            if cell.date.month()%2 != cell.date.month()%2:
                painter.fillRect(cell, self.palette().alternateBase())

        data = self.model.data(cell.date, self._style)

        if self._style in (self.YEAR, self.MONTH, self.FORTNIGHT):
            if data.is_public_hol:
                brush = QtGui.QBrush(QtCore.Qt.lightGray)
                public_hol_rect = cell.adjusted(0, cell.height()*0.8, 0, 0)
                painter.fillRect(public_hol_rect, brush)
                if data.public_hol_text:
                    painter.drawText(public_hol_rect, data.public_hol_text)

            i = cell.date.day()
            if i == 1 and self._style != self.YEAR:
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)
                d_str = u"%s %s"% (
                    cell.date.shortMonthName(cell.date.month()), i)
            else:
                d_str = str(i)

            if cell.date.dayOfWeek()>5:
                painter.setPen(QtGui.QColor("red"))

            painter.drawText(cell, d_str, self.text_align_option)

            if data.has_sessions:
                #painter.drawText(cell, "session", self.text_align_option)
                #print "session found", data.session_start, data.session_finish
                day_mins = 60*24
                start = data.minutes_past_midnight(data.session_start(1))
                finish = data.minutes_past_midnight(data.session_finish(1))
                srect = QtCore.QRectF(
                    cell.x(),
                    cell.y()+start/day_mins * cell.height(),
                    cell.width(),
                    cell.height() * ((finish-start)/day_mins)
                    )
                painter.fillRect(srect, SESSION_COLOUR)
                #painter.drawText(srect, "session", self.text_align_option)

            if not data.in_bookable_range:
                painter.save()
                painter.setPen(self.palette().background().color())
                painter.drawLine(cell.topLeft(), cell.bottomRight())
                painter.restore()

        else: #DAY, FOUR_DAY or WEEK,
            if data.has_sessions:
                day_mins = 60*24
                start = data.minutes_past_midnight(data.session_start(1))
                finish = data.minutes_past_midnight(data.session_finish(1))
                day_height = self.left_margin.total_height
                srect = QtCore.QRectF(
                    cell.x(),
                    cell.y()+start/day_mins * day_height - self.top_margin.height,
                    cell.width(),
                    day_height * ((finish-start)/day_mins)
                    )
                painter.fillRect(srect, SESSION_COLOUR)

            self.draw_time_cells(cell, data, painter)

            if not data.in_bookable_range:
                painter.save()
                painter.setPen(self.palette().background().color())
                painter.drawLine(   cell.x(),
                                    cell.y(),
                                    cell.width() + self.left_margin.width,
                        self.left_margin.total_height-self.top_margin.height)
                painter.restore()

        painter.restore()

    def draw_time_cells(self, cell, data, painter):

        #for time_cell in cell.time_cells:
            #pass
            #painter.drawRect(time_cell)
            #painter.drawText(time_cell, "%s"% time_cell.mpm)

        for entry in data.entries:
            if self.is_resized or entry.rect is None:
                day_mins = 60*24
                start = data.minutes_past_midnight(entry.start)
                finish = data.minutes_past_midnight(entry.finish)
                day_height = self.left_margin.total_height
                entry.rect = QtCore.QRectF(
                    cell.x(),
                    cell.y()+start/day_mins * day_height - self.top_margin.height,
                    cell.width(),
                    day_height * ((finish-start)/day_mins)
                    )
            painter.fillRect(entry.rect, APPOINTMENT_COLOUR)
            painter.drawText(entry.rect, entry.message)

if __name__ == "__main__":



    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    dl.setMinimumSize(500,300)

    from lib_openmolar.client.db_orm.diary import DiaryDataModel
    from lib_openmolar.client.connect import DemoDiaryClientConnection
    cc = DemoDiaryClientConnection()
    cc.connect()
    model = DiaryDataModel()
    model.load()

    obj = DiaryWidget(dl)
    obj.setModel(model)

    cb = QtGui.QComboBox()
    cb.addItems(["Day","4 day", "week", "fortnight", "month",
        "year", "agenda", "tasks"])
    cb.currentIndexChanged.connect(obj.setViewStyle)

    layout = QtGui.QVBoxLayout(dl)
    layout.setMargin(0)
    layout.addWidget(obj)
    layout.addWidget(cb)

    dl.exec_()