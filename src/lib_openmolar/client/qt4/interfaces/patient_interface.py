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

import sys, traceback
from PyQt4 import QtCore, QtGui

from lib_openmolar.client.qt4 import client_widgets

from lib_openmolar.client.qt4.client_widgets.procedures.proc_code_widget \
    import ProcCodeDockWidget

from lib_openmolar.client.qt4 import pages

from lib_openmolar.client.qt4 import dialogs

from lib_openmolar.client import db_orm

class PatientInterface(QtGui.QWidget):
    '''
    PatientInterface
    A composite widget containing all elements for viewing a patient record
    '''
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self._proc_code_dock_widget = None #initialise if needed.

        self.control_panel = client_widgets.ControlPanel(self)
        '''a pointer to the :doc:`ControlPanel`'''

        self.details_browser = client_widgets.DetailsBrowser(self)
        '''a pointer to the :doc:`DetailsBrowser`'''

        self.reception_page = pages.ReceptionPage(self)
        '''a pointer to the :doc:`ReceptionPage`'''

        self.charts_page = pages.ChartsPage(self)
        '''a pointer to the :doc:`ChartsPage`'''

        self.treatment_page = pages.TreatmentPage(self)
        '''a pointer to the :doc:`TreatmentPage`'''

        self.notes_page = client_widgets.NotesWidget(self)
        '''a pointer to the :doc:`NotesWidget`'''

        self.estimates_page = pages.EstimatesPage(self)
        '''a pointer to the :doc:`EstimatesPage`'''

        self.history_page = pages.HistoryPage(self)
        '''a pointer to the :doc:`HistoryPage`'''

        # summary_page shares the "model" of the static chart
        model = self.charts_page.static.chart_data_model
        self.summary_page = pages.SummaryPage(model, self)
        '''a pointer to the :doc:`SummaryPage`'''

        self.options_widget = client_widgets.PatientInterfaceOptionsWidget(self)
        '''a pointer to the :doc:`PatientInterfaceOptionsWidget`'''

        self.options_widget.tab_index_changed(0)

        self.tab_widget = QtGui.QTabWidget(self)
        '''a pointer to the TabWidget'''
        self.tab_widget.tabBar().setFocusPolicy(QtCore.Qt.NoFocus)
        self.tab_widget.addTab(self.reception_page, _("Reception"))
        self.tab_widget.addTab(self.summary_page, _("Summary"))
        self.tab_widget.addTab(self.charts_page, _("Charts"))
        self.tab_widget.addTab(self.treatment_page, _("Treatment"))
        self.tab_widget.addTab(self.estimates_page, _("Estimates"))
        self.tab_widget.addTab(self.notes_page, _("Notes"))
        self.tab_widget.addTab(self.history_page, _("History"))
        self.tab_widget.setCornerWidget(self.options_widget)

        left_widget = QtGui.QWidget()
        left_widget.setMaximumWidth(240)
        layout = QtGui.QVBoxLayout(left_widget)
        layout.setMargin(0)
        layout.addWidget(self.control_panel)
        layout.addWidget(self.details_browser)

        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(left_widget)
        layout.addWidget(self.tab_widget)

        ## keep this dialog everpresent..
        ## it can then keep a record of previous searches etc...
        self._find_dialog = None

        self.load_history, self.history_pos = [], -1
        self.pt = None
        #self.clear()
        self.connect_signals()

    @property
    def is_dirty(self):
        return self.ok_to_leave_record

    @property
    def find_dialog(self):
        if self._find_dialog is None:
            self._find_dialog = dialogs.FindPatientDialog(self)
        return self._find_dialog

    def connect_signals(self):

        app = QtGui.QApplication.instance()

        self.connect(self.control_panel,
            QtCore.SIGNAL('New Patient'), self.new_patient)
        self.connect(self.control_panel,
            QtCore.SIGNAL('Next Patient'), self.next_patient)
        self.connect(self.control_panel,
            QtCore.SIGNAL('Last Patient'), self.last_patient)
        self.connect(self.control_panel,
            QtCore.SIGNAL('Related Patients'), self.related_patient)
        self.connect(self.control_panel,
            QtCore.SIGNAL('Find Patient'), self.find_patient)
        self.connect(self.control_panel,
            QtCore.SIGNAL('Home'), self.go_home)
        self.connect(self.control_panel,
            QtCore.SIGNAL('Reload Patient'), self.reload_patient)

        self.connect(self.find_dialog, QtCore.SIGNAL("Advise"), self.Advise)
        self.connect(self.find_dialog, QtCore.SIGNAL("Load Serial Number"),
            self.load_patient)

        self.connect(self.treatment_page, QtCore.SIGNAL("Advise"), self.Advise)
        self.connect(self.summary_page, QtCore.SIGNAL("Advise"), self.Advise)

        self.connect(app, QtCore.SIGNAL("proc code selected"),
            self.treatment_page.proc_code_selected)

        self.connect(app, QtCore.SIGNAL("treatment item generated"),
            self.treatment_page.add_treatment_item)

        self.connect(self.details_browser,
            QtCore.SIGNAL("Edit Patient Details"), self.edit_patient)
        self.connect(self.details_browser,
            QtCore.SIGNAL("Edit Patient Address"), self.edit_address)
        self.connect(self.details_browser,
            QtCore.SIGNAL("Edit Patient Phone"), self.edit_phone)

        #self.connect(self.reception_page, QtCore.SIGNAL("db notify"),
        #    SETTINGS.psql_conn.emit_notification)

        self.connect(self.summary_page.summary_chart,
            QtCore.SIGNAL("key_press"),
            self.charts_page.tooth_data_editor.keyPressEvent)

        self.connect(self.summary_page.summary_chart,
            QtCore.SIGNAL("current tooth changed"),
            self.charts_page.sync_static)

        self.connect(self.charts_page.static,
            QtCore.SIGNAL("current tooth changed"),
            self.summary_page.sync_static)

        self.connect(self.charts_page,
            QtCore.SIGNAL("clear summary chart selection"),
            self.summary_page.clear_static)

        self.connect(self.summary_page.summary_chart, QtCore.SIGNAL("Focused"),
            self.charts_page.tooth_data_editor.set_mode)

        self.connect(self.charts_page, QtCore.SIGNAL("teeth present changed"),
            self.summary_page.summary_chart.set_known_teeth)

        self.connect(self.charts_page, QtCore.SIGNAL("add treatment"),
            self.treatment_page.chart_treatment_added)

        self.connect(self.treatment_page, QtCore.SIGNAL("garbage chart tx"),
            self.charts_page.tooth_data_editor.invalid_input)

        self.connect(self.treatment_page, QtCore.SIGNAL("valid chart tx"),
            self.charts_page.tooth_data_editor.valid_input)

        self.connect(self.summary_page.summary_chart,
            QtCore.SIGNAL("teeth present changed"),
            self.charts_page.known_teeth_changed)

        self.connect(self.charts_page,
            QtCore.SIGNAL("update patient teeth present"),
            self.update_patient_teeth_present)

        for page in (self.charts_page, self.treatment_page, self.summary_page):
            self.connect(page, QtCore.SIGNAL("Show Fee Widget"),
                self.call_fee_widget)

        self.connect(self.summary_page, QtCore.SIGNAL("clinical_memo_changed"),
            self.update_patient_memo_clinical)

        self.connect(self.details_browser,
            QtCore.SIGNAL("Edit clerical memo"),
            self.update_patient_memo_clerical)

        self.tab_widget.currentChanged.connect(self.tab_index_changed)

        self.connect(self.options_widget,
            QtCore.SIGNAL("chart style"), self.set_chart_style)

        self.connect(self.summary_page.bpe_widget,
            QtCore.SIGNAL("New BPE"), self.new_bpe)

        self.connect(self.summary_page.bpe_widget,
            QtCore.SIGNAL("Show BPE"), self.list_bpes)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def clear(self):
        '''
        clears all displayed information by iterating over child widgets
        and calling their clear functions
        '''
        self.details_browser.clear()
        self.apply_mode()

        for i in range(self.tab_widget.count()):
            self.tab_widget.widget(i).clear()
        ## not sure why I have to call these again??
        self.summary_page.clear()
        self.options_widget.clear()
        self.notes_page.clear()

        self.pt = None
        self.emit(QtCore.SIGNAL("Patient Loaded"), None)

    def apply_mode(self):
        '''
        applies the chosen "mode" which can be either a surgery machine or
        reception machine
        '''
        mode = SETTINGS.PERSISTANT_SETTINGS.get("mode", 0)
        self.tab_widget.setCurrentIndex(mode)
        self.options_widget.tab_index_changed(mode)

    def tab_index_changed(self, i):
        self.options_widget.tab_index_changed(i)
        page = self.tab_widget.widget(i)
        if page == self.notes_page:
            self.notes_page.load_patient()
        elif page == self.treatment_page:
            self.treatment_page.load_patient()
        elif page == self.history_page:
            self.history_page.load_patient()

    def edit_patient(self):
        '''
        functionality for editing parameters stored in the patients table
        for the loaded patient
        '''
        pt = self.pt['patient']
        dl = dialogs.EditPatientDialog(pt, self)
        if dl.exec_():
            dl.apply()
            if pt.is_dirty:
                if pt.commit_changes():
                    self.refresh_patient()

    def edit_address(self, index):
        '''
        functionality for editing and adding address information
        for the loaded patient
        '''
        address_db = self.pt['addresses']
        dl = dialogs.AddressDialog(address_db, index, self)
        refresh_needed = False
        if dl.exec_():
            self.Advise("update addresses!")
            self.refresh_patient()
        else:
            self.Advise("addresses unchanged!")

    def edit_phone(self):
        self.Advise("edit phone numbers")

    def call_fee_widget(self):
        if self._proc_code_dock_widget is not None:
            state =  self.proc_code_dock_widget.isVisible()
            self.proc_code_dock_widget.setVisible(not state)
            return

        self.emit(QtCore.SIGNAL("Show Fee Widget"), self.proc_code_dock_widget)

    @property
    def proc_code_dock_widget(self):
        if self._proc_code_dock_widget is None:
            self._proc_code_dock_widget = ProcCodeDockWidget(self)
            self.connect(self._proc_code_dock_widget,
                QtCore.SIGNAL("Code Selected"),
                self.treatment_page.proc_code_selected)
        return self._proc_code_dock_widget

    def update_patient_teeth_present(self, key):
        if not self.pt:
            return
        self.pt.set_dent_key(key)

    def update_patient_memo_clinical(self, memo):
        if not self.pt:
            return
        self.pt["memo_clinical"].setValue("memo", memo)

    def update_patient_memo_clerical(self):
        if not self.pt:
            return
        dl = QtGui.QInputDialog(self)
        dl.setWindowTitle(_("Edit Memo"))
        dl.setLabelText(_("Edit Memo"))
        dl.setTextValue(self.pt.clerical_memo)
        dl.resize(QtCore.QSize(400,200))
        if dl.exec_():
            self.pt["memo_clerical"].setValue("memo", dl.textValue())
            self.details_browser.setHtml(self.pt.details_html())

    def set_chart_style(self, enum):
        for chart in (
            self.summary_page.summary_chart,
            self.charts_page.static,
            self.charts_page.treatment,
            self.charts_page.completed):
            chart.setStyle(enum)

    def new_bpe(self):
        '''
        raises a dialog and creates a new bpe record for the current patient
        '''
        if not self.pt:
            return
        dl = dialogs.NewBpeDialog(self)
        if dl.exec_():
            self.pt.refresh_bpe()
            self.summary_page.bpe_widget.set_values(self.pt.current_bpe)

    def list_bpes(self):
        '''
        raises a dialog showing all bpes for the current patient
        '''
        dl = dialogs.ListBpeDialog(self)
        dl.exec_()

    def new_patient(self):
        '''
        raises a dialog and creates a new patient record in the database
        '''
        dl = dialogs.NewPatientDialog(self)
        self.connect(dl, QtCore.SIGNAL("Advise"), self.Advise)
        self.connect(dl, QtCore.SIGNAL("Load Serial Number"),
                self.load_patient)
        dl.exec_()

    def next_patient(self):
        '''
        cycle forwards through the list of recently visited records
        '''
        self.history_pos += 1
        try:
            self.load_patient(self.load_history[self.history_pos], True)
        except IndexError:
            self.history_pos = len(self.load_history) - 1
            self.Advise(_("Reached end of the List"))

    def last_patient(self):
        '''
        cycle backwards through recently visited records
        '''
        self.history_pos -= 1
        try:
            self.load_patient(self.load_history[self.history_pos], True)
        except IndexError:
            self.history_pos = 0
            self.Advise(_("Reached Start of the List"))

    def related_patient(self):
        self.Advise("related patient")

    def find_patient(self):
        '''
        raise a dialog which allows for patient search
        I keep a pointer to this dialog at all times
        (ie,it is not garbage collected)
        when the dialog wants a patient loaded it communicates via a signal
        '''
        if self.find_dialog.exec_():
            self.find_dialog.apply()

    def go_home(self):
        '''
        user has called for a clearing of the current record
        '''
        if not self.ok_to_leave_record:
            return

        self.clear()

    def reload_patient(self):
        '''
        reload from the database (has record been altered by another terminal?)
        '''
        if self.pt:
            self.load_patient(self.pt.patient_id, True)

    def refresh_patient(self):
        '''
        refresh after internal (possibly non-committed) changes
        '''
        if self.pt:
            self._load_patient()

    def _load_patient(self):
        '''
        updates the ui after a pt load from db, or a dialog box change
        '''
        SETTINGS.set_current_patient(self.pt)
        self.details_browser.setHtml(self.pt.details_html())
        self.options_widget.clear()
        self.history_page.clear()
        self.estimates_page.clear()
        for page in (
            self.reception_page,
            self.summary_page,
            self.charts_page,
            self.treatment_page,
            ):
                page.load_patient()

        self.summary_page.summary_chart.chart_data_model.endResetModel()
        self.pt.treatment_model.update_views()
        self.apply_mode()

    def load_patient(self, patient_id, called_via_history = False):
        '''
        load patient with id patient_id
        if optional 2nd arg is passed, this means don't alter the history list
        '''
        if not self.ok_to_leave_record:
            return
        self.clear()

        self.Advise(u"%s<br />%d"% (_("Loading Record Number"), patient_id))
        QtGui.QApplication.instance().setOverrideCursor(QtCore.Qt.WaitCursor)

        if __name__ == "__main__":
            exception_ = db_orm.PatientNotFoundError
        else:
            exception_ = Exception

        try:
            self.pt = db_orm.PatientModel(patient_id)
            self._load_patient()
            self.emit(QtCore.SIGNAL("Patient Loaded"), self.pt)
            if not called_via_history:
                self.load_history.append(patient_id)
                self.history_pos = len(self.load_history) - 1
        except db_orm.PatientNotFoundError:
            self.Advise(
            u"%s %d %s"% (_("Record"), patient_id, _("not found!")), 1)
        except exception_ as e:
            QtGui.QApplication.instance().restoreOverrideCursor()
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()

            readable_ex =   traceback.format_exception(
                exceptionType, exceptionValue, exceptionTraceback)

            message = u"%s\n\n"% _("Unhandled exception - please file a bug")

            for line in readable_ex:
                message += "%s\n" % line
            self.Advise(message, 2)


        QtGui.QApplication.instance().restoreOverrideCursor()

    @property
    def ok_to_leave_record(self):
        if self.pt is None:
            return True
        self.update_patient()
        if self.pt.is_dirty:
            if not self.save_patient(True):
                return False
        return True

    def update_patient(self):
        '''
        applies any changes from the underlying pages into the db ORM
        '''
        self.charts_page.update_patient()

    def save_patient(self, closing=False):
        if self.pt is None:
            return
        self.update_patient()
        if self.pt.is_dirty:
            message = "You have unsaved changes to record %s"% (
                self.pt.patient_id)

            dl = dialogs.SaveDiscardCancelDialog(message,
                self.pt.what_has_changed, self)
            dl.discard_but.setVisible(closing)
            if dl.exec_():
                if dl.save_on_exit:
                    self.pt.commit_changes()
                return True
            else:
                return False
        else:
            self.Advise(_("No changes Found"))

if __name__ == "__main__":
    def _test_dock_widget(dw):
        dw.show()
        dw.setFloating(True)

    from lib_openmolar.common.qt4.widgets import RestorableApplication

    app = RestorableApplication("openmolar-client")
    dl = QtGui.QDialog()
    dl.setMinimumSize(500,300)

    from lib_openmolar.client.connect import ClientConnection

    cc = ClientConnection()

    SETTINGS.PLUGIN_DIRS = QtCore.QSettings().value("plugin_dirs").toStringList()
    SETTINGS.PERSISTANT_SETTINGS = {"compile_plugins":True}
    SETTINGS.load_plugins()

    pi = PatientInterface(dl)

    cc.connect()
    pi.load_patient(1)

    layout = QtGui.QVBoxLayout(dl)
    layout.setMargin(0)
    layout.addWidget(pi)

    dl.connect(pi, QtCore.SIGNAL("Show Fee Widget"), _test_dock_widget)

    dl.exec_()
