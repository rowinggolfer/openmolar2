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
provides objects which display the practitioners and their avatars etc.
'''

from PyQt4 import QtCore, QtGui, QtSql, QtSvg


class PractitionerListModel(QtCore.QAbstractListModel):
    '''
    provides a model for use in comboboxes etc.. when user has to choose
    from the list of current practitioners
    '''
    def __init__(self, practitioners, parent=None):
        QtCore.QAbstractListModel.__init__(self, parent)
        #:
        self.practitioners = practitioners

    def rowCount(self, index):
        return len(self.practitioners)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self.practitioners[index.row()].full_name
        elif role == QtCore.Qt.DecorationRole:
            return self.practitioners[index.row()].icon
        elif role == QtCore.Qt.UserRole:
            return self.practitioners[index.row()]
        return QtCore.QVariant()

    def headerData(self, column_no, orientation, role=QtCore.Qt.DisplayRole):
        '''
        not called by combobox.. but of use to listviews
        '''
        if role == QtCore.Qt.DisplayRole:
            if column_no == 0:
                return _("Practitioners")
        return QtCore.QVariant()

class AvatarWidget(QtSvg.QSvgWidget):
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
        return QtCore.QSize(80, 80)

    def paintEvent(self, event):
        QtSvg.QSvgWidget.paintEvent(self, event)
        if self.is_active:
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QColor("blue"))
            painter.drawRoundedRect(self.rect().adjusted(2,2,-2,-2), 10, 10)

class PractitionerObject(QtSql.QSqlRecord):
    def __init__(self, record):
        QtSql.QSqlRecord.__init__(self, record)
        self._avatar_widg = None
        self._user = None

    @property
    def is_hygienist(self):
        return self.value("type").toString() == "hygienist"

    @property
    def user(self):
        '''
        all practitioners are also users (ie. exist in SETTINGS.users
        '''
        if self._user == None:
            uid = self.value("user_id").toInt()[0]
            self._user = SETTINGS.users[uid]
        return self._user

    @property
    def id(self):
        '''
        returns an int - the id of the practitioner
        '''
        return self.value("practitioner_id").toInt()[0]

    @property
    def full_name(self):
        return u"%s %s %s"% (
            self.value("title").toString(),
            self.value("first_name").toString(),
            self.value("last_name").toString())

    @property
    def abbrv_name(self):
        return self.value("abbrv_name").toString()

    @property
    def qualifications(self):
        return self.value("qualifications").toString()

    @property
    def type(self):
        return self.value("type").toString()

    @property
    def is_active(self):
        return self.value("status").toString() == "active"

    @property
    def icon(self):
        return self.user.icon

    @property
    def avatar_resource(self):
        '''
        returns the location of the svg file of this users avatar
        '''
        return self.user.avatar_resource

    @property
    def avatar_widget(self):
        if self._avatar_widg == None:
            svg_data = self.value("svg_data").toByteArray()

            self._avatar_widg = AvatarWidget()
            self._avatar_widg.load(svg_data)
            self._avatar_widg.setToolTip(self.toHtml())
        return self._avatar_widg

    def toHtml(self):
        return '''<html><body>
            <ul>
            <li>%s</li>
            <li>%s</li>
            <li>%s</li>
            </ul>
            </body</html>'''% (self.full_name, self.qualifications, self.type)

class Practitioners(object):
    '''
    this, at its heart is an ordered dict
    '''
    def __init__(self):
        self._no = -1
        self._order = {}
        self._dict = {}

        self.get_records()

        self._model = None
        self._dentists_model = None

    def get_records(self):

        query = '''SELECT practitioner_id, user_id,
        title, first_name, last_name,
        qualifications, type, abbrv_name, svg_data, status
        from view_practitioners order by display_order, last_name'''

        q_query = QtSql.QSqlQuery(query, SETTINGS.psql_conn)
        while q_query.next():
            record = q_query.record()
            practitioner = PractitionerObject(record)

            self[record.value(0).toInt()[0]] = practitioner

    @property
    def active_practitioners(self):
        '''
        a list of ACTIVE practitioner names
        '''
        for practitioner in self:
            if practitioner.is_active:
                yield practitioner

    @property
    def active_dentist_list(self):
        dents = []
        for practitioner in self.active_practitioners:
            if practitioner.type == "dentist":
                dents.append(practitioner)
        return dents

    def index(self, practitioner):
        for i in range(self._no):
            if self[i] == practitioner:
                return i
        return -1

    def practitioner_from_user(self, user):
        '''
        if :doc:`UserObject` is a practitioner, this function will return them
        '''
        if not user:
            return
        for practitioner in self:
            if practitioner.user.id == user.id:
                return practitioner

    @property
    def model(self):
        '''
        a model for use in 1 dimensional views (eg comboboxes)
        '''
        if self._model is None:
            self._model = PractitionerListModel(self)
        return self._model

    @property
    def dentists_model(self):
        '''
        a model for use in 1 dimensional views (eg comboboxes)
        '''
        if self._dentists_model is None:
            self._dentists_model = PractitionerListModel(self.active_dentist_list)
        return self._dentists_model

    def keys(self):
        return self._dict.keys()

    def value(self, key):
        return self._dict[key]

    def __setitem__(self, key, val):
        self._no += 1
        self._order[self._no] = key
        self._dict[key] = val

    def __getitem__(self, i):
        key = self._order[i]
        return self._dict[key]

    def __iter__(self):
        for i in range(self._no):
            yield self[i]

    def __len__(self):
        return len(self._dict)

if __name__ == "__main__":

    app = QtGui.QApplication([])
    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    practitioners = Practitioners(cc)
    for practitioner in practitioners:
        print practitioner.full_name
        #print practitioner.toHtml()
        print practitioner.avatar_resource

    print practitioners[0].full_name

    cb = QtGui.QComboBox()
    cb.setModel(practitioners.dentists_model)
    cb.show()
    app.exec_()
