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

import logging
from PyQt4 import QtGui, QtCore

HORIZONTAL_HEADERS = ("Code", "Description", "No.", "details",
"Px dent", "Tx dent",
"Completed", "Invoiced", "Fee Scale", "Fee", "Patient Fee" )



class TreeItem(object):
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    '''
    def __init__(self, treatment_item, header, parentItem):
        self.treatment_item = treatment_item
        self.parentItem = parentItem
        self.header = header
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(HORIZONTAL_HEADERS)

    def data(self, column):
        if self.treatment_item == None:
            if column == 0:
                return self.header
        else:
            item = self.treatment_item
            if column == 0:
                return item.code.code
            elif column == 1:
                return item.description
            elif column == 2:
                return 1
            elif column == 3:
                message = u""
                for data in item.metadata:
                    message += "%s\n"% data.brief_description
                message += item.comment
                return message.strip("\n")
            elif column == 4:
                return str(item.px_clinician)
            elif column == 5:
                return str(item.tx_clinician)
            elif column == 6:
                if item.is_completed:
                    return item.cmp_date

        return QtCore.QVariant()

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

class TreatmentTreeModel(QtCore.QAbstractItemModel):
    '''
    a model to display treatment items
    This is purely a display vessel for :doc:`TreatmentModel`
    '''
    def __init__(self, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.setupModelData()

    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(HORIZONTAL_HEADERS)

    def update_treatments(self):
        '''
        this should be called whenever a treatment is added
        '''
        self.setupModelData()

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.UserRole:
            if item:
                return item.treatment_item

        return QtCore.QVariant()

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
        role == QtCore.Qt.DisplayRole):
            try:
                return QtCore.QVariant(HORIZONTAL_HEADERS[column])
            except IndexError:
                pass

        return QtCore.QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
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

        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            p_Item = self.rootItem
        else:
            p_Item = parent.internalPointer()
        return p_Item.childCount()

    def setupModelData(self):
        self.beginResetModel()
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}

        if SETTINGS.current_patient is None:
            LOGGER.debug("TreatmentTreeModel - no patient")
            treatment_items = []
        else:
            LOGGER.debug("loading patient's treatment model")
            model = SETTINGS.current_patient.treatment_model
            treatment_items = sorted(model.treatment_items)
        for treatment_item in treatment_items:
            category = treatment_item.category
            if not self.parents.has_key(category):
                newparent = TreeItem(None, category, self.rootItem)
                self.rootItem.appendChild(newparent)

                self.parents[category] = newparent

            parentItem = self.parents[category]
            newItem = TreeItem(treatment_item, "", parentItem)
            parentItem.appendChild(newItem)
        self.endResetModel()

class _TestDialog(QtGui.QMainWindow):
    def __init__(self, model, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.tree_view = QtGui.QTreeView(self)
        self.tree_view.setModel(model)
        self.tree_view.setAlternatingRowColors(True)

        self.setCentralWidget(self.tree_view)

    def sizeHint(self):
        return QtCore.QSize(800,300)


if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)

    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import DemoClientConnection
    from lib_openmolar.client.db_orm import PatientModel

    cc = DemoClientConnection()
    cc.connect()

    obj = PatientModel(1)
    SETTINGS.set_current_patient(obj)

    model = TreatmentTreeModel()

    mw = _TestDialog(model)
    mw.show()
    app.exec_()
