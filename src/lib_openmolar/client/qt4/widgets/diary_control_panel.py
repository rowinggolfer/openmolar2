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

class DiaryControl(QtGui.QWidget):
    '''
    A widget to allow user choice of parameters to show what information
    is displayed on the diary (date, clinician etc...)
    '''

    date_changed = QtCore.pyqtSignal(object)
    '''
    signal indicating that the date has changed.
    supplies a QDate
    '''

    view_changed = QtCore.pyqtSignal(object)
    '''
    signal indicating that the user want to view a different style
    eg day, week, fortnight etc...
    '''

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.calendar = QtGui.QCalendarWidget()
        self.calendar.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.calendar.setVerticalHeaderFormat(self.calendar.NoVerticalHeader)
        self.calendar.setMaximumSize(self.calendar.minimumSizeHint())

        top_frame = QtGui.QFrame(self)

        icon = QtGui.QIcon.fromTheme("document-print")
        print_button = QtGui.QPushButton(icon, "Print")
        print_button.setFlat(True)

        self.combo_box = QtGui.QComboBox(self)
        self.combo_box.addItems([_("Day"),_("Four Days"), _("Week"),
            _("Fortnight"), _("Month"), _("Year"), _("Agenda"), ("Tasks")])

        padding = 9
        ##DENTISTS
        dentist_frame = QtGui.QFrame()
        dentist_frame.setMaximumHeight(120)

        self.dentist_layout = QtGui.QGridLayout(dentist_frame)

        label = QtGui.QLabel(_("Dentists"))
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.dentist_layout.setMenuBar(label)
        ##HYGIENISTS
        hygienist_frame = QtGui.QFrame()
        hygienist_frame.setMaximumHeight(120)

        self.hygienist_layout = QtGui.QGridLayout(hygienist_frame)

        label = QtGui.QLabel(_("Hygienists"))
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.hygienist_layout.setMenuBar(label)

        ##STAFF
        staff_frame = QtGui.QFrame()
        staff_frame.setMaximumHeight(120)

        self.staff_layout = QtGui.QGridLayout(staff_frame)

        label = QtGui.QLabel(_("Staff"))
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.staff_layout.setMenuBar(label)


        layout = QtGui.QVBoxLayout(self)
        layout.setMargin(padding)
        layout.addWidget(self.calendar)
        layout.addWidget(self.combo_box)
        layout.addWidget(dentist_frame)
        layout.addWidget(hygienist_frame)
        layout.addWidget(staff_frame)

        layout.addWidget(print_button)
        layout.addStretch()

        self.setMaximumWidth(self.calendar.width()+ padding*2)

        self.calendar.selectionChanged.connect(self.date_change)
        self.combo_box.currentIndexChanged.connect(self.view_change)

    def set_limits(self, start, end):
        self.calendar.setMinimumDate(start)
        self.calendar.setMaximumDate(end)

    def refresh_practitioners(self, practitioners):
        self.practitioners = practitioners
        #if not self.practitioner_layout.isEmpty():
        #    self.practitioner_frame.clear()
        row, col = 0, 0
        for type_, layout in (  ("dentist",self.dentist_layout),
                                ("hygienist", self.hygienist_layout)):
            for practitioner in practitioners:
                widg = practitioner.avatar_widget
                if practitioner.type == type_:
                    layout.addWidget(widg, row, col%4)
                    col += 1
                    if col%4 == 0:
                        row += 1

    def refresh_staff_members(self, staff_members):
        self.staff_members = staff_members

        #if not self.practitioner_layout.isEmpty():
        #    self.practitioner_frame.clear()
        row, col = 0, 0
        for staff in staff_members:
            widg = staff.avatar_widget
            self.staff_layout.addWidget(widg, row, col%8)
            col += 1
            if col % 8 == 0:
                row += 1

    @property
    def selected_practitioners(self):
        selected = []
        for practitioner in self.practitioners:
            if practitoner.is_active:
                selected.append(practitioner)
        return selected

    def sizeHint(self):
        return QtCore.QSize(self.maximumWidth(), 400)

    def date_change(self):
        date = self.calendar.selectedDate()
        self.date_changed.emit(date)

    def view_change(self, i):
        self.view_changed.emit(i)

if __name__ == "__main__":

    from lib_openmolar.client.connect import DemoClientConnection
    cc = DemoClientConnection()
    cc.connect()

    app = QtGui.QApplication([])
    dl = QtGui.QDialog()

    obj = DiaryControl(dl)
    obj.refresh_practitioners(SETTINGS.practitioners)
    obj.refresh_staff_members(SETTINGS.staff_members)

    layout = QtGui.QVBoxLayout(dl)
    layout.setMargin(0)
    layout.addWidget(obj)

    dl.exec_()