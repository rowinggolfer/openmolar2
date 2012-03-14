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

'''
This Module provides one class - AddNotesWidget
'''

from PyQt4 import QtCore, QtGui
from lib_openmolar.common.qt4 import widgets

class AddNotesWidget(QtGui.QWidget):
    '''
    A custom widget to take text entry and signal when completed.
    '''
    def __init__(self, parent=None):
        '''
        AddNotesWidget.__init__(self, parent=None)
        '''
        QtGui.QWidget.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        #: a pointer to the :doc:`CompletionTextEdit` component
        self.text_edit = widgets.CompletionTextEdit(self)
        save_but = QtGui.QPushButton(_("&Save"), self)
        save_but.setSizePolicy(QtGui.QSizePolicy.Preferred,
            QtGui.QSizePolicy.Expanding)

        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.text_edit)
        layout.addWidget(save_but)

        save_but.clicked.connect(self.emit_save)

    def minimumSizeHint(self):
        '''
        overwrite the base class method
        return QtCore.QSize(200,50)
        '''
        return QtCore.QSize(200,50)

    def sizeHint(self):
        '''
        overwrite the base class method
        return QtCore.QSize(500,120)
        '''
        return QtCore.QSize(500, 120)

    def emit_save(self):
        '''
        this function is called when user clicks the save button

        >>> self.emit(QtCore.SIGNAL("Save Requested"))

        '''
        self.emit(QtCore.SIGNAL("Save Requested"))

    def set_text(self, text):
        '''
        A convenience function to access :doc:`CompletionTextEdit` component's
        setText functionality
        '''
        self.text_edit.setText(text)

    @property
    def text(self):
        '''
        A convenience function to access :doc:`CompletionTextEdit` component's
        current text
        '''
        return self.text_edit.document().toPlainText()

if __name__ == "__main__":
    def sig_catcher():
        print "save request sent!"
    app = QtGui.QApplication([])
    obj = AddNotesWidget()
    obj.connect(obj, QtCore.SIGNAL("Save Requested"), sig_catcher)
    obj.show()
    app.exec_()
    print obj.text
