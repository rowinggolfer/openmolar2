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

from PyQt4 import QtCore, QtSql
from diary_settings import _DiarySettings
from diary_day_data import DiaryDayData

class DiaryDataModel(_DiarySettings):
    '''
    This is a custom model, which forms a bridge between the client
    and the database
    '''
    def __init__(self):
        self._data = {}
        self._active_diaries = None
        #default values in case db isn't open
        self.start_date = QtCore.QDate.currentDate().addYears(-2)
        self.end_date = QtCore.QDate.currentDate().addYears(2)

        ##TODO this should be user settable.
        self.last_day = QtCore.QDate.currentDate().addMonths(6)

    def __repr__(self):
        data_repr = ""
        for key in self._data:
            data_repr += "%s:%s\n"% (key, self._data[key])
        return '''DiaryDataModel
        db     = %s
        start  = %s
        end    = %s
        =========   DATA STARTS   ==============\n%s
        =========   DATA ENDS     =============='''% (
            SETTINGS.psql_conn.databaseName(),
            self.start_date,
            self.end_date,
            data_repr)

    def load(self):
        self._data = {}
        self.get_bounds()
        self.init_data()

    def get_bounds(self):
        '''
        poll the database for start, end and appointment limits
        '''
        query = 'select min(book_start), max(book_end) from diaries'
        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)

        q_query.exec_()
        if q_query.last():
            record = q_query.record()
            self.start_date = record.value("min").toDate()
            self.end_date = record.value("max").toDate()
        else:
            LOGGER.warning("using default limits for diary")

    def init_data(self):
        '''
        when called this initiates a dictionary of key value pairs
        where keys are all dates between the start and end values
        and the values are DayDataObjects with only public holiday data loaded
        '''
        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)

        #due to database constraints, this list will be a
        #set of key value pairs.
        query = '''select dt, event
        from (SELECT dt FROM generate_dates(?, ?, 1) dt) as gen
        left join calendar on dt = date_id'''

        q_query.prepare(query)
        q_query.addBindValue(self.start_date)
        q_query.addBindValue(self.end_date)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()
            day_data = DiaryDayData(record.value("dt").toDate())
            day_data.set_public_hol_text(record.value("event").toString())
            if QtCore.QDate.currentDate() <= day_data.date <= self.last_day:
                day_data.in_bookable_range = True
            ##QDate.__hash__ has a bug.. so have to convert here
            ##this has been fixed in recent PyQt4..
            ##there may be a perfomance benefit here
            self._data[day_data.date.toPyDate()] = day_data

        q_query.finish()

    @property
    def active_diaries(self):
        '''
        poll the database (one time only) and get active diary ids.
        '''
        if self._active_diaries is None:
            active_diaries = []
            q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)

            query = '''select ix from diaries where active'''

            q_query.prepare(query)
            q_query.exec_()
            while q_query.next():
                record = q_query.record()
                active_diaries.append(record.value("ix").toInt()[0])
            self._active_diaries = tuple(active_diaries)
        return self._active_diaries

    def rowCount(self, style):
        if style in (self.DAY, self.WEEK, self.FOUR_DAY):
            return 24
        if style in (self.MONTH, self.FORTNIGHT): #1 week per row
            i =0
            start = self.start_date
            while start < self.end_date:
                start = start.addDays(7)
                i += 1
            return i

        if style == self.YEAR: #return the number of months.
            i = 0
            start = self.start_date
            while (start.year(), start.month()) < (self.end_date.year(), self.end_date.month()):
                i += 1
                start = start.addMonths(1)
            return i

        return 100

    def row_from_date(self, date, style):
        '''
        returns the relative position of the date in the rows displayed
        '''
        rowcount = self.rowCount(style)
        if style == self.YEAR:
            past_years = date.year() - self.start_date.year()
            return past_years*12 - self.start_date.month() + date.month()
        if style in (self.MONTH, self.FORTNIGHT):
            i = 0
            start = self.start_date
            while start <= date:
                start = start.addDays(7)
                i += 1

            if style == self.MONTH:
                i -= date.day()//7

            return i
        return 1

    def data(self, date, view_style=0):
        '''
        returns a 'DayData' object for the date requested
        '''

        ##QDate.__hash__ has a bug.. so have to convert here
        try:
            day_data = self._data[date.toPyDate()]

        except KeyError:
            day_data = DiaryDayData(date)
            self._data[date.toPyDate()] = day_data

        if view_style != self.TASKS:
            if not day_data.sessions_loaded:
                day_data.load_sessions()

        return day_data

    def new_data(self, d1t, dt2, diary_ids, view_style=0):
        '''
        returns a 'DayData' objects for the date range requested
        and specified diary ids
        '''
        return "NEW DATA"


    def header_data(self, row, style=0):
        if style == self.YEAR:
            date = self.start_date.addMonths(row)
            month_name = date.shortMonthName(date.month())
            return u"%s %s" %(month_name, date.year())
        else:
            return "??"


if __name__ == "__main__":

    import logging
    logging.basicConfig(level = logging.DEBUG)
    LOGGER = logging.getLogger("test")

    from PyQt4 import QtGui
    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    model = DiaryDataModel()
    model.load()

    today = QtCore.QDate.currentDate()
    for i in range(7):
        model.data(today.addDays(i))

    print (model)
