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

    refresh_clicked = QtCore.pyqtSignal()
    new_patient_clicked = QtCore.pyqtSignal()
    next_patient_clicked = QtCore.pyqtSignal()
    last_patient_clicked = QtCore.pyqtSignal()
    related_patient_clicked = QtCore.pyqtSignal()
    find_patient_clicked = QtCore.pyqtSignal()
    home_clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ControlPanel, self).__init__(parent)

        new_icon = QtGui.QIcon(':icons/add_user.png')
        back_icon = QtGui.QIcon(':icons/agt_back.png')
        related_icon = QtGui.QIcon(':icons/agt_family.png')
        next_icon = QtGui.QIcon(':icons/agt_forward.png')
        home_icon = QtGui.QIcon(':icons/agt_home.png')
        refresh_icon = QtGui.QIcon(':icons/agt_reload.png')
        find_icon = QtGui.QIcon(':icons/search.png')

        home_button = QtGui.QPushButton(home_icon, "")
        home_button.setFocusPolicy(QtCore.Qt.NoFocus)
        home_button.setToolTip(_( u"Exit the Current Patient Record."))
        home_button.setShortcut(_( u"Esc"))

        find_button = QtGui.QPushButton(find_icon, _(u"find"))
        find_button.setFocusPolicy(QtCore.Qt.NoFocus)
        find_button.setToolTip(
            _( u"Search for a patient in your database."))
        find_button.setShortcut(_( u"Ctrl+F"))

        new_button = QtGui.QPushButton(new_icon, "")
        new_button.setFocusPolicy(QtCore.Qt.NoFocus)
        new_button.setToolTip(_( u"Add a New Patient to the database."))

        back_button = QtGui.QPushButton(back_icon, "")
        back_button.setFocusPolicy(QtCore.Qt.NoFocus)
        back_button.setToolTip(
            _(u"cycle back through records loaded this session."))

        next_button = QtGui.QPushButton(next_icon, "")
        next_button.setFocusPolicy(QtCore.Qt.NoFocus)
        next_button.setToolTip(
            _(u"cycles forward through the history of records loaded today."))

        refresh_button = QtGui.QPushButton(refresh_icon, "")
        refresh_button.setFocusPolicy(QtCore.Qt.NoFocus)
        refresh_button.setToolTip(
            _(u"Reload the patient from the database."))

        related_button = QtGui.QPushButton(related_icon, _(u"Related"))
        related_button.setFocusPolicy(QtCore.Qt.NoFocus)
        related_button.setToolTip(
            _( u"Show patients with same family number, or similar address."))

        top_line_widget = QtGui.QWidget()
        line_layout = QtGui.QHBoxLayout(top_line_widget)
        line_layout.setMargin(0)
        line_layout.setSpacing(2)
        line_layout.addWidget(home_button)
        line_layout.addWidget(new_button)
        line_layout.addWidget(find_button)

        bottom_line_widget = QtGui.QWidget()
        line_layout = QtGui.QHBoxLayout(bottom_line_widget)
        line_layout.setMargin(0)
        line_layout.setSpacing(2)
        line_layout.addWidget(back_button)
        line_layout.addWidget(refresh_button)
        line_layout.addWidget(next_button)
        line_layout.addWidget(related_button)

        mainlayout = QtGui.QVBoxLayout(self)
        mainlayout.setMargin(0)
        mainlayout.setSpacing(2)
        mainlayout.addWidget(top_line_widget)
        mainlayout.addWidget(bottom_line_widget)

        home_button.clicked.connect(self.home_clicked.emit)
        refresh_button.clicked.connect(self.refresh_clicked.emit)
        back_button.clicked.connect(self.last_patient_clicked.emit)
        next_button.clicked.connect(self.next_patient_clicked.emit)
        related_button.clicked.connect(self.related_patient_clicked.emit)
        find_button.clicked.connect(self.find_patient_clicked.emit)
        new_button.clicked.connect(self.new_patient_clicked.emit)

    def sizeHint(self):
        return QtCore.QSize(200,60)

if __name__ == "__main__":

    def sig_catcher(*args):
        print args, cp.sender()

    from gettext import gettext as _

    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    layout = QtGui.QVBoxLayout(dl)
    cp = ControlPanel(dl)
    cp.refresh_clicked.connect(sig_catcher)
    cp.new_patient_clicked.connect(sig_catcher)
    cp.next_patient_clicked.connect(sig_catcher)
    cp.last_patient_clicked.connect(sig_catcher)
    cp.related_patient_clicked.connect(sig_catcher)
    cp.find_patient_clicked.connect(sig_catcher)
    cp.home_clicked.connect(sig_catcher)
    cp.new_patient_clicked.connect(sig_catcher)


    layout.addWidget(cp)
    dl.exec_()
