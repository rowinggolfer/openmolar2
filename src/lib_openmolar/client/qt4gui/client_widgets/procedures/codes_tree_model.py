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

from PyQt4 import QtGui, QtCore
HORIZONTAL_HEADERS = ("Codes",)
# see below

class TreeItem(object):
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    '''
    def __init__(self, proc_code, header, parentItem):
        self.proc_code = proc_code
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
        if self.proc_code == None:
            if column == 0:
                return self.header
        else:
            if column == 0:
                return u"%s (%s)"% (
                self.proc_code.description, self.proc_code.code)

            ## the rest of this is debug stuff for this very important
            ## data set

            elif column == 1:
                return "Y" if self.proc_code.further_info_needed else "N"
            elif column == 2:
                return "Y" if self.proc_code.is_chartable else "N"
            elif column == 3:
                return self.proc_code.material
            elif column == 4:
                return self.proc_code.crown_type
            elif column == 5:
                if self.proc_code.description_required:
                    return "Y"
            elif column == 6:
                if self.proc_code.tooth_required:
                    return "Y"
            elif column == 7:
                if self.proc_code.multi_tooth:
                    return "Y"
            elif column == 8:
                if self.proc_code.surfaces_required:
                    return self.proc_code.no_surfaces
            elif column == 9:
                if self.proc_code.pontics_required:
                    return "Y %s"% self.proc_code.no_pontics
            elif column == 10:
                return self.proc_code.total_span

        return QtCore.QVariant()

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

class ProcCodeTreeModel(QtCore.QAbstractItemModel):
    '''
    a model to display procedure codes
    '''
    def __init__(self, parent=None):
        super(ProcCodeTreeModel, self).__init__(parent)
        self.proc_codes = SETTINGS.PROCEDURE_CODES
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.setupModelData()

    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            #return 1
            return len(HORIZONTAL_HEADERS)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.UserRole:
            if item:
                return item.proc_code

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
        for proc_code in self.proc_codes:
            category = proc_code.category
            if not self.parents.has_key(category):
                newparent = TreeItem(None, category, self.rootItem)
                self.rootItem.appendChild(newparent)

                self.parents[category] = newparent

            parentItem = self.parents[category]
            newItem = TreeItem(proc_code, "", parentItem)
            parentItem.appendChild(newItem)

    def searchModel(self, code):
        '''
        get the modelIndex for a given code
        '''
        def searchNode(node):
            '''
            a function called recursively, looking at all nodes beneath node
            '''
            for child in node.childItems:
                if code == child.proc_code:
                    index = self.createIndex(child.row(), 0, child)
                    return index

                if child.childCount() > 0:
                    result = searchNode(child)
                    if result:
                        return result

        retarg = searchNode(self.parents[0])
        print retarg
        return retarg

    def find_code(self, code):
        found_code = None
        for proc_code in self.proc_codes:
            if proc_code.code == code:
                found_code = proc_code
                break
        if found_code != None:
            index = self.searchModel(found_code)
            return (True, index)
        return (False, None)

    def find_description(self, descr):
        found_code = None
        for proc_code in self.proc_codes:
            if proc_code.description.lower().find(descr.toLower()) != -1:
                found_code = proc_code
                break
        if found_code != None:
            index = self.searchModel(found_code)
            return (True, index)
        return (False, None)


class _TestDialog(QtGui.QDialog):
    def __init__(self, model, parent=None):
        super(_TestDialog, self).__init__(parent)

        self.tree_view = QtGui.QTreeView(self)
        self.tree_view.setModel(model)
        self.tree_view.setAlternatingRowColors(True)

        label = QtGui.QLabel("Search for the following code")

        frame = QtGui.QFrame(self)
        layout2 = QtGui.QHBoxLayout(frame)

        i = 0
        for proc_code in model.proc_codes:
            but = QtGui.QPushButton(proc_code.code, frame)
            layout2.addWidget(but)
            but.clicked.connect(self.but_clicked)
            i += 1
            if i == 10:
                 break


        but = QtGui.QPushButton("Clear Selection")
        but.clicked.connect(self.tree_view.clearSelection)

        self.tree_view.clicked.connect(self.row_clicked)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.tree_view)
        layout.addWidget(label)
        layout.addWidget(frame)
        layout.addWidget(but)

    def row_clicked(self, index):
        '''
        when a row is clicked... print the code
        '''
        print self.tree_view.model().data(index, QtCore.Qt.UserRole)

    def but_clicked(self):
        '''
        when a button is clicked, I iterate over the model,
        find the code, and set the treeviews current item
        '''
        code = self.sender().text()
        result, index = model.find_code(code)
        if result:
            if index:
                self.tree_view.setCurrentIndex(index)
                return
        tv.clearSelection()


if __name__ == "__main__":

    ## for this test code.. the model displays a lot more information
    ## to help put logic into the treatment codes

    from lib_openmolar import client
    HORIZONTAL_HEADERS = ("Codes", "NEEDS INFO?", "is chartable",
    "material","crown_type",
    "needs description?","needs a tooth?",
    "is multi tooth?", "needs surfaces?", "pontics?", "span")

    app = QtGui.QApplication([])

    model = ProcCodeTreeModel()
    dl = _TestDialog(model)
    dl.exec_()
