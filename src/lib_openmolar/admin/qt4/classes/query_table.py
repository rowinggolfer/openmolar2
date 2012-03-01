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

import re
from PyQt4 import QtCore, QtGui, QtSql, Qsci
from lib_openmolar.common.qt4.dialogs import BaseDialog
from lib_openmolar.common.import_export import export_csv
from lib_openmolar.common.import_export import export_xls

class ManageHistoryDialog(BaseDialog):
    def __init__(self, history, parent=None):
        super(ManageHistoryDialog, self).__init__(parent)
        self.setMinimumWidth(500)
        self.setWindowTitle(_("Delete Items"))

        label = QtGui.QLabel(_("Select Items to delete from history"))
        label.setAlignment(QtCore.Qt.AlignCenter)

        checkbox = QtGui.QCheckBox(_("Check All"))
        checkbox.stateChanged.connect(self.check_all)

        self.list_widget = QtGui.QListWidget(self)
        self.list_widget.setWordWrap(True)
        self.list_widget.setAlternatingRowColors(True)
        for query in history:
            checkable_item = QtGui.QListWidgetItem(query)
            checkable_item.setCheckState(0)
            self.list_widget.addItem(checkable_item)

        self.layout.insertWidget(0, label)
        self.layout.insertWidget(1, checkbox)
        self.layout.insertWidget(2, self.list_widget)

        self.enableApply()

    def check_all(self, check_state):
        for i in xrange(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(check_state)

    @property
    def selected(self):
        selected = []
        for i in xrange(self.list_widget.count()):
            if self.list_widget.item(i).checkState() == 2:
                selected.append(i)
        return selected


class SqlQueryTable(QtGui.QWidget):
    pg_session = None
    name = _("SqlQuery Tool")
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.query_editor = Qsci.QsciScintilla()

        self.query_editor.setLexer(Qsci.QsciLexerSQL())
        self.query_editor.setCaretLineVisible(True)

        self.go_button = QtGui.QPushButton(_("Execute Query"), self)
        self.go_button.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_Return)

        icon = QtGui.QIcon.fromTheme('x-office-spreadsheet')
        self.action_export_xls = QtGui.QAction(icon,
            "Export to Excel Spreadsheet", self)
        self.action_export_csv = QtGui.QAction(icon, "Export to csv", self)

        self.action_export_xls.setEnabled(export_xls.AVAILABLE)

        menu = QtGui.QMenu(self)
        menu.addAction(self.action_export_xls)
        menu.addAction(self.action_export_csv)

        export_toolbutton = QtGui.QToolButton(self)
        export_toolbutton.setText(_("&Export"))
        export_toolbutton.setPopupMode(export_toolbutton.InstantPopup)
        export_toolbutton.setSizePolicy(QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)

        export_toolbutton.setMenu(menu)

        self.back_button = QtGui.QPushButton ("<", self)
        self.back_button.setMaximumWidth(40)
        self.back_button.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_Up)
        self.next_button = QtGui.QPushButton (">", self)
        self.next_button.setMaximumWidth(40)
        self.next_button.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_Down)

        self.clear_text_button = QtGui.QPushButton ("clear text", self)
        self.clear_text_button.setShortcut(
            QtCore.Qt.CTRL + QtCore.Qt.Key_Delete)

        self.hist_combobox_headers = [_("Query History"), _("Clear Items"),
            _("Clear All History")]

        self.hist_combobox = QtGui.QComboBox(self)
        self.hist_combobox.addItems(self.hist_combobox_headers)

        self.model = QtSql.QSqlQueryModel(self)
        table_view = QtGui.QTableView(self)
        table_view.setModel(self.model)


        top_frame = QtGui.QWidget(self)
        layout = QtGui.QHBoxLayout(top_frame)
        layout.setMargin(0)
        layout.addWidget(self.go_button)
        layout.addWidget(export_toolbutton)

        sub_frame = QtGui.QFrame(self)
        layout = QtGui.QHBoxLayout(sub_frame)
        layout.setMargin(0)
        layout.addWidget(self.back_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.clear_text_button)

        frame = QtGui.QFrame(self)
        frame.setMaximumWidth(200)
        layout = QtGui.QVBoxLayout(frame)
        layout.setMargin(0)
        layout.addWidget(top_frame)
        layout.addWidget(sub_frame)

        layout.addItem(QtGui.QSpacerItem(
            0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        layout.addWidget(self.hist_combobox)

        top_frame = QtGui.QFrame(self)
        layout = QtGui.QHBoxLayout(top_frame)
        layout.setMargin(0)
        layout.addWidget(self.query_editor)
        layout.addWidget(frame)

        splitter = QtGui.QSplitter(self)
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.addWidget(top_frame)
        splitter.addWidget(table_view)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(splitter)
        splitter.setSizes([50,400])

        self.query_editor.setFocus()

        self.history = QtCore.QStringList()
        self.get_history()
        self.history_position = -1

        self.connect_signals()

    def connect_signals(self):
        self.go_button.clicked.connect(self.execute)
        self.back_button.clicked.connect(self.load_previous_query)
        self.next_button.clicked.connect(self.load_next_query)
        self.clear_text_button.clicked.connect(self.clear_text)

        self.action_export_csv.triggered.connect(self.export_csv)
        self.action_export_xls.triggered.connect(self.export_xls)

        self.hist_combobox.currentIndexChanged.connect(self.hist_cb_manage)

    def set_connection(self, connection):
        self.pg_session = connection

    def get_history(self):
        settings = QtCore.QSettings()
        history = settings.value('query_table_history').toStringList()

        if not history:
            self.history = QtCore.QStringList()
            self.history_position = -1
            settings.setValue('query_table_history', self.history)

        if history != self.history:
            self.history = history
            self.update_cb()

    def update_cb(self):
        if len(self.history) != (self.hist_combobox.count() -
            len(self.hist_combobox_headers)):
            while self.hist_combobox.count() > len(self.hist_combobox_headers):
                self.hist_combobox.removeItem(self.hist_combobox.count()-1)
            for item in self.history:
                if len(item) > 80:
                    self.hist_combobox.addItem("%s ..."% item[:76])
                else:
                    self.hist_combobox.addItem(item)

    def set_history(self):
        settings = QtCore.QSettings()
        settings.setValue('query_table_history', self.history)
        self.update_cb()

    def add_history(self, query):
        self.get_history()
        if not query in self.history:
            self.history.append(query)
            self.history_position = self.history.indexOf(query)
        self.set_history()

    def execute(self):
        query = self.query_editor.text()
        self.add_history(query)

        q_query = QtSql.QSqlQuery(query, self.pg_session)

        self.model.setQuery(q_query)

        if self.model.lastError().isValid():
            error = self.model.lastError().text()
            self.emit(QtCore.SIGNAL("Query Error"), error)
        elif q_query.numRowsAffected() != -1:
            message = u"%s<hr />%d %s"% (_("Query Executed"),
            q_query.numRowsAffected(), _("rows affected"))
            self.emit(QtCore.SIGNAL("Query Success"), message)
        else:
            self.emit(QtCore.SIGNAL("Query Success"), _("Query Executed"))

    def _load_known(self):
        try:
            self.query_editor.setText(self.history[self.history_position])
        except IndexError:
            self.history_position = len(self.history)-1
            self.query_editor.setText("")

    def load_previous_query(self):
        self.get_history()

        self.history_position -= 1
        if self.history_position <0:
            self.history_position = len(self.history)-1
        self._load_known()

    def load_next_query(self):
        self.get_history()

        self.history_position += 1
        self._load_known()

    def clear_text(self):
        self.query_editor.setText("")

    def manage_history(self):
        self.get_history()
        dl = ManageHistoryDialog(self.history)
        if dl.exec_():
            for i in dl.selected:
                self.history.replace(i, "")
            self.history.removeAll("")
            self.set_history()

    def clear_history(self):
        if self.history and QtGui.QMessageBox.question(
        self, _("confirm"), _("clear history?"),
        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Ok) == QtGui.QMessageBox.Ok:
            self.history = QtCore.QStringList()
            self.history_position = -1
            self.set_history()
            self.get_history() # updates the combobox

    def hist_cb_manage(self, i):
        if i==0:
            return
        self.hist_combobox.setCurrentIndex(0)
        if i==1:
            self.manage_history()
        elif i==2:
            self.clear_history()
        else:
            self.history_position = i - len(self.hist_combobox_headers)
            self._load_known()
            self.execute()

    def export_csv(self, i):
        try:
            filepath = QtGui.QFileDialog.getSaveFileName(self,
            _("save as CSV (Comma Separated Values)"), "openmolar_export.csv",
            _("CSV files ")+"(*.csv)")
            if filepath != '':
                if not re.match(".*\.csv$", filepath):
                    filepath += ".csv"
                f = open(filepath, "w")
                writer = export_csv.CSV_Writer(f)
                writer.write_model(self.model)
                QtGui.QMessageBox.information(self, _("Success"),
                _("CSV file saved"))
            else:
                QtGui.QMessageBox.information(self, _("Abandoned"),
                _("CSV file NOT saved!"))
        except Exception, e:
            QtGui.QMessageBox.warning(self, _("ERROR"),
                (u"%s<hr />%s"% (_("Error Exporting to CSV"), e)))

    def export_xls(self, i):
        try:
            filepath = QtGui.QFileDialog.getSaveFileName(self,
            _("save as XLS (Excel Spreadsheet Format)"),
            "openmolar_export.xls",
            _("XLS files ")+"(*.xls)")
            if filepath != '':
                if not re.match(".*\.xls$", filepath):
                    filepath += ".xls"
                writer = export_xls.XLS_Writer(filepath)
                writer.write_model(self.model)
                QtGui.QMessageBox.information(self, _("Success"),
                _("XLS file saved"))
            else:
                QtGui.QMessageBox.information(self, _("Abandoned"),
                _("XLS file NOT saved!"))
        except Exception, e:
            QtGui.QMessageBox.warning(self, _("ERROR"),
                (u"%s<hr />%s"% (_("Error Exporting to Excel Format"), e)))


def _test():
    from lib_openmolar.admin.connect import DemoAdminConnection
    def show_error(error):
        QtGui.QMessageBox.warning(mw, "error", error)

    app = QtGui.QApplication([])

    ac = DemoAdminConnection()
    ac.connect()

    mw = QtGui.QMainWindow()
    mw.setMinimumSize(400,400)

    table = SqlQueryTable(mw)
    table.set_connection(ac)

    mw.setCentralWidget(table)

    mw.connect(table, QtCore.SIGNAL("Query Error"), show_error)
    mw.show()

    app.exec_()


if __name__ == "__main__":
    import gettext
    gettext.install("")

    _test()
