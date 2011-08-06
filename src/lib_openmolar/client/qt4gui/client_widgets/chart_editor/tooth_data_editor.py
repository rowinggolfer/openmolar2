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

from tooth_data_list_widget import ToothDataListWidget
from chart_line_edit import ChartLineEdit
from chart_editor_tooth import ToothEditor
from navigate_frame import NavigateFrame
from static_shortcuts_frame import StaticShortcutsFrame

from lib_openmolar.client.qt4gui.client_widgets.procedures.crown_codes_model \
    import CrownCodesModel

class ToothDataEditor(QtGui.QWidget):
    '''
    this class provides the widget for the right hand side of the charts page
    '''
    #:
    STATIC_MODE = 0
    #:
    PLANNING_MODE = 1
    #:
    mode = STATIC_MODE
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        #: a pointer to the chart being edited
        self.current_chart = None
        #:
        self.current_tooth = None
        #:
        self.tooth_label = QtGui.QLabel("")
        self.tooth_label.setAlignment(QtCore.Qt.AlignCenter)
        #:
        self.line_edit = ChartLineEdit(self)
        #: a pointer to the :doc:`ToothDataListWidget`
        self.tooth_data_list_widget = ToothDataListWidget()

        #: a pointer to the :doc:`ToothEditor`
        self.tooth_editor = ToothEditor(self)

        self.roots_combo_box = QtGui.QComboBox()
        '''populated with :doc:`OMTypes` ["root_description"].selections'''
        self.roots_combo_box.addItem(_("ROOTS"))
        root_list = SETTINGS.OM_TYPES["root_description"].selections
        self.roots_combo_box.addItems(root_list)

        #: populated with :doc:`CrownCodesModel`
        self.crowns_combo_box = QtGui.QComboBox()
        self.crowns_combo_box.setModel(CrownCodesModel())

        #:
        self.navigate_buttons = NavigateFrame()
        #:
        self.static_buttons = StaticShortcutsFrame()

        #:
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
        splitter.addWidget(self.navigate_buttons)
        splitter.addWidget(self.static_buttons)
        splitter.addWidget(self.roots_combo_box)
        splitter.addWidget(self.crowns_combo_box)
        splitter.addWidget(self.show_fee_widget_button)

        self.connect_signals()

        layout = QtGui.QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.tooth_label)
        layout.addWidget(splitter)

        self.connect(self.static_buttons, QtCore.SIGNAL("Shortcut"),
            self.shortcut_received)

    def advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def set_mode(self, static=True):
        '''
        this widget has two modes.. static or planning
        '''
        self.current_chart = self.sender()

        current_mode = self.mode
        self.mode = self.STATIC_MODE if static else self.PLANNING_MODE

        if current_mode != self.mode:
            self.apply_mode()

    def apply_mode(self):
        if self.mode == self.STATIC_MODE:
            self.static_buttons.show()
        else:
            self.static_buttons.hide()

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

    def shortcut_received(self, shortcut):
        '''
        this is connected to the static_buttons
        '''
        if shortcut == "TM":
            self.emit(QtCore.SIGNAL("toggle_tooth_present"))
        elif shortcut == "AT":
            self.advise("AT doesn't work yet")
        else:
            self.line_edit.setText(shortcut)

        self.line_edit.finished_edit()

    def keyPressEvent(self, event):
        self.line_edit.keyPressEvent(event)

    def add_property_to_current_tooth(self):
        if not self.current_tooth:
            SETTINGS.log("not adding property.. no current tooth selected")
            return

        tooth_data = chart_widgets.ToothData(self.current_tooth.tooth_id)
        input = self.line_edit.trimmed_text
        if self.mode == self.STATIC_MODE:

            try:
                tooth_data.from_user_input(input)
                self.current_tooth.add_property(tooth_data)
                self.tooth_data_list_widget.setTooth(self.current_tooth)

                return True
            except chart_widgets.ToothDataError as e:
                self.invalid_input(e)
                return False

        else:
            plan_or_cmp = self.current_chart.treatment_addition_cat
            try:
                tooth_data.from_user_input(input)
            except chart_widgets.ToothDataError as e:
                pass

            tooth_data.tx_input = input
            self.emit(QtCore.SIGNAL("add treatment"), tooth_data, plan_or_cmp)

    def invalid_input(self, error=""):
        '''
        alert the user that the text entered is garbage, and offer to delete it
        '''
        if QtGui.QMessageBox.question(self,
            _("question"),
            u"error from input '%s'<br />%s<hr />delete input?"% (
            self.line_edit.trimmed_text, error),
            QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
            QtGui.QMessageBox.Yes) == QtGui.QMessageBox.Yes:

            self.line_edit.setText("")

    def valid_input(self):
        '''
        clear the line edit
        '''
        self.line_edit.setText("")

    def add_crown_property_to_current_tooth(self, index):
        '''
        catches a signal that the row of the crown combobox has changed
        '''

        ##TODO - this is broken!!!
        if not self.current_tooth or index == 0: #row 0 is a header
            pass
        else:
            model = self.crowns_combo_box.model()
            index = model.index(index)
            chosen_crown = model.data(index, QtCore.Qt.UserRole)

            tooth_data = chart_widgets.ToothData(self.current_tooth.tooth_id)
            tooth_data.from_proc_code(chosen_crown)
            self.current_tooth.add_property(to)
            self.tooth_data_list_widget.setTooth(self.current_tooth)
            try:
                chart = self.current_tooth.data_model.views[0]
                plan_or_cmp = chart.treatment_addition_cat

                ## this signal is eventually caught by the
                ## treaments page.chart_treatment_added
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

    def nav_key(self, event):
        '''
        pass on some key presses to the current chart
        '''
        if self.current_chart:
            self.current_chart.keyPressEvent(event)

    def navigate(self, direction):
        '''
        catches signals from components requesting a move to another tooth
        '''
        if self.current_tooth is None:
            new_ref = None
        elif direction == "next":
            new_ref = self.current_tooth.ref_next
        elif direction == "prev":
            new_ref = self.current_tooth.ref_prev
        else:
            new_ref = None

        result = self.apply_edits()
        if result:
            self.line_edit.clear()
        else:
            return

        if direction == "stay":
            return

        if self.current_chart:
            self.current_chart.set_current_tooth(new_ref)
            self.current_chart.redraw_check()

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

        self.show_fee_widget_button.clicked.connect(self._call_fee_widget)

        self.crowns_combo_box.currentIndexChanged.connect(
            self.add_crown_property_to_current_tooth)

        self.connect(self.line_edit,
            QtCore.SIGNAL("Navigate"), self.navigate)

        self.connect(self.navigate_buttons,
            QtCore.SIGNAL("Navigate"), self.navigate)

        self.connect(self.line_edit,
            QtCore.SIGNAL("Nav_key"), self.nav_key)

if __name__ == "__main__":

    def sig_catcher(*args):
        print args, dl.sender()

    from lib_openmolar.client.qt4gui.client_widgets.chart_widgets import \
        teeth, chart_data_model

    model = chart_data_model.ChartDataModel()
    tooth = teeth.ChartTooth(1, model)

    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    obj = ToothDataEditor(dl)
    obj.setTooth(tooth)

    dl.connect(obj, QtCore.SIGNAL("Code Selected"), sig_catcher)

    static_button = QtGui.QRadioButton("static")
    static_button.setChecked(True)
    planning_button = QtGui.QRadioButton("planning")

    static_button.toggled.connect(obj.set_mode)

    toggle_frame = QtGui.QFrame()
    layout = QtGui.QVBoxLayout(toggle_frame)
    layout.addWidget(static_button)
    layout.addWidget(planning_button)

    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(obj)
    layout.addWidget(toggle_frame)
    dl.exec_()
