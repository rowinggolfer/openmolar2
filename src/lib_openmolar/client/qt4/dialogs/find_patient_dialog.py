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

from PyQt4 import QtCore, QtGui

from lib_openmolar.common.qt4.dialogs import BaseDialog, ExtendableDialog
from lib_openmolar.client.qt4.widgets import SoundexLineEdit

class FindPatientDialog(ExtendableDialog):
    def __init__(self, parent=None):
        super(FindPatientDialog, self).__init__(parent)

        self.setWindowTitle(_("Patient Finder"))

        label = QtGui.QLabel(_('Fill in a few of the following fields to get a list of matching patients'))
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.set_accept_button_text(_("Search Now"))

        self.sname_le = SoundexLineEdit(self)
        self.fname_le = SoundexLineEdit(self)
        self.dob_edit = QtGui.QDateEdit(self)
        self.dob_edit.setCalendarPopup(True)
        self.dob_edit.setDate(QtCore.QDate(1900,1,1))
        self.address_le = QtGui.QLineEdit(self)
        self.pcde_le = QtGui.QLineEdit(self)
        self.telephone_le = QtGui.QLineEdit(self)

        widget = QtGui.QWidget()
        form = QtGui.QFormLayout(widget)
        form.addRow(_("SNO or Surname"), self.sname_le)
        form.addRow(_("First Name"), self.fname_le)
        form.addRow(_("Date of Birth"), self.dob_edit)
        form.addRow(_("Address includes"), self.address_le)
        form.addRow(_("Post Code"), self.pcde_le)
        form.addRow(_("Telephone"), self.telephone_le)

        icon = QtGui.QIcon(":/icons/agt_reload.png")
        self.repeat_button = QtGui.QPushButton(icon,
            _("Load Last Search Values"), self)

        self.insertWidget(label)
        self.insertWidget(widget)

        #advanced options
        self.add_advanced_widget(self.repeat_button)

        self.enable_soundex_checkbox = QtGui.QCheckBox(
            _("enable 'sounds like' options"))
        self.add_advanced_widget(self.enable_soundex_checkbox)

        self._has_completers = False
        self._connect_signals()
        self.search_values = {}

    def sizeHint(self):
        return QtCore.QSize(350,320)

    def show_soundex(self, visible):
        self.sname_le.show_soundex(visible)
        self.fname_le.show_soundex(visible)

    def _connect_signals(self):
        self.sname_le.editingFinished.connect(self.fname_completer)

        self.sname_le.cursorPositionChanged.connect(self._check)
        self.fname_le.cursorPositionChanged.connect(self._check)
        self.address_le.cursorPositionChanged.connect(self._check)
        self.pcde_le.cursorPositionChanged.connect(self._check)
        self.telephone_le.cursorPositionChanged.connect(self._check)
        self.dob_edit.dateChanged.connect(self._check)

        self.repeat_button.clicked.connect(self.load_last_search)

        self.enable_soundex_checkbox.toggled.connect(self.show_soundex)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def reset_completers(self):
        '''
        called if the connection changes
        '''
        print "reseting completers"
        self._has_completers = False

    def populate_completers(self):
        self.sname_le.setCompleter(SETTINGS.psql_conn.sname_completer())
        self._has_completers = True
        self.connect (QtGui.QApplication.instance(),
            QtCore.SIGNAL("db_connected"), self.reset_completers)

    def fname_completer(self):
        sname = self.sname_le.text()
        if sname == "":
            self.fname_le.setCompleter(QtGui.QCompleter())
        else:
            self.fname_le.setCompleter(
                SETTINGS.psql_conn.fname_completer(sname))

    def _check(self, *args):
        enable = (self.sname_le.text() != "" or
            self.fname_le.text() != "" or
            self.dob_edit.date() != QtCore.QDate(1900,1,1) or
            self.address_le.text() != "" or
            self.pcde_le.text() != "" or
            self.telephone_le.text() != "")

        self.enableApply(enable)
        self.repeat_button.setVisible(self.search_values != {})

    def exec_(self):
        self.clear()
        if not self._has_completers:
            self.populate_completers()

        return BaseDialog.exec_(self)

    def clear(self):
        for le in (self.sname_le, self.fname_le, self.address_le,
        self.pcde_le, self.telephone_le):
            le.setText("")
        self.dob_edit.setDate(QtCore.QDate(1900,1,1))
        self.sname_le.setChecked(False)
        self.fname_le.setChecked(False)

        self.sname_le.setFocus()
        self._check()

    def apply(self):
        self._analyse()

    def _emit_result(self, val):
        self.emit(QtCore.SIGNAL("Load Serial Number"), val)

    def _analyse(self):
        self.search_values["dob"] = self.dob_edit.date()
        self.search_values["addr"] = self.address_le.text()
        self.search_values["tel"] = self.telephone_le.text()
        sname = self.sname_le.text()
        self.search_values["sname"] = sname
        self.search_values["fname"] = self.fname_le.text()
        self.search_values["pcde"] = self.pcde_le.text()
        self.search_values["soundex_sname"] = self.sname_le.isChecked()
        self.search_values["soundex_fname"] = self.fname_le.isChecked()

        patient_id, result = sname.toInt()
        if result and patient_id > 0:
            self._emit_result(patient_id)
        else:
            matches = SETTINGS.psql_conn.get_matchlist(self.search_values)

            if matches == []:
                self.Advise(_("no match found"), 1)
            else:
                if len(matches) > 1:
                    sno = self.final_choice(matches)
                    if sno != None:
                        self._emit_result(sno)
                else:
                    self._emit_result(matches[0].patient_id)

    def final_choice(self, matches):
        dl = FinalSelectionDialog(matches, self.parent())
        return dl.chosen_id

    def load_last_search(self):
        self.sname_le.setText(self.search_values.get("sname",""))
        self.fname_le.setText(self.search_values.get("fname",""))
        self.dob_edit.setDate(self.search_values.get(
            "dob", QtCore.QDate(1900,1,1)))
        self.address_le.setText(self.search_values.get("addr",""))
        self.pcde_le.setText(self.search_values.get("pcde",""))
        self.telephone_le.setText(self.search_values.get("tel",""))
        self.sname_le.setChecked(self.search_values.get("soundex_sname", False))
        self.fname_le.setChecked(self.search_values.get("soundex_fname", False))

