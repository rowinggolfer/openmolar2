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

from PyQt4 import QtCore, QtSql

class _DiarySettings(object):

    DAY = 0
    FOUR_DAY = 1
    WEEK = 2
    FORTNIGHT = 3
    MONTH = 4
    YEAR = 5
    AGENDA = 6
    TASKS = 7

    DAY_VIEWS = (DAY, FOUR_DAY, WEEK, FORTNIGHT)

    def __init__(self):
        self._style = self.DAY

    def set_style(self, style):
        assert style>=self.DAY and style<=self.TASKS
        self._style = style

class Appointment(object):
    def __init__(self, record): #date, hour, minute, length, name):
        self.start = record.value("start").toDateTime()
        self.finish =  record.value("finish").toDateTime()
        self.type = record.value('type').toString()
        self.comments = record.value('comments').toString()
        self.rect = None

    @property
    def message(self):
        return u"%s %s"% (self.type, self.comments)

    @property
    def full_details(self):
        return u"%s %s %s"% (self.start.toString(), self.type, self.comments)

    def __repr__(self):
        return "appointment %s %s %s %s"% (
            self.start, self.finish, self.type, self.comments)


class DayData(object):
    def __init__(self, practice_id=1):
        self.sessions_loaded = False
        self._appointments = None

        self.practice_id = practice_id
        self.date = None

        self._diaries = {}
        self._diary_list = None
        self._public_hol_text = ""
        self.in_bookable_range = False
        self._session_start = None
        self._session_finish = None

    def __repr__(self):
        return "Daydata %s %s with diaries=%s"% (
            self.public_hol_text,
            self.message,
            self.diaries)

    def clear(self):
        self.sessions_loaded = False
        self._diaries_loaded = False

    @property
    def appointments(self):
        if self._appointments is None:
            self.load_appointments()
        return self._appointments

    @property
    def public_hol_text(self):
        return self._public_hol_text

    def set_public_hol_text(self, text):
        self._public_hol_text = text

    @property
    def is_public_hol(self):
        return self._public_hol_text != ""

    @property
    def has_session(self):
        return self._session_start != None and self._session_finish != None

    def set_session_start(self, start):
        self._session_start = start

    @property
    def session_start(self):
        return self._session_start

    def set_session_finish(self, finish):
        self._session_finish = finish

    @property
    def session_finish(self):
        return self._session_finish

    @property
    def message(self):
        try:
            message =  u"%s <br />%s - %s"% (
                _("session"),
                self.session_start.toString(),
                self.session_finish.toString())
        except AttributeError:
            message = _("no session")
        return message

    @property
    def diaries(self):
        if self._diary_list == None:
            self._diary_list = sorted(self._diaries.keys())
        return self._diary_list

    def minutes_past_midnight(self, dtime):
        '''
        takes either a QDateTime, or a QTime, and returns the minutes past
        midnight
        '''
        if type(dtime) == QtCore.QDateTime:
            dtime = dtime.time()
        return dtime.hour() * 60 + dtime.minute()

    def load_sessions(self):
        '''
        loads all appointments of type "session" for this day
        '''
        q_query = QtSql.QSqlQuery(SETTINGS.database)

        query = '''select start, finish
        from  diary_sessions where practice_id = ? and date(start) = ?'''
        q_query.prepare(query)
        q_query.addBindValue(self.practice_id)
        q_query.addBindValue(self.date)

        q_query.exec_()
        if q_query.lastError().isValid():
            print q_query.lastError().text()
        while q_query.next():
            record = q_query.record()

            start = record.value("start").toDateTime()
            finish =  record.value("finish").toDateTime()

            self.set_session_start(start)
            self.set_session_finish(finish)

        q_query.finish()

        self.sessions_loaded = True

    def load_appointments(self):
        '''
        loads all appointments of type "session" for this day
        '''

        q_query = QtSql.QSqlQuery(SETTINGS.database)

        query = '''select diary_id, start, finish, type, comments
        from diary_appointments where diary_id = ? and date(start) = ?
        order by start'''

        q_query.prepare(query)
        q_query.addBindValue(4)  ## todo fix when ^ no of diaries
        q_query.addBindValue(self.date)

        self._appointments = []
        q_query.exec_()
        if q_query.lastError().isValid():
            print q_query.lastError().text()
        while q_query.next():
            record = q_query.record()
            appt = Appointment(record)

            self._appointments.append(appt)

        q_query.finish()

class DiaryDataModel(_DiarySettings):
    '''
    This is a custom model, which forms a bridge between the client
    and the database
    '''
    def __init__(self, practice_id = 1):
        self._data = {}
        self.practice_id = practice_id
        #default values in case db isn't open
        self.start_date = QtCore.QDate.currentDate().addYears(-2)
        self.end_date = QtCore.QDate.currentDate().addYears(2)
        self.last_day = QtCore.QDate.currentDate().addMonths(6)

    def __repr__(self):
        data_repr = ""
        for key in self._data:
            data_repr += "%s:%s\n"% (key, self._data[key])
        return "DiaryDataModel\ndb=%s\npractice=%s\nstart=%s\nend=%s\n%s"% (
            SETTINGS.database.databaseName(),
            self.practice_id,
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
        query = '''select book_start, book_end, last_day
        from diary_settings where practice_id = ?'''
        q_query = QtSql.QSqlQuery(SETTINGS.database)
        q_query.prepare(query)
        q_query.addBindValue(self.practice_id)
        q_query.exec_()
        if q_query.last():
            record = q_query.record()
            self.start_date = record.value("book_start").toDate()
            self.end_date = record.value("book_end").toDate()
            self.last_day = record.value("last_day").toDate()
        else:
            print "WARNING - using default limits for diary"

    def init_data(self):
        '''
        when called this initiates a dictionary of key value pairs
        where keys are all dates between the start and end values
        and the values are DayDataObjects with only public holiday data loaded
        '''
        q_query = QtSql.QSqlQuery(SETTINGS.database)

        #due to database constraints, this list will be a
        #set of key value pairs.
        query = '''select dt, event
        from (SELECT dt FROM generate_dates(?, ?, 1) dt)  as gen
        left join diary_calendar on dt = date_id'''

        q_query.prepare(query)
        q_query.addBindValue(self.start_date)
        q_query.addBindValue(self.end_date)

        q_query.exec_()
        while q_query.next():
            record = q_query.record()
            day_data = DayData()
            day_data.set_public_hol_text(record.value("event").toString())
            day_data.date = record.value("dt").toDate()
            if QtCore.QDate.currentDate() <= day_data.date <= self.last_day:
                day_data.in_bookable_range = True
            ##QDate.__hash__ has a bug.. so have to convert here
            self._data[day_data.date.toPyDate()] = day_data

        q_query.finish()

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

        return 200

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
            day_data = DayData()
            day_data.date = date
            self._data[date.toPyDate()] = day_data

        if view_style != self.TASKS:
            if not day_data.sessions_loaded:
                day_data.load_sessions()

        return day_data

    def header_data(self, row, style=0):
        if style == self.YEAR:
            date = self.start_date.addMonths(row)
            month_name = date.shortMonthName(date.month())
            return u"%s %s" %(month_name, date.year())
        else:
            return "??"


if __name__ == "__main__":



    import os, sys
    sys.path.insert(0, os.path.abspath("../../../../../"))

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    model = DiaryDataModel()
    model.load()
    day_data = model.data(QtCore.QDate(2011,12,25))
    print "public hol - ", day_data.is_public_hol, day_data.public_hol_text

    print model
