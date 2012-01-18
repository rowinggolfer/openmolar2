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
gets records from the staff table
'''

from PyQt4 import QtCore, QtGui, QtSql, QtSvg

class StaffAvatarWidget(QtSvg.QSvgWidget):
    '''
    A QtSvg.QSvgWidget, which appears differently if it :attr:`is_active`
    '''
    
    def __init__(self, parent=None):
        QtSvg.QSvgWidget.__init__(self, parent)
        #self.setMouseTracking(True)
        
        #:
        self.is_active = False
        self.setMaximumSize(self.sizeHint())

    def mousePressEvent(self, event):
        self.is_active = not self.is_active
        self.update()

    def sizeHint(self):
        return QtCore.QSize(60, 60)

    def paintEvent(self, event):
        QtSvg.QSvgWidget.paintEvent(self, event)
        if self.is_active:
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QColor("blue"))
            painter.drawRoundedRect(self.rect().adjusted(2,2,-2,-2), 10, 10)

class StaffObject(QtSql.QSqlRecord):
    def __init__(self, record):
        QtSql.QSqlRecord.__init__(self, record)
        self._avatar = None

    @property
    def full_name(self):
        return u"%s %s"% (self.value("first_name").toString(),
            self.value("last_name").toString())

    @property
    def qualifications(self):
        return self.value("qualifications").toString()

    @property
    def role(self):
        return self.value("role").toString()

    @property
    def avatar_widget(self):
        if self._avatar == None:
            self._avatar = StaffAvatarWidget()
            self._avatar.load(self.value("svg_data").toByteArray())
            self._avatar.setToolTip(self.toHtml())
        return self._avatar

    def toHtml(self):
        return '''<html><body>%s %s <br />%s</body</html>'''% (
            self.full_name, self.qualifications, self.role)

class StaffMembers(list):
    def __init__(self):
        self.get_records()

    def get_records(self):
        query = '''SELECT staff.ix, first_name, last_name, qualifications,
        role, abbrv_name, svg_data
        from staff left join avatars on avatar_id = avatars.ix'''

        q_query = QtSql.QSqlQuery(query, SETTINGS.psql_conn)
        while q_query.next():
            record = q_query.record()
            practitioner = StaffObject(record)
            self.append(practitioner)

if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    staff_members = StaffMembers(cc)
    for member in staff_members:
        print member.toHtml()