class FinalSelectionModel(QtCore.QAbstractTableModel):
    def __init__(self, selection_of_patients, parent=None):
        super(FinalSelectionModel, self).__init__(parent)
        self.patients = selection_of_patients
        self.headers = (_("Serial No"), _("Name"), _("Date of Birth"),
        _("Address Line 1"),_("Address Line 2"), _("Postal Code"),
        _("Telephone"))

    def rowCount(self, index=None):
        return len(self.patients)

    def columnCount(self, index=None):
        return len(self.headers)

    def headerData(self, item, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self.headers[item]
        return QtCore.QVariant()

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            patient = self.patients[index.row()]
            col = index.column()
            if col == 0:
                return patient.patient_id
            if col == 1:
                return patient.full_name
            if col == 2:
                return patient.dob
            if col == 3:
                return patient.addr1
            if col == 4:
                return patient.addr2
            if col == 5:
                return patient.pcde
            if col == 6:
                return patient.number

        elif role == QtCore.Qt.FontRole:
            if index.column() == 1:
                font = QtGui.QApplication.instance().font()
                font.setBold(True)
                return QtCore.QVariant(font)

        return QtCore.QVariant()

class FinalSelectionDialog(BaseDialog):
    def __init__(self, selection_of_patients, parent=None):
        super(FinalSelectionDialog, self).__init__(parent)

        self.patients = selection_of_patients
        self.model = FinalSelectionModel(self.patients, self)

        self.setWindowTitle(_("Final Selection"))
        self.top_label = QtGui.QLabel(
        _("Multiple Matches Found, please choose from the following"))
        self.top_label.setAlignment(QtCore.Qt.AlignCenter)

        self.table_view = QtGui.QTableView(self)
        self.table_view.setModel(self.model)

        self.table_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table_view.setWordWrap(True)
        self.table_view.resizeColumnsToContents()
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.layout.removeItem(self.spacer)
        self.table_view.setSizePolicy(
            QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding))

        self.layout.insertWidget(0, self.top_label)
        self.layout.insertWidget(1, self.table_view)

        try:
            width = parent.width()
            width = width*.9
            if width > 800:
                width = 800
            self.setMinimumWidth(width)
        except AttributeError:
            self.setMinimumWidth(600)
        self.table_view.selectionModel().currentChanged.connect(self._enable)
        self.table_view.doubleClicked.connect(self._accept)
        self.table_view.selectRow(0)
        self.table_view.setFocus()

        self.set_accept_button_text(_("Load Selected Record"))

    def sizeHint(self):
        return QtCore.QSize(800,300)

    def _enable(self, *args):
        self.enableApply()

    def _accept(self, *args):
        self.accept()

    @property
    def chosen_id(self):
        if self.exec_():
            selected = self.table_view.currentIndex().row()
            return self.patients[selected].patient_id


if __name__ == "__main__":

    def sig_catcher(*args):
        print args

    app = QtGui.QApplication([])

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    dl = FindPatientDialog()
    QtCore.QTimer.singleShot(1000, dl.populate_completers)

    dl.connect(dl, QtCore.SIGNAL("Serial Number"), sig_catcher)
    if dl.exec_():
        dl.apply()
