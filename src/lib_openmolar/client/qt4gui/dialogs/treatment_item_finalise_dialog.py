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


class TreatmentItemFinaliseDialog(ExtendableDialog):
    def __init__(self, parent=None):
        '''
        when a :doc:`TreatmentItem` is added,
        this dialog attempts to validate it.
        (ie.. is the item aware who prescribed it?
        if applicable - which tooth it relates to? etc. )
        '''
        ExtendableDialog.__init__(self, parent)
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
        self.px_clinician_frame = QtGui.QFrame()

        label = QtGui.QLabel(_("Who is prescribing this treatment?"))

        self.px_dent_cb = QtGui.QComboBox()

        layout = QtGui.QHBoxLayout(self.px_clinician_frame)
        layout.addWidget(label)
        layout.addWidget(self.px_dent_cb)

        ## a line edit for description
        self.description_frame = QtGui.QFrame()
        description_label = QtGui.QLabel(_("Description of item"))
        self.description_line_edit = QtGui.QLineEdit()

        layout = QtGui.QHBoxLayout(self.description_frame)
        layout.setMargin(0)
        layout.addWidget(description_label)
        layout.addWidget(self.description_line_edit)

        self.insertWidget(self.top_label)
        self.insertWidget(self.px_clinician_frame)
        self.insertWidget(self.chart_frame)
        self.insertWidget(self.pontics_frame)
        self.insertWidget(self.surfaces_frame)
        self.insertWidget(self.description_frame)

        self.changes_list_widget = QtGui.QListWidget()
        self.add_advanced_widget(self.changes_list_widget)

        self.dent_key = 281474976645120  #adult only
        self.info_list = []
        self.connect_signals()

    def sizeHint(self):
        return QtCore.QSize(400,100)

    def connect_signals(self):
        self.connect(self.chart,
            QtCore.SIGNAL("current tooth changed"), self.update_tooth_widget)
        self.connect(self.pontics_chart,
            QtCore.SIGNAL("current tooth changed"), self.update_widgets)
        self.connect(self.tooth, QtCore.SIGNAL("toothSurface"),
            self.update_surfaces)
        self.description_line_edit.textEdited.connect(self.update_widgets)

    def clear(self):
        self.chart.clear()
        self.pontics_chart.clear()
        self.tooth.clear()
        self.treatment_item = None
        self.description_line_edit.setText("")
        self.px_dent_cb.setCurrentIndex(-1)
        self.update_widgets()

    def showExtension(self, extend):
        if extend:
            self.changes_list_widget.clear()
            self.changes_list_widget.addItems(self.info_list)
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
        i = self.px_dent_cb.currentIndex()
        model = self.px_dent_cb.model()
        index = model.index(i)
        practitioner = model.data(index, QtCore.Qt.UserRole)
        return practitioner.id

    def get_info(self, treatment_item):
        self.clear()
        self.top_label.setText(
            u"%s  - %s"% (_("Add Item"), treatment_item.description))
        self.chart.set_known_teeth(self.dent_key)
        self.pontics_chart.set_known_teeth(self.dent_key)

        self.chart_frame.setVisible(treatment_item.tooth_required)
        self.chart.allow_multi_select = treatment_item.allow_multiple_teeth

        self.pontics_frame.setVisible(treatment_item.pontics_required)

        self.surfaces_frame.setVisible(treatment_item.surfaces_required)

        self.description_frame.setVisible(treatment_item.description_required)

        practitioners = SETTINGS.practitioners
        try:
            index = practitioners.index(SETTINGS.current_practitioner)
        except ValueError:
            index = -1
        self.px_dent_cb.setModel(practitioners.dentists_model)
        self.px_dent_cb.setCurrentIndex(index)


        if treatment_item.px_clinician is None:
            self.px_clinician_frame.show()
        else:
            self.px_clinician_frame.hide()

        self.info_list = ["hello world"]

        while True:
            if not self.exec_():
                break

            treatment_item.set_px_clinician(self.chosen_px_clinician)
            treatment_item.set_teeth(self.chart.selected_teeth)
            treatment_item.set_pontics(self.pontics_chart.selected_teeth)

            tooth = self.chart.current_tooth
            if tooth:
                treatment_item.set_tooth(tooth.tooth_id)
            treatment_item.set_surfaces(self.tooth.filledSurfaces)

            treatment_item.set_description(
                unicode(self.description_line_edit.text()))

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

    for code in SETTINGS.PROCEDURE_CODES:
        item = TreatmentItem(code)
        item.set_px_clinician(1)
        if not item.is_valid:
            dl = TreatmentItemFinaliseDialog()
            dl.get_info(item)

        print item
        print item.is_valid