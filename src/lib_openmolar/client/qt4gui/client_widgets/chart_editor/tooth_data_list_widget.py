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

class ToothDataListModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.items = []

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.items)

    def data(self, index, role):
        if index.isValid():
            item = self.items[index.row()]
            if role == QtCore.Qt.DisplayRole:
                return item.text
            #elif role == QtCore.Qt.ForegroundRole:
            #    return item.brush
            elif role == QtCore.Qt.DecorationRole:
                return item.icon

        return QtCore.QVariant()

    def add_item(self, item):
        self.beginResetModel()
        self.items.append(item)
        self.endResetModel()

    def clear(self):
        self.beginResetModel()
        self.items = []
        self.endResetModel()

    def setTooth(self, tooth):
        self.tooth = tooth
        self.setItems(tooth.properties)

    def setItems(self, items):
        self.beginResetModel()
        self.items = []
        for item in items:
            self.items.append(item)
        self.endResetModel()

class ToothDataListWidget(QtGui.QListView):
    def __init__(self, parent=None):
        QtGui.QListView.__init__(self, parent)
        self.setModel(ToothDataListModel())
        #self.setAlternatingRowColors(True)

    def sizeHint(self):
        return QtCore.QSize(200,80)

    def add_item(self, item):
        self.model().add_item(item)

    def clear(self):
        self.model().clear()

    def setTooth(self, tooth):
        self.model().setTooth(tooth)

if __name__ == "__main__":

    from lib_openmolar.client.qt4gui.client_widgets.chart_widgets.teeth \
        import ChartTooth
    from lib_openmolar.client.qt4gui.client_widgets.chart_widgets.tooth_data \
        import ToothData
    from lib_openmolar.client.qt4gui.client_widgets.chart_widgets.chart_data_model \
        import ChartDataModel

    app = QtGui.QApplication([])
    dl = QtGui.QDialog()

    obj = ToothDataListWidget()

    model = ChartDataModel()
    tooth = ChartTooth(1, model)

    prop = ToothData(1)
    prop.set_type(prop.FILLING)
    prop.from_fill_string("MOD,GL")
    tooth.add_property(prop)

    prop = ToothData(1)
    prop.set_type(prop.CROWN)
    prop.set_crown_type("LAVA")
    tooth.add_property(prop)

    prop = ToothData(1)
    prop.set_type(prop.ROOT)
    prop.set_root_type("IM")
    tooth.add_property(prop)

    prop = ToothData(1)
    prop.set_type(prop.COMMENT)
    prop.set_comment("I am a comment")
    tooth.add_property(prop)

    obj.setTooth(tooth)

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(obj)
    dl.exec_()
