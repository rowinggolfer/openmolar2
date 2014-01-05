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

'''
provides one 'private' class DiaryDayData
'''
from PyQt4 import QtCore, QtSql
from diary_appointment import DiaryAppointment

class DiaryDayData(object):
    '''
    this object stores information gleaned from the diary of the database.
    '''
    def __init__(self, date):
        self.sessions_loaded = False
        self._entries = None

        self.date = date

        self._diaries = {}
        self._diary_list = None
        self._public_hol_text = ""
        self.in_bookable_range = False
        self._sessions = {}

    def __repr__(self):
        return "DiaryDayData %s (%d Diaries), %s, %s" % (
        self.date.toString("yyyy-MM-dd"), len(self._diaries),
        self._sessions, self.entries)

    def clear(self):
        self.sessions_loaded = False
        self._diaries_loaded = False

    @property
    def entries(self):
        if self._entries is None:
            self.load_entries()
        return self._entries

    @property
    def public_hol_text(self):
        return self._public_hol_text

    def set_public_hol_text(self, text):
        self._public_hol_text = text

    @property
    def is_public_hol(self):
        return self._public_hol_text != ""

    @property
    def has_sessions(self):
        return self._sessions != {}

    def set_session_start(self, diary_id, start):
        try:
            self._sessions[diary_id]["start"] = start
        except KeyError:
            self._sessions[diary_id]={"start":start}

    def session_start(self, diary_id):
        if not self.sessions_loaded:
            self.load_sessions()
        try:
            return self._sessions.get(diary_id).get("start")
        except KeyError:
            return None

    def set_session_finish(self, diary_id, finish):
        self._sessions[diary_id]["finish"] = finish

    def session_finish(self, diary_id):
        if not self.sessions_loaded:
            self.load_sessions()
        try:
            return self._sessions.get(diary_id).get("finish")
        except KeyError:
            return None

    @property
    def message(self):
        message =  u"<b>%s</b><ul>"% _("sessions")
        for diary_id in self.diaries:
            message += "<li>Diary  - %s %s - %s</li>"% (
                diary_id,
                self.session_start(diary_id).toString(),
                self.session_finish(diary_id).toString())
        return u"%s </ul>"% message

    @property
    def diaries(self):
        LOGGER.debug("%s diaries"% self)

        if self._diary_list == None:
            self._diary_list = sorted(self._sessions.keys())
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
        LOGGER.debug("%s load_sessions"% self)
        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)

        query = '''select diary_id, start, finish
        from  diary_in_office where date(start) = ?'''
        q_query.prepare(query)
        q_query.addBindValue(self.date)

        q_query.exec_()
        if q_query.lastError().isValid():
            LOGGER.error("%s"% q_query.lastError().text())
            LOGGER.debug("query was %s"% q_query.lastQuery())
        while q_query.next():
            record = q_query.record()
            diary_id = record.value("diary_id").toInt()[0]
            start = record.value("start").toDateTime()
            finish =  record.value("finish").toDateTime()

            self.set_session_start(diary_id, start)
            self.set_session_finish(diary_id, finish)

        q_query.finish()

        self.sessions_loaded = True

    def load_entries(self):
        '''
        loads all appointments of type "session" for this day
        '''
        LOGGER.debug("load_entries for date %s"% self.date)
        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)

        query = '''select diary_id, start, finish, etype, comment
        from diary_entries where date(start) = ?
        order by start'''

        q_query.prepare(query)
        q_query.addBindValue(self.date)

        self._entries = []
        q_query.exec_()
        if q_query.lastError().isValid():
            LOGGER.error("%s"% q_query.lastError().text())
            LOGGER.debug("query was %s"% q_query.lastQuery())
        while q_query.next():
            record = q_query.record()
            entry = DiaryAppointment(record)
            self._entries.append(entry)
        q_query.finish()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level = logging.DEBUG)
    LOGGER = logging.getLogger("test")

    from PyQt4 import QtGui
    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    day_data = DiaryDayData(QtCore.QDate(2013,03,18))
    LOGGER.debug("%s"% day_data)
    LOGGER.debug("public hol - %s %s"% (
        day_data.is_public_hol, day_data.public_hol_text))
    day_data.load_sessions()
    LOGGER.debug("day_data diaries %s"% day_data.diaries)
    LOGGER.debug("day_data message '%s'"% day_data.message)

    LOGGER.debug("day_data entries '%s'"% day_data.entries)

