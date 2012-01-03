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
from PyQt4 import QtCore, QtGui

from lib_openmolar.common.dialogs import ExtendableDialog

from lib_openmolar.client.qt4gui import client_widgets

class ChooseClinicianFrame(QtGui.QFrame):
        '''
        allows user to choose a prescribing or completing clinician
        '''
        def __init__(self, completing, parent=None):
            QtGui.QFrame.__init__(self, parent)
            if completing:
                message = _("Who performed this treatment?")
            else:
                message = _("Who is prescribing this treatment?")

            label = QtGui.QLabel(message)

            self.dent_cb = QtGui.QComboBox()

            layout = QtGui.QHBoxLayout(self)
            layout.addWidget(label)
            layout.addWidget(self.dent_cb)


class TreatmentItemFinaliseDialog(ExtendableDialog):
    def __init__(self, parent=None):
        '''
        when a :doc:`TreatmentItem` is added,
        this dialog attempts to validate it.
        (ie.. is the item aware who prescribed it?
        if applicable - which tooth it relates to? etc. )
        '''
        ExtendableDialog.__init__(self, parent, remove_stretch=False)
        self.setWindowTitle(_("Additional Information is Required"))

        self.top_label = QtGui.QLabel(_("Additional Information is Required"))
        self.top_label.setAlignment(QtCore.Qt.AlignCenter)

        ## chart
        self.chart_frame = QtGui.QFrame()
        self.chart = client_widgets.ChartWidgetBase()
        #self.chart.setStyle(self.chart.CHART_STYLE_ROOTS)
        self.chart.setStyle(self.chart.CHART_STYLE_MIXED)

        teeth_needed_label = QtGui.QLabel()
        teeth_needed_label.setMinimumWidth(120)
        teeth_needed_label.setText(_("Which tooth is being treated?"))
        teeth_needed_label.setWordWrap(True)

        self.chosen_teeth_label = QtGui.QLabel("-")
        self.chosen_teeth_label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtGui.QGridLayout(self.chart_frame)
        layout.setMargin(0)
        layout.addWidget(teeth_needed_label)
        layout.addWidget(self.chosen_teeth_label,1,0)
        layout.addWidget(self.chart,0,1,2,1)

        ## tooth for selecting chosen surfaces

        self.surfaces_frame = QtGui.QFrame()
        self.tooth = client_widgets.ToothWidget()
        surfs_needed_label = QtGui.QLabel(_("Select surfaces"))
        self.chosen_surfaces_label = QtGui.QLabel("-")
        self.chosen_surfaces_label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtGui.QGridLayout(self.surfaces_frame)
        layout.setMargin(0)
        layout.addWidget(surfs_needed_label)
        layout.addWidget(self.chosen_surfaces_label,1,0)
        layout.addWidget(self.tooth,0,1,2,1)

        ## pontics chart
        self.pontics_frame = QtGui.QFrame()
        self.pontics_chart = client_widgets.ChartWidgetBase()
        #self.chart.setStyle(self.chart.CHART_STYLE_ROOTS)
        self.pontics_chart.setStyle(self.pontics_chart.CHART_STYLE_MIXED)

        teeth_needed_label = QtGui.QLabel()
        teeth_needed_label.setMinimumWidth(120)
        teeth_needed_label.setText(_("Replacing which Teeth?"))
        teeth_needed_label.setWordWrap(True)

        self.chosen_pontics_label = QtGui.QLabel("-")
        self.chosen_pontics_label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtGui.QGridLayout(self.pontics_frame)
        layout.setMargin(0)
        layout.addWidget(teeth_needed_label)
        layout.addWidget(self.chosen_pontics_label,1,0)
        layout.addWidget(self.pontics_chart,0,1,2,1)

        ## a combo box for prescribing clinician
        self.px_clinician_frame = ChooseClinicianFrame(completing=False)
        self.tx_clinician_frame = ChooseClinicianFrame(completing=True)

        ## a line edit for description
        self.description_frame = QtGui.QFrame()
        description_label = QtGui.QLabel(_("Description of item"))
        self.comment_line_edit = QtGui.QLineEdit()

        layout = QtGui.QHBoxLayout(self.description_frame)
        layout.setMargin(0)
        layout.addWidget(description_label)
        layout.addWidget(self.comment_line_edit)

        self.plan_completed_frame = QtGui.QFrame()
        layout = QtGui.QGridLayout(self.plan_completed_frame)
        self.completed_radiobutton = QtGui.QRadioButton(_("Completed Today"))
        self.planning_radiobutton = QtGui.QRadioButton(_("Planned Treatment"))
        self.planning_radiobutton.setChecked(True)
        layout.addWidget(self.planning_radiobutton, 0, 0)
        layout.addWidget(self.completed_radiobutton, 0, 1)
        layout.addWidget(self.tx_clinician_frame, 1,0,1,2)

        self.insertWidget(self.top_label)
        self.insertWidget(self.px_clinician_frame)
        self.insertWidget(self.chart_frame)
        self.insertWidget(self.pontics_frame)
        self.insertWidget(self.surfaces_frame)
        self.insertWidget(self.description_frame)
        self.insertWidget(self.plan_completed_frame)

        self.changes_list_widget = QtGui.QListWidget()
        self.add_advanced_widget(self.changes_list_widget)

        self.dent_key = 281474976645120  #adult only
        self.connect_signals()

    def sizeHint(self):
        return QtCore.QSize(400,600)

    def connect_signals(self):
        self.connect(self.chart,
            QtCore.SIGNAL("current tooth changed"), self.update_tooth_widget)
        self.connect(self.pontics_chart,
            QtCore.SIGNAL("current tooth changed"), self.update_widgets)
        self.connect(self.tooth, QtCore.SIGNAL("toothSurface"),
            self.update_surfaces)
        self.comment_line_edit.textEdited.connect(self.update_widgets)

        self.completed_radiobutton.toggled.connect(self.set_completed)

    def clear(self):
        self.chart.clear()
        self.pontics_chart.clear()
        self.tooth.clear()
        self.treatment_item = None
        self.comment_line_edit.setText("")
        self.px_clinician_frame.dent_cb.setCurrentIndex(-1)
        self.tx_clinician_frame.dent_cb.setCurrentIndex(-1)
        self.update_widgets()
        self.planning_radiobutton.setChecked(True)

    def set_completed(self, completed):
        '''
        this function is fired when the completed radio button is toggled
        '''
        if self.treatment_item is not None:
            if completed:
                self.treatment_item.set_cmp_date()
            else:
                self.treatment_item.set_completed(False)
        self.tx_clinician_frame.setVisible(completed)

    def showExtension(self, extend):
        if extend:
            self.changes_list_widget.clear()
            self.changes_list_widget.addItem(
                _("The following items need to be resolved by this dialog"))
            self.changes_list_widget.addItems(self.treatment_item.errors)

        ExtendableDialog.showExtension(self, extend)

    def update_tooth_widget(self):
        chosen_tooth = self.chart.current_tooth
        self.tooth.setTooth(chosen_tooth)

        if chosen_tooth == None:
            self.chosen_teeth_label.setText("-")
            self.update_surfaces("-")
        else:
            self.chosen_teeth_label.setText(chosen_tooth.long_name)
        self.update_widgets()

    def update_widgets(self, *args):
        chosen_tooth = self.pontics_chart.current_tooth
        if chosen_tooth == None:
            self.chosen_pontics_label.setText("-")
        else:
            self.chosen_pontics_label.setText(chosen_tooth.long_name)
        self.update_surfaces(self.tooth.filledSurfaces)

        self.enableApply(True)

    def update_surfaces(self, surfs):
        self.chosen_surfaces_label.setText(surfs)

    def set_known_teeth(self, key):
        self.dent_key = key

    @property
    def chosen_px_clinician(self):
        i = self.px_clinician_frame.dent_cb.currentIndex()
        if i == -1:
            return None
        index = SETTINGS.practitioners.dentists_model.index(i)
        practitioner = SETTINGS.practitioners.dentists_model.data(index,
            QtCore.Qt.UserRole)
        return practitioner.id

    @property
    def chosen_tx_clinician(self):
        i = self.tx_clinician_frame.dent_cb.currentIndex()
        if i == -1:
            return None
        index = SETTINGS.practitioners.dentists_model.index(i)
        practitioner = SETTINGS.practitioners.dentists_model.data(index,
            QtCore.Qt.UserRole)
        return practitioner.id

    def get_info(self, treatment_item, completing=False):
        '''
        executes the dialog in a loop, and modifies the :doc:`TreatmentItem`
        until it "is_vald" or the dialog is cancelled.
        '''
        self.clear()
        self.treatment_item = treatment_item
        if completing:
            message = u"%s  - %s"% (_("Add Item"), treatment_item.description)
        else:
            message = u"%s  - %s"% (_("Complete Item"),
                treatment_item.description)

        self.completed_radiobutton.setChecked(completing)
        self.completed_radiobutton.setVisible(not completing)
        self.planning_radiobutton.setVisible(not completing)

        self.top_label.setText(message)
        self.chart.set_known_teeth(self.dent_key)
        self.pontics_chart.set_known_teeth(self.dent_key)
        self.chart.allow_multi_select = treatment_item.allow_multiple_teeth

        if SETTINGS.current_practitioner is None:
            result = QtGui.QMessageBox.warning(self.parent(), _("warning"),
            "No clinician is set.. you will need to enter this manually",
            QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel)
            if result == QtGui.QMessageBox.Cancel:
                return False


        practitioners = SETTINGS.practitioners
        try:
            index = practitioners.index(SETTINGS.current_practitioner)
        except ValueError:
            index = -1

        self.tx_clinician_frame.dent_cb.setModel(practitioners.dentists_model)
        self.tx_clinician_frame.dent_cb.setCurrentIndex(index)

        self.px_clinician_frame.dent_cb.setModel(practitioners.dentists_model)
        self.px_clinician_frame.dent_cb.setCurrentIndex(index)

        get_pontics = treatment_item.pontics_required
        get_surfaces = treatment_item.surfaces_required
        get_comment = treatment_item.comment_required
        get_px_clinician = treatment_item.px_clinician is None
        get_tx_clinician = (treatment_item.is_completed and
            treatment_item.tx_clinician is None)
        get_teeth = treatment_item.tooth_required

        self.chart_frame.setVisible(get_teeth)
        self.pontics_frame.setVisible(get_pontics)
        self.surfaces_frame.setVisible(get_surfaces)
        self.description_frame.setVisible(get_comment)
        self.px_clinician_frame.setVisible(get_px_clinician)
        self.tx_clinician_frame.setVisible(get_tx_clinician)

        while True:
            if not self.exec_():
                break

            if treatment_item.is_completed:
                treatment_item.set_tx_clinician(self.chosen_tx_clinician)

            if get_px_clinician:
                treatment_item.set_px_clinician(self.chosen_px_clinician)

            if get_teeth:
                treatment_item.clear_metadata()

                if treatment_item.is_bridge:
                    treatment_item.set_abutments(self.chart.selected_teeth)
                else:
                    treatment_item.set_teeth(self.chart.selected_teeth)

            if get_pontics:
                treatment_item.set_pontics(self.pontics_chart.selected_teeth)

            if get_surfaces:
                treatment_item.set_surfaces(self.tooth.filledSurfaces)

            if get_comment:
                treatment_item.set_comment(
                    unicode(self.comment_line_edit.text()))

            valid, errors = treatment_item.check_valid()
            if not valid:
                message = u"<ul>"
                for error in errors:
                    message += "<li>%s</li>"% error

                QtGui.QMessageBox.warning(self, _("error"),
                    u"%s<hr />%s</ul>"% (
                    _("Please check the following"), message))

            else:
                return True

        return False

if __name__ == "__main__":

    from lib_openmolar.common.common_db_orm import TreatmentItem
    from lib_openmolar.client.connect import ClientConnection

    app = QtGui.QApplication([])

    cc = ClientConnection()
    cc.connect()

    dl = TreatmentItemFinaliseDialog()

    code = SETTINGS.PROCEDURE_CODES["D10"]
    item = TreatmentItem(code)
    #item.set_completed(True)
    while not item.is_valid:
        if not dl.get_info(item):
            break

    if False:
        for code in SETTINGS.PROCEDURE_CODES:
            item = TreatmentItem(code)
            item.set_px_clinician(1)
            if not item.is_valid:
                dl.get_info(item)

            print item
            print item.is_valid