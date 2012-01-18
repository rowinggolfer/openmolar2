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

from lib_openmolar.common.qt4.dialogs import ExtendableDialog

class SaveDiscardCancelDialog(ExtendableDialog):
    def __init__(self, message, changes, parent=None):
        '''
        offers a choiced of save discard cancel, but allows for examination
        of what has changed.
        changes should be a function, which returns a string list
        '''
        ExtendableDialog.__init__(self, parent)
        self.set_advanced_but_text(_("What's changed?"))
        self.apply_but.setText("&Save")
        self.enableApply()
        self.save_on_exit = True

        label = QtGui.QLabel(message)
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.insertWidget(label)

        self.discard_but = self.button_box.addButton(
            QtGui.QDialogButtonBox.Discard)

        self.changes = changes
        self.changes_list_widget = QtGui.QListWidget()
        self.add_advanced_widget(self.changes_list_widget)

    def sizeHint(self):
        return QtCore.QSize(400,100)

    def clicked(self, but):
        if but == self.discard_but:
            self.discard()
            return
        ExtendableDialog.clicked(self, but)

    def discard(self):
        if QtGui.QMessageBox.question(self,_("Confirm"),
        _("Are you sure you want to discard these changes?"),
        QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.No )==QtGui.QMessageBox.Yes:
            self.save_on_exit = False
            self.accept()

    def showExtension(self, extend):
        if extend:
            self.changes_list_widget.clear()
            self.changes_list_widget.addItems(self.changes())
        ExtendableDialog.showExtension(self, extend)



if __name__ == "__main__":
    def changes():
        return ["Sname","Fname"]



    app = QtGui.QApplication([])
    message = "You have unsaved changes"

    dl = SaveDiscardCancelDialog(message, changes)
    print dl.exec_()