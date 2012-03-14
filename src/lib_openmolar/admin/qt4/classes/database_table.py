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

from xml.dom import minidom
import re
from PyQt4 import QtCore, QtGui, QtSql


from lib_openmolar.admin.qt4.classes import MyModel, MyRelationalModel
from lib_openmolar.admin.qt4.dialogs.new_db_row_dialog import NewRowDialog


class DatabaseTableViewer(QtGui.QWidget):
    connection = None
    name = _("Table Viewer")
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.table_list = QtGui.QListWidget(self)
        tool_bar = QtGui.QToolBar()

        icon = QtGui.QIcon.fromTheme("document-open")
        action_import = QtGui.QAction(icon, "import from xml", self)
        action_import.setToolTip(
            "import data into the current table from an xml file")


        icon = QtGui.QIcon.fromTheme("document-save")
        action_export = QtGui.QAction(icon, "export to xml", self)
        action_export.setToolTip(
            "export data from the current table to an xml file")

        action_new_row = QtGui.QAction("New Row", self)
        action_new_row.setToolTip(
            "add a row of data to the current table")


        tool_bar.addAction(action_new_row)
        tool_bar.addSeparator()
        tool_bar.addAction(action_import)
        tool_bar.addAction(action_export)


        self.table_view = QtGui.QTableView(self)

        #h_header = self.table_view.horizontalHeader()
        #h_header.setStretchLastSection(True)

        left_frame = QtGui.QFrame(self)
        layout = QtGui.QVBoxLayout(left_frame)
        layout.setMargin(0)
        layout.addWidget(self.table_list)
        layout.addWidget(tool_bar)

        splitter = QtGui.QSplitter(self)
        splitter.addWidget(left_frame)
        splitter.addWidget(self.table_view)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(splitter)
        splitter.setSizes([150,400])

        self.table_list.itemSelectionChanged.connect(self.load_data)

        action_new_row.triggered.connect(self.new_row)
        action_import.triggered.connect(self.import_data)
        action_export.triggered.connect(self.export_data)

    def set_connection(self, connection):
        self.connection = connection
        self.load_table_choice()
        self.setModel()

    def setModel(self):
        self.model = MyModel(self, self.connection)

    def load_table_choice(self):
        self.table_list.clear()
        if not self.connection:
            return
        tables = self.connection.get_available_tables()
        tables.sort()
        if tables:
            self.table_list.addItems(tables)
            self.table_list.setCurrentRow(-1)
        else:
            self.parent().parent().emit(QtCore.SIGNAL("Query Success"),
                _("No Tables"))

    def advise(self, message):
        QtGui.QMessageBox.warning(self, _("error"), message)

    def new_row(self, args):
        listwidget_item = self.table_list.currentItem()
        if not listwidget_item.isSelected():
            self.advise("no table chosen")
            return

        dl = NewRowDialog(self.model)
        if dl.exec_():
            record = dl.record
            if self.model.insertRecord(-1, record):
                self.advise(_("Successful insert"))
            else:
                self.advise(u"%s<hr /><pre>%s</pre>"% (_("error"),
                    self.model.lastError().text()))
                self.model.revert()


    def export_data(self, args):
        listwidget_item = self.table_list.currentItem()
        if not listwidget_item.isSelected():
            self.advise("no table chosen")
            return
        try:
            filepath = QtGui.QFileDialog.getSaveFileName(None,
            _("save xml"),"%s.xml"% self.model.tableName(),
            _("text files ")+"(*.xml)")
            if filepath != '':
                if not re.match(".*\.xml$", filepath):
                    filepath += ".xml"
                f = open(filepath, "w")
                f.write(self.model.table_xml())
                f.close()
        except Exception, e:
            self.advise(_("File not saved")+" - %s"% e)

    def import_data(self, args):
        '''
        import from xml
        '''
        listwidget_item = self.table_list.currentItem()
        if not listwidget_item.isSelected():
            self.advise("no table chosen")
            return
        filename = QtGui.QFileDialog.getOpenFileName(self,
        _("load an xml file"),"%s.xml"% self.model.tableName(),
        _("xml files")+" (*xml)")

        if filename != '':
            try:
                dom = minidom.parse(str(filename))
                if dom.getElementsByTagName("ix") != []:
                    new_keys = QtGui.QMessageBox.question(self, _("option"),
                    u"%s<hr />%s"% (
    _("would you like to try and preserve existing keys for this table"),
                    _("click 'no' to generate new serial keys")),
                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No) == QtGui.QMessageBox.No

                self.model.load_table_xml(dom, new_keys)
                self.load_data()
            except IOError, e:#Exception, e:
                self.advise(_("error parsing template file")+" - %s"% e)

    def load_data(self):
        listwidget_item = self.table_list.currentItem()
        if not listwidget_item.isSelected():
            return
        table = listwidget_item.text()
        app = QtGui.QApplication.instance()
        try:
            self.model.reset()
            app.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.model.setTable(table)
            self.model.select()
            self.table_view.setModel(self.model)

        except Exception as e:
            print e
        finally:
            app.restoreOverrideCursor()

        error = self.model.lastError()
        if error.isValid():
            self.emit(QtCore.SIGNAL("Query Error"), error.text())
        else:
            self.emit(QtCore.SIGNAL("Query Success"),
                u"%s '%s'"%(_("loaded table"),table))


class RelationalDatabaseTableViewer(DatabaseTableViewer):
    '''
    a custom class consisting of a list widget and a table view connected
    to a RelationalDatabase Model
    '''
    def __init__(self, parent=None):
        DatabaseTableViewer.__init__(self, parent)

    def setModel(self):
        '''
        a re-implemented method
        '''
        self.model = MyRelationalModel(self, self.connection)



def _test():
    from lib_openmolar.admin.connect import DemoAdminConnection
    def show_error(error):
        QtGui.QMessageBox.warning(mw, "error", error)

    app = QtGui.QApplication([])

    ac = DemoAdminConnection()
    ac.connect()

    mw = QtGui.QMainWindow()
    mw.setMinimumSize(400,400)

    label1 = QtGui.QLabel("table viewer")
    widg1 = DatabaseTableViewer(mw)
    widg1.set_connection(ac)
    widg1.load_table_choice()

    label2 = QtGui.QLabel("relational table viewer")
    widg2 = RelationalDatabaseTableViewer(mw)
    widg2.set_connection(ac)
    widg2.load_table_choice()

    frame = QtGui.QFrame()
    layout = QtGui.QVBoxLayout(frame)

    layout.addWidget(label1)
    layout.addWidget(widg1)
    layout.addWidget(label2)
    layout.addWidget(widg2)

    mw.setCentralWidget(frame)

    mw.connect(widg1, QtCore.SIGNAL("Query Error"), show_error)
    mw.connect(widg2, QtCore.SIGNAL("Query Error"), show_error)
    mw.show()

    app.exec_()


if __name__ == "__main__":
    import gettext
    gettext.install("")

    _test()

