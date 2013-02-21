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

from PyQt4 import QtSql, QtCore, QtGui

if __name__ == "__main__":
    from gettext import gettext as _

HORIZONTAL_HEADERS = (
    _("Date & Time"),
    _("Practitioner"),
    _("Length"),
    _("Treatment"),
    _("Memo")
    )


class _TreeItem(object):
    is_appointment = False
    def __init__(self, parent):
        self.parent = parent
        self.children = []

    def child(self, row):
        return self.children[row]

    def row_count(self):
        return len(self.children)

    def clear(self):
        self.children = []

    def row(self):
        try:
            if self.parent:
                return self.parent.children.index(self)
        except ValueError:
            LOGGER.exception("_TreeItem.row exception")
        return 0

    def data(self, column):
        if column == 0:
            return _("View Past Appointments")
        return QtCore.QVariant()

    def append_child(self, child):
        self.children.append(child)

class _AppointmentTreeItem(_TreeItem):
    is_appointment = True
    def __init__(self, appointment, parent):
        _TreeItem.__init__(self, parent)
        self.appointment = appointment
        self.date_ = self.appointment.value("start").toDate()

    @property
    def is_today(self):
        return self.date_== QtCore.QDate.currentDate()

    @property
    def is_past(self):
        return (self.date_ < QtCore.QDate.currentDate() and
            not self.date_.isNull())

    @property
    def is_unscheduled(self):
        return self.date_.isNull()

    def data(self, column):
        if column == 0:
            if self.is_unscheduled:
                return _("TBA")
            return self.appointment.value("start").toDateTime()
        if column == 1:
            return self.appointment.value("diary_id").toString()
        if column == 2:
            value, result = self.appointment.value("len").toInt()
            if result:
                return u"%s %s"% (value, _("minutes"))
        if column == 3:
            trt1 = self.appointment.value("trt1").toString()
            trt2 = self.appointment.value("trt2").toString()
            return u"%s %s"% (trt1, trt2)
        if column == 4:
            return self.appointment.value("preferred_practitioner").toString()
        if column == 5:
            return self.appointment.value("memo").toString()

        return QtCore.QVariant()

class PatientDiaryModel(QtCore.QAbstractItemModel):
    '''
    a model to display a the patient diary in a sensible manner
    '''

    _normal_icon = None
    _selected_icon = None

    def __init__(self, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)

        self.model = QtSql.QSqlQueryModel(parent)

        self.root_item = _TreeItem(None)
        self._past_items = None

    @property
    def normal_icon(self):
        if self._normal_icon == None:
            self._normal_icon = QtGui.QIcon()
            self._normal_icon.addPixmap(QtGui.QPixmap(":/schedule.png"),
                QtGui.QIcon.Normal, QtGui.QIcon.Off)
        return self._normal_icon

    @property
    def selected_icon(self):
        if self._selected_icon == None:

            self.selected_icon = QtGui.QIcon()
            self.selected_icon.addPixmap(
                QtGui.QPixmap(":/icons/schedule_active.png"))
        return self._selected_icon

    @property
    def past_items(self):
        if self._past_items is None:
            self._past_items = _TreeItem(self.root_item)
            self.root_item.append_child(self._past_items)
        return self._past_items

    def columnCount(self, parent):
        return len(HORIZONTAL_HEADERS)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.ForegroundRole and item.is_appointment:
            if item.is_today:
                return QtGui.QBrush(SETTINGS.COLOURS.PT_DIARY_TODAY)
            if item.is_past:
                return QtGui.QBrush(SETTINGS.COLOURS.PT_DIARY_PAST)
            if item.is_unscheduled:
                return QtGui.QBrush(SETTINGS.COLOURS.PT_DIARY_TBA)

        return QtCore.QVariant()

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
        role == QtCore.Qt.DisplayRole):
            return HORIZONTAL_HEADERS[column]

        return QtCore.QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.root_item
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        if not childItem:
            return QtCore.QModelIndex()

        parentItem = childItem.parent

        if parentItem == None:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, index):
        if not index.isValid():
            parent_item = self.root_item
        else:
            parent_item = index.internalPointer()

        return parent_item.row_count()

    def clear(self):
        self.beginResetModel()
        self.root_item.clear()
        self._past_items = None
        self.endResetModel()

    def set_patient(self, patient_id):
        self.beginResetModel()
        LOGGER.debug("PatientDiaryModel.set_patient(%d)"% patient_id)
        self.root_item.clear()
        query = '''select * from
        appointments left join diary_entries
        on appointments.diary_entry_id = diary_entries.ix
        where patient_id = ?
        order by start'''
        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        q_query.addBindValue(patient_id)
        q_query.exec_()
        if q_query.lastError().isValid():
            LOGGER.error("PatientDiaryModel.set_patient(%d)\n%s"% (
                patient_id,
                q_query.lastError().text()
                ))

        self.model.setQuery(q_query)

        LOGGER.debug("PatientDiaryModel.rowcount = %d"% self.model.rowCount())
        for row in range(self.model.rowCount()):
            record = self.model.record(row)
            date_ = record.value("start").toDate()
            if date_.isNull() or date_ >= QtCore.QDate.currentDate():
                parent = self.root_item
            else:
                parent = self.past_items
            item = _AppointmentTreeItem(record, parent)
            parent.append_child(item)
        self.endResetModel()

if __name__ == "__main__":
    from lib_openmolar.client.connect import DemoClientConnection

    app = QtGui.QApplication([])

    cc = DemoClientConnection()
    cc.connect()

    model = PatientDiaryModel()

    tv = QtGui.QTreeView()
    tv.setMinimumWidth(800)
    tv.setModel(model)
    tv.setAlternatingRowColors(True)
    tv.show()


    model.set_patient(1)
    model.clear()
    model.set_patient(1)


    app.exec_()
