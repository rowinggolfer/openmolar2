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


from lib_openmolar.client.qt4gui.client_widgets import chart_widgets

import tooth_data_list_widget
import chart_line_edit
import chart_editor_tooth

from lib_openmolar.client.qt4gui.client_widgets.procedures import crown_codes_model



class ToothDataEditor(QtGui.QWidget):
    '''
    this class provides the widget for the right hand side of the charts page
    '''
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.current_tooth = None
        self.tooth_label = QtGui.QLabel("")
        self.tooth_label.setAlignment(QtCore.Qt.AlignCenter)
        self.line_edit = chart_line_edit.ChartLineEdit(self)
        self.tooth_data_list_widget = tooth_data_list_widget.ToothDataListWidget()

        self.tooth_editor = chart_editor_tooth.ToothEditor(self)

        self.roots_combo_box = QtGui.QComboBox()
        self.roots_combo_box.addItem(_("ROOTS"))
        root_list = SETTINGS.OM_TYPES["root_description"].selections
        self.roots_combo_box.addItems(root_list)

        self.crowns_combo_box = QtGui.QComboBox()
        self.crowns_combo_box.setModel(crown_codes_model.CrownCodesModel())

        self.show_fee_widget_button = QtGui.QPushButton(_("Procedure Codes"))

        edit_frame = QtGui.QFrame()
        layout = QtGui.QVBoxLayout(edit_frame)
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.addWidget(self.tooth_data_list_widget)
        layout.addWidget(self.line_edit)

        splitter = QtGui.QSplitter(self)
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.addWidget(edit_frame)
        splitter.addWidget(self.tooth_editor)
        splitter.addWidget(self.roots_combo_box)
        splitter.addWidget(self.crowns_combo_box)
        splitter.addWidget(self.show_fee_widget_button)

        self.connect_signals()

        layout = QtGui.QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.tooth_label)
        layout.addWidget(splitter)

    def advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    @property
    def is_dirty(self):
        return self.line_edit.text() != ""

    def minimumSizeHint(self):
        return QtCore.QSize(80,200)

    def sizeHint(self):
        return QtCore.QSize(200,600)

    def clear(self):
        self.current_tooth = None
        self.tooth_label.setText("")
        self.tooth_editor.clear()
        self.tooth_data_list_widget.clear()
        self.line_edit.setText("")

    def keyPressEvent(self, event):
        self.line_edit.keyPressEvent(event)

    def add_property_to_current_tooth(self):
        if not self.current_tooth:
            return
        prop = chart_widgets.ToothData(self.current_tooth)

        try:
            prop.from_user_input(self.line_edit.trimmed_text)
            self.current_tooth.add_property(prop)
            self.tooth_data_list_widget.setTooth(self.current_tooth)

            try:
                chart = self.current_tooth.data_model.views[0]
                plan_or_cmp = chart.treatment_addition_cat

                ## this signal is eventually caught by the
                ## estimates page.chart_treatment_added
                self.emit(QtCore.SIGNAL("add treatment"), prop, plan_or_cmp)

            except AttributeError:
                #static or summary charts don't have treatment_added
                pass

            return True
        except chart_widgets.ToothDataError as e:
            if QtGui.QMessageBox.question(self,
            _("question"),
            u"error from input '%s'<br />%s<hr />delete input?"% (
            self.line_edit.trimmed_text, e),
            QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
            QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:
                self.line_edit.setText("")
            return False

    def add_crown_property_to_current_tooth(self, index):
        '''
        catches a signal that the row of the crown combobox has changed
        '''
        if not self.current_tooth or index == 0: #row 0 is a header
            pass
        else:
            model = self.crowns_combo_box.model()
            index = model.index(index)
            chosen_crown = model.data(index, QtCore.Qt.UserRole)
            print chosen_crown
            prop = chart_widgets.ToothData(self.current_tooth)
            prop.from_proc_code(chosen_crown)
            self.current_tooth.add_property(prop)
            self.tooth_data_list_widget.setTooth(self.current_tooth)
            try:
                chart = self.current_tooth.data_model.views[0]
                plan_or_cmp = chart.treatment_addition_cat

                ## this signal is eventually caught by the
                ## estimates page.chart_treatment_added
                self.emit(QtCore.SIGNAL("add treatment"), prop, plan_or_cmp)

            except AttributeError:
                #static chart doesn't have a treatment_added attribute
                pass

        self.crowns_combo_box.setCurrentIndex(0)

    def apply_edits(self):
        if not self.is_dirty:
            return True
        return self.add_property_to_current_tooth()

    def tooth_editor_input_finished(self):
        self.apply_edits()
        self.line_edit.setText("")

    def setTooth(self, tooth):
        '''
        make the editor aware of the tooth selected by the charts
        '''
        if not self.apply_edits():
            return False

        self.current_tooth = tooth
        self.tooth_editor.setTooth(tooth)
        if tooth:
            self.tooth_label.setText(tooth.long_name)
            self.tooth_data_list_widget.setTooth(tooth)
            self.line_edit.setText("")
            #self.line_edit.setText(tooth.line_edit_text)
        else:
            self.clear()
        return True

    def updateSurfaces(self, arg):
        existing = str(self.line_edit.text().toAscii())
        keep = ""
        currentFill = existing
        if "," in currentFill:                          #we have a material
            split = currentFill.split(",")
            mat = "," + split[1]
            currentFill = self.tooth_editor.tooth_widget.filledSurfaces + mat
        else:                                           #virgin tooth
            currentFill = arg
        self.line_edit.setText(keep+currentFill)

    def updateMaterial(self, arg):
        existing = str(self.line_edit.text().toAscii())
        keep = ""
        currentFill = existing
        if "," in currentFill: #already a material set! replace it.
            split = currentFill.split(",")
            surfaces = split[0]
            currentFill = surfaces+","+arg
        else:
            currentFill += "," + arg
        self.line_edit.setText(keep + currentFill)

    def _call_fee_widget(self):
        '''
        the "procedure codes" button has been pressed, emit a signal
        '''
        self.emit(QtCore.SIGNAL("Show Fee Widget"))

    def connect_signals(self):
        self.connect(self.tooth_editor.tooth_widget,
            QtCore.SIGNAL("toothSurface"), self.updateSurfaces)

        self.connect(self.tooth_editor.tooth_widget,
            QtCore.SIGNAL("material"),self.updateMaterial)

        self.connect(self.tooth_editor, QtCore.SIGNAL("editing finished"),
            self.tooth_editor_input_finished)

        self.connect(self.line_edit, QtCore.SIGNAL("User Input"),
            self.apply_edits)

        self.show_fee_widget_button.clicked.connect(self._call_fee_widget)

        self.crowns_combo_box.currentIndexChanged.connect(
            self.add_crown_property_to_current_tooth)

if __name__ == "__main__":

    def sig_catcher(*args):
        print args, dl.sender()

    
    
    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    obj = ToothDataEditor(dl)

    dl.connect(obj, QtCore.SIGNAL("Code Selected"), sig_catcher)

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(obj)
    dl.exec_()
