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
gets records from the users table
'''
import os
from PyQt4 import QtCore, QtGui, QtSql, QtSvg

class GeneratedSvg(QtSvg.QSvgGenerator):
    '''
    Creates an svg from text, saving to a location given at __init__
    '''
    def __init__(self, text, save_location):
        '''
        :param: text to be rendered
        :param: filepath to write to
        '''
        QtSvg.QSvgGenerator.__init__(self)

        self.setFileName(save_location)
        self.setTitle("mock svg")
        self.setSize(QtCore.QSize(40,40))
        self.setViewBox(QtCore.QRect(2,2,36,36))

        painter = QtGui.QPainter()
        painter.begin(self)
        #painter.fillRect(gen.viewBox(), QtGui.QColor("blue"))
        font = painter.font()
        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(self.viewBox(),
                         QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap,
                         text)
        #painter.drawEllipse(self.viewBox())
        painter.end()

class UserObject(QtSql.QSqlRecord):
    def __init__(self, record):
        QtSql.QSqlRecord.__init__(self, record)
        self._svg_filepath = None
        self._avatar_resource = None
        self._icon = None

    @property
    def id(self):
        '''
        returns the database ix for this user
        '''
        return self.value("ix").toInt()[0]

    @property
    def abbrv_name(self):
        return self.value("abbrv_name").toString()

    @property
    def full_name(self):
        return u"%s %s %s"% (  self.value("title").toString(),
                            self.value("first_name").toString(),
                            self.value("last_name").toString())

    @property
    def is_active(self):
        return self.value("status").toString() == "active"

    @property
    def role(self):
        return self.value("role").toString()

    @property
    def svg_filepath(self):
        '''
        returns the location of the file holding the users svg data
        if user has  no svg data, a :doc:`GeneratedSvg` is created
        '''
        if self._svg_filepath is None:
            loc = str(QtCore.QDir.tempPath())
            svg_data = self.value("svg_data").toByteArray()
            path = os.path.join(loc, "om_avatar_XXXXXX.svg")
            f = QtCore.QTemporaryFile(path)
            f.setAutoRemove(False)
            if svg_data:
                if f.open(QtCore.QIODevice.WriteOnly):
                    f.writeData(svg_data)
            else:
                if f.open(QtCore.QIODevice.WriteOnly):
                    GeneratedSvg(self.abbrv_name, f.fileName())

            self._svg_filepath = f.fileName()
        return self._svg_filepath

    @property
    def icon(self):
        if self._icon is None:
            self._icon = QtGui.QIcon(self.svg_filepath)
        return self._icon

    @property
    def avatar_resource(self):
        if self._avatar_resource is None:
            self._avatar_resource = "file://%s"% (self.svg_filepath)
        return self._avatar_resource

    def toHtml(self):
        return '''<html><body>%s<br />%s</body</html>'''% (
            self.full_name, self.role)

class Users(object):
    def __init__(self):
        self._no = 0
        self._order = {}
        self._dict = {}

        self.get_records()

    def get_records(self):
        self._dict = {}
        query = '''SELECT users.ix, abbrv_name, title, first_name, last_name,
        role, svg_data, status
        from users left join avatars on avatar_id = avatars.ix
        order by display_order, last_name'''

        q_query = QtSql.QSqlQuery(query, SETTINGS.psql_conn)
        while q_query.next():
            record = q_query.record()
            user = UserObject(record)
            self[record.value(0).toInt()[0]] = user

    @property
    def abbrv_name_list(self):
        '''
        a list of initials of ACTIVE users
        '''
        abbrv_names = []
        for user in self:
            if user.is_active:
                abbrv_names.append(user.abbrv_name)
        return abbrv_names

    def user_from_abbrv_name_list_index(self, index):
        '''
        the equivalent of abbrv_name_list[i]
        '''
        i = 0
        for user in self:
            if user.is_active:
                if i == index:
                    return user
                i += 1

    def __setitem__(self, key, val):
        self._order[self._no] = key
        self._dict[key] = val
        self._no += 1

    def __getitem__(self, i):
        return self._dict[i]

    def __iter__(self):
        for i in range(self._no):
            yield self[self._order[i]]

    def get(self, key, alt=None):
        try:
            return self._dict[key]
        except KeyError:
            return alt

    def get_avatar_html(self, key, options=""):
        user = self.get(key)
        if user is None:
            return "%s (?)"% user
        return '<img src = "%s" alt="%s" %s/>' % (
            user.avatar_resource, key, options)

if __name__ == "__main__":

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    for member in SETTINGS.users:
        print member.toHtml()
        print member.avatar_resource
        print member.is_active
