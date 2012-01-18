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

from lib_openmolar.client.qt4.dialogs import TreatmentItemFinaliseDialog

from lib_openmolar.common import common_db_orm

class TreatmentPage(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.patient = None

        self.label = QtGui.QLabel()
        self.label.setWordWrap(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.tree_view = QtGui.QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setModel(SETTINGS.treatment_model.tree_model)

        self.show_fee_widget_button = QtGui.QPushButton(_("Procedure Codes"))

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.tree_view)
        layout.addWidget(self.show_fee_widget_button)

        self.treatment_item_finalise_dialog = TreatmentItemFinaliseDialog(self)

        self.clear()
        self.connect_signals()

    def sizeHint(self):
        return QtCore.QSize(400,400)

    def minimumSizeHint(self):
        return QtCore.QSize(300,300)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def connect_signals(self, connect=True):
        self.show_fee_widget_button.clicked.connect(self._call_fee_widget)

        self.tree_view.clicked.connect(self.treatment_item_selected)

    def _call_fee_widget(self):
        '''
        the "procedure codes" button has been pressed, emit a signal
        '''
        self.emit(QtCore.SIGNAL("Show Fee Widget"))

    def treatment_item_selected(self, index):
        item = self.tree_view.model().data(index, QtCore.Qt.UserRole)

        if not item:
            return

        action1 = QtGui.QAction(_("&Complete"), self)
        action2 = QtGui.QAction(_("&Undo"), self)
        action3 = QtGui.QAction(_("&Delete"), self)

        menu = QtGui.QMenu(self)
        if not item.is_completed:
            menu.addAction(action1)
        else:
            menu.addAction(action2)
        menu.addAction(action3)
        menu.addSeparator()
        menu.addAction(_("Cancel"))

        pos = self.tree_view.visualRect(index).bottomRight()
        result = menu.exec_(self.tree_view.mapToGlobal(pos))

        if not result:
            return
        if result == action1:
            self.complete_treatment_item(item)
        elif result == action2:
            self.complete_treatment_item(item, completed=False)
        elif result == action3:
            self.remove_treatment_item(item)

    def add_treatment_item(self, treatment_item):
        '''
        adds a treatment item
        '''
        patient = SETTINGS.current_patient
        if patient is None:
            self.Advise(_("No Patient Loaded"))
            return

        if treatment_item.is_completed:
            treatment_item.set_cmp_date()
            if SETTINGS.current_practitioner:
                treatment_item.set_tx_clinician(
                    SETTINGS.current_practitioner.id)

        while not patient.treatment_model.add_treatment_item(
                                        treatment_item):
            dl = self.treatment_item_finalise_dialog
            dl.set_known_teeth(patient.dent_key)
            if not dl.get_info(treatment_item):
                return

        self.expand_all()

        self.Advise(u"%s %s"%(_("added to treatment plan"),
            treatment_item.description))

    def remove_treatment_item(self, treatment_item):
        '''
        removes a treatment item
        '''
        patient = SETTINGS.current_patient
        if patient is None:
            self.Advise(_("No Patient Loaded"))
            return

        patient.treatment_model.remove_treatment_item(treatment_item)

        self.expand_all()

    def complete_treatment_item(self, treatment_item, completed=True):
        '''
        completes a treatment item
        '''
        patient = SETTINGS.current_patient
        if patient is None:
            self.Advise(_("No Patient Loaded"))
            return

        while not patient.treatment_model.complete_treatment_item(
            treatment_item, completed):

            dl = self.treatment_item_finalise_dialog
            if self.patient:
                dl.set_known_teeth(self.patient.dent_key)
            if not dl.get_info(treatment_item, completing=True):
                return

        self.expand_all()

    def proc_code_selected(self, proc_code):
        '''
        a raw procedure code has been selected
        (from the :doc:`ProcCodeWidget`)
        convert to a :doc:`TreatmentItem`, validate and pass to
        :func:`add_treatment_item`
        '''
        treatment_item = common_db_orm.TreatmentItem(proc_code)

        self.add_treatment_item(treatment_item)

    def chart_treatment_added(self, tooth_data, plan_or_cmp):
        '''
        treatment has been added using the charts page
        if this is not understood, the following signal is emitted
        QtCore.SIGNAL("garbage chart tx")
        '''
        proc_code = tooth_data.proc_code
        if proc_code == None:
            proc_code = SETTINGS.PROCEDURE_CODES.convert_user_shortcut(
                tooth_data.tx_input)
        if proc_code == None:
            self.emit(QtCore.SIGNAL("garbage chart tx"))
            return
        treatment_item = common_db_orm.TreatmentItem(proc_code)
        treatment_item.set_teeth([tooth_data.tooth_id])
        treatment_item.set_surfaces(tooth_data.surfaces)
        if plan_or_cmp == "Completed":
            treatment_item.set_completed(True)
            treatment_item.set_cmp_date(QtCore.QDate.currentDate())
        self.add_treatment_item(treatment_item)

        self.emit(QtCore.SIGNAL("valid chart tx"))

    def clear(self):
        self.patient = None
        self.label.setText("no patient loaded")
        SETTINGS.treatment_model.clear()

    def load_patient(self):
        patient = SETTINGS.current_patient
        self.patient = patient
        if patient:
            self.label.setText(u"Treatments for %s"% patient.full_name)
        else:
            self.clear()

        self.expand_all()

    def expand_all(self):
        patient = SETTINGS.current_patient
        if patient:
            self.tree_view.expandAll()
            for i in range(patient.treatment_model.tree_model.columnCount()):
                self.tree_view.resizeColumnToContents(i)

class _TestDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(_TestDialog, self).__init__(parent)
        self.proc_code_dock_widget = None

        self.page = TreatmentPage(self)

        toolbar = QtGui.QToolBar(self)

        test_all = QtGui.QAction("Add all txs", self)
        test_all.triggered.connect(self.test_all)

        toolbar.addAction(test_all)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.page)
        layout.addWidget(toolbar)
        self.connect_signals()

        self.page.load_patient()

    def connect_signals(self):
        self.connect(self.page, QtCore.SIGNAL("Show Fee Widget"),
            self.call_fee_widget)

    def call_fee_widget(self):
        if self.proc_code_dock_widget != None:
            state =  self.proc_code_dock_widget.isVisible()
            self.proc_code_dock_widget.setVisible(not state)
            return

        from lib_openmolar.client.qt4.client_widgets.procedures.proc_code_widget \
            import ProcCodeDockWidget

        self.proc_code_dock_widget = ProcCodeDockWidget(self)
        self.connect(self.proc_code_dock_widget,
            QtCore.SIGNAL("Code Selected"), self.page.proc_code_selected)

        self.proc_code_dock_widget.show()
        self.proc_code_dock_widget.setFloating(True)

    def test_all(self):
        '''
        iterate over the procedure codes, and show them all
        '''
        for code in SETTINGS.PROCEDURE_CODES:
            self.page.proc_code_selected(code)

if __name__ == "__main__":

    app = QtGui.QApplication([])
    from lib_openmolar.client.connect import ClientConnection
    from lib_openmolar.client.db_orm import PatientModel

    cc = ClientConnection()
    cc.connect()

    pt = PatientModel(1)
    SETTINGS.set_current_patient(pt)
    pt.treatment_model.update_views()

    dl = _TestDialog()
    dl.exec_()
