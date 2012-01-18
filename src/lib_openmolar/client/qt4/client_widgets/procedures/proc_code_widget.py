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
from lib_openmolar.client.qt4.client_widgets.procedures.codes_tree_model \
    import ProcCodeTreeModel

class ProcCodeWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.model = ProcCodeTreeModel()

        self.tree_view = QtGui.QTreeView(self)
        self.tree_view.setIndentation(15)  #reduce default of 20
        self.tree_view.setModel(self.model)

        find_icon = QtGui.QIcon(':icons/search.png')

        self.search_line_edit = QtGui.QLineEdit()
        self.search_but = QtGui.QPushButton(find_icon,"")
        self.search_but.setMaximumWidth(40)

        search_frame = QtGui.QFrame()
        layout = QtGui.QHBoxLayout(search_frame)
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.addWidget(self.search_line_edit)
        layout.addWidget(self.search_but)

        layout = QtGui.QVBoxLayout(self)
        layout.setMargin(3)
        layout.addWidget(self.tree_view)
        layout.addWidget(search_frame)

        self.tree_view.doubleClicked.connect(self.item_double_clicked)
        self.search_line_edit.returnPressed.connect(self.search_but.click)
        self.search_but.clicked.connect(self.search_items)

    def sizeHint(self):
        return QtCore.QSize(120, 300)

    def item_double_clicked(self, index):
        item = self.model.data(index, QtCore.Qt.UserRole)
        if item:
            self.parent().emit(QtCore.SIGNAL("Code Selected"), item)

    def search_items(self):
        search_field = self.search_line_edit.text()
        result, index = self.model.find_description(search_field)
        if result:
            self.tree_view.setCurrentIndex(index)
        else:
            QtGui.QMessageBox.information(self, _("results"),
                "'%s' %s"% (search_field, _("not found")))


class DockWidgetTitleWidget(QtGui.QWidget):
    '''
    experimental code...
    I WILL need this to be a custom widget.. but it is not trivial
    so not yet!
    '''
    def __init__(self, parent):
        '''
        parent MUST be a QDockWidget
        '''
        super(DockWidgetTitleWidget, self).__init__(parent)
        self.setMouseTracking(True)
        self.dock_widget = parent
        self.add_child_widgets()

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self.is_vertical:
            return QtCore.QSize(20, 120)
        else:
            return QtCore.QSize(120, 20)

    def resizeEvent(self, event):
        self.add_child_widgets

    def mouseMoveEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        event.ignore()

    def mouseDoubleClickEvent(self, event):
        event.ignore()

    def add_child_widgets(self):
        self.is_vertical =  (self.dock_widget.features() &
            self.dock_widget.DockWidgetVerticalTitleBar)


class ProcCodeDockWidget(QtGui.QDockWidget):
    def __init__(self, parent=None):
        QtGui.QDockWidget.__init__(self, _("Fees"), parent)

        ## the following lines add the custom title bar.

        #super(ProcCodeDockWidget, self).__init__(parent)

        #widg = DockWidgetTitleWidget(self)
        #self.setTitleBarWidget(widg)

        self.setObjectName("ProcCodeDockWidget")

        self.widget = ProcCodeWidget(self)
        self.setWidget(self.widget)

if __name__ == "__main__":
    def sig_catcher(arg):
        print arg




    

    app = QtGui.QApplication([])

    obj = ProcCodeDockWidget()
    obj.show()

    obj.connect(obj, QtCore.SIGNAL("Code Selected"), sig_catcher)

    app.exec_()
