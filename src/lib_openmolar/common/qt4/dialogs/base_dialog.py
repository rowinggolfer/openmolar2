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

class BaseDialog(QtGui.QDialog):
    '''
    A base class for all my dialogs
    provides a button box with ok and cancel buttons,
    slots connected to accept and reject
    has a VBoxlayout - accessed by self.layout
    '''
    def __init__(self, parent=None, remove_stretch=False):
        QtGui.QDialog.__init__(self, parent)

        self.button_box = QtGui.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            self.button_box.Cancel|self.button_box.Apply)

        self.cancel_but = self.button_box.button(self.button_box.Cancel)
        self.apply_but = self.button_box.button(self.button_box.Apply)

        self.button_box.setCenterButtons(True)

        self.layout = QtGui.QVBoxLayout(self)
        
        self.button_box.clicked.connect(self._clicked)

        self.check_before_reject_if_dirty = False
        self.dirty = False
        self.enableApply(False)

        self.spacer = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding)
        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.button_box)
        self.insertpoint_offset = 2

        if remove_stretch:
            self.remove_spacer()

    def sizeHint(self):
        '''
        Overwrite this function inherited from QWidget
        '''
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        '''
        Overwrite this function inherited from QWidget
        '''
        return QtCore.QSize(300, 300)

    def remove_spacer(self):
        '''
        If this is called, then the spacer added at init is removed.
        sometimes the spacer mucks up dialogs
        '''
        self.layout.removeItem(self.spacer)
        self.insertpoint_offset = 1

    def set_check_on_cancel(self, check):
        '''
        if true, then user will be asked if changes should be abandoned
        if the dialog is rejected, and given the opportunity to continue
        '''
        self.check_before_reject_if_dirty = check

    def set_accept_button_text(self, text):
        '''
        by default, the text here is "apply"...
        change as required using this function
        '''
        self.apply_but.setText(text)

    def set_reject_button_text(self, text):
        '''
        by default, the text here is "cancel"...
        change as required using this function
        '''
        self.cancel_but.setText(text)

    def insertWidget(self, widg):
        '''
        insert widget at the bottom of the layout
        '''
        count = self.layout.count()
        insertpoint = count - self.insertpoint_offset
        self.layout.insertWidget(insertpoint, widg)

    def _clicked(self, but):
        '''
        "private" function called when button box is clicked
        '''
        role = self.button_box.buttonRole(but)
        if role == QtGui.QDialogButtonBox.ApplyRole:
            self.accept()
        else:
            if not self.check_before_reject_if_dirty:
                self.reject()
            if (not self.dirty or QtGui.QMessageBox.question(self,
            _("Confirm"), _("Abandon Changes?"),
            QtGui.QMessageBox.Yes|QtGui.QMessageBox.Cancel,
            QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Yes):
                self.reject()

    def enableApply(self, enable=True):
        '''
        call this to enable the apply button (which is disabled by default)
        '''
        self.apply_but.setEnabled(enable)

if __name__ == "__main__":
    import gettext
    gettext.install("")

    def input(self, *args):
        dl.dirty = True
        dl.enableApply()

    app = QtGui.QApplication([])

    dl = BaseDialog()
    dl.set_check_on_cancel(True)

    label = QtGui.QLabel()
    label.setWordWrap(True)
    label.setText('''
    I am a dialog, which can only be 'applied' after valid user input''')

    cb = QtGui.QCheckBox("Example interaction")
    cb.toggled.connect(input)

    dl.insertWidget(label)
    dl.insertWidget(cb)

    dl.exec_()

    app.closeAllWindows()
