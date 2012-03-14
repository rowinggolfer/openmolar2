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


class ControlPanel(QtGui.QWidget):
    '''
    this class provides a widget which emits signals following user input
    indicating which patient record they wish to load
    Emits the following signals
    -New Patient
    -Next Patient
    -Last Patient
    -Related Patients
    -Find Patient
    -Home
    -Refresh Patient
    '''
    def __init__(self, parent=None):
        super(ControlPanel, self).__init__(parent)

        new_icon = QtGui.QIcon(':icons/add_user.png')
        back_icon = QtGui.QIcon(':icons/agt_back.png')
        related_icon = QtGui.QIcon(':icons/agt_family.png')
        next_icon = QtGui.QIcon(':icons/agt_forward.png')
        home_icon = QtGui.QIcon(':icons/agt_home.png')
        refresh_icon = QtGui.QIcon(':icons/agt_reload.png')
        find_icon = QtGui.QIcon(':icons/search.png')

        self.home_button = QtGui.QPushButton(home_icon, "")
        self.home_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.home_button.setToolTip(_( u"Exit the Current Patient Record."))
        self.home_button.setShortcut(_( u"Esc"))

        self.find_button = QtGui.QPushButton(find_icon, _(u"find"))
        self.find_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.find_button.setToolTip(
            _( u"Search for a patient in your database."))
        self.find_button.setShortcut(_( u"Ctrl+F"))

        self.new_button = QtGui.QPushButton(new_icon, "")
        self.new_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.new_button.setToolTip(_( u"Add a New Patient to the database."))

        self.back_button = QtGui.QPushButton(back_icon, "")
        self.back_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.back_button.setToolTip(
            _(u"cycle back through records loaded this session."))

        self.next_button = QtGui.QPushButton(next_icon, "")
        self.next_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.next_button.setToolTip(
            _(u"cycles forward through the history of records loaded today."))

        self.refresh_button = QtGui.QPushButton(refresh_icon, "")
        self.refresh_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.refresh_button.setToolTip(
            _(u"Reload the patient from the database."))

        self.related_button = QtGui.QPushButton(related_icon, _(u"Related"))
        self.related_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.related_button.setToolTip(
            _( u"Show patients with same family number, or similar address."))

        top_line_widget = QtGui.QWidget()
        line_layout = QtGui.QHBoxLayout(top_line_widget)
        line_layout.setMargin(0)
        line_layout.setSpacing(2)
        line_layout.addWidget(self.home_button)
        line_layout.addWidget(self.new_button)
        line_layout.addWidget(self.find_button)

        bottom_line_widget = QtGui.QWidget()
        line_layout = QtGui.QHBoxLayout(bottom_line_widget)
        line_layout.setMargin(0)
        line_layout.setSpacing(2)
        line_layout.addWidget(self.back_button)
        line_layout.addWidget(self.refresh_button)
        line_layout.addWidget(self.next_button)
        line_layout.addWidget(self.related_button)

        mainlayout = QtGui.QVBoxLayout(self)
        mainlayout.setMargin(0)
        mainlayout.setSpacing(2)
        mainlayout.addWidget(top_line_widget)
        mainlayout.addWidget(bottom_line_widget)

        self.home_button.clicked.connect(self.emit_home)
        self.refresh_button.clicked.connect(self.emit_refresh)
        self.back_button.clicked.connect(self.emit_last_patient)
        self.next_button.clicked.connect(self.emit_next_patient)
        self.related_button.clicked.connect(self.emit_related_patient)
        self.find_button.clicked.connect(self.emit_find_patient)
        self.new_button.clicked.connect(self.emit_new_patient)

    def sizeHint(self):
        return QtCore.QSize(200,60)

    def emit_new_patient(self):
        self.emit(QtCore.SIGNAL("New Patient"))

    def emit_next_patient(self):
        self.emit(QtCore.SIGNAL("Next Patient"))

    def emit_last_patient(self):
        self.emit(QtCore.SIGNAL("Last Patient"))

    def emit_related_patient(self):
        self.emit(QtCore.SIGNAL("Related Patients"))

    def emit_find_patient(self):
        self.emit(QtCore.SIGNAL("Find Patient"))

    def emit_home(self):
        self.emit(QtCore.SIGNAL("Home"))

    def emit_refresh(self):
        self.emit(QtCore.SIGNAL("Reload Patient"))


if __name__ == "__main__":

    def sig_catcher(*args):
        print args, cp.sender()

    
    
    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    layout = QtGui.QVBoxLayout(dl)
    cp = ControlPanel(dl)

    dl.connect(cp, QtCore.SIGNAL('New Patient'), sig_catcher)
    dl.connect(cp, QtCore.SIGNAL('Next Patient'), sig_catcher)
    dl.connect(cp, QtCore.SIGNAL('Last Patient'), sig_catcher)
    dl.connect(cp, QtCore.SIGNAL('Related Patients'), sig_catcher)
    dl.connect(cp, QtCore.SIGNAL('Find Patient'), sig_catcher)
    dl.connect(cp, QtCore.SIGNAL('Home'), sig_catcher)
    dl.connect(cp, QtCore.SIGNAL('Refresh Patient'), sig_catcher)

    layout.addWidget(cp)
    dl.exec_()
