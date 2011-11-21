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

from PyQt4 import QtGui, QtCore
from lib_openmolar.common.widgets import Advisor

class Preference(object):
    '''
    A custom data structure used by PreferencesDialog
    '''
    def __init__(self, title):
        self.title = title
        self.icon = QtGui.QIcon.fromTheme("help-about")
        self.widget = QtGui.QLabel(title + " hello world")

    def setIcon(self, icon):
        self.icon = icon

    def setWidget(self, widget):
        self.widget = widget

class PreferencesDialog(QtGui.QMainWindow, Advisor):
    '''
    A custom dialog providing a listWidget and a connected panel
    '''
    def __init__(self, parent=None):
        super(PreferencesDialog, self).__init__(parent)
        Advisor.__init__(self)
        self.setWindowTitle(u"Openmolar %s"% _("Preferences"))
        self.setMinimumSize(400, 400)

        self.listwidget = QtGui.QListWidget()
        self.stackedwidget = QtGui.QStackedWidget(self)

        splitter = QtGui.QSplitter(self)
        splitter.addWidget(self.listwidget)
        splitter.addWidget(self.stackedwidget)

        self.connect(self.listwidget,
            QtCore.SIGNAL("currentRowChanged (int)"),
            self.stackedwidget.setCurrentIndex)

        self.add_font_option()

        self.setCentralWidget(splitter)

    def add_font_option(self):
        '''
        this is so useful, I include it by default
        '''
        pref = Preference(_("Fonts"))
        pref.setWidget(FontOptionsWidget(self.parent()))
        pref.setIcon(QtGui.QIcon.fromTheme("applications-fonts"))
        self.add_preference_dialog(pref)

    def add_preference_dialog(self, preference):
        '''
        takes a single instance of Preference class
        and adds it to the dialog
        '''
        self.insert_preference_dialog(-1, preference)

    def insert_preference_dialog(self, index, preference):
        '''
        takes a single instance of Preference class
        and adds it to the dialog
        '''
        count = self.listwidget.count()
        if index < 0 or index > count:
            index = count
        list_widget_item = QtGui.QListWidgetItem()
        list_widget_item.setIcon(preference.icon)
        list_widget_item.setText(preference.title)

        self.listwidget.insertItem(index, list_widget_item)

        scrollarea = QtGui.QScrollArea(self)
        scrollarea.setWidgetResizable(True)
        scrollarea.setWidget(preference.widget)
        self.stackedwidget.insertWidget(index, scrollarea)

        self.listwidget.setCurrentRow(index)

    def exec_(self):
        '''
        With the advent of gnome3.. it became clear that this isn't a dialog at
        all.
        so I changed the base class to QMainWindow, and put exec_ here for
        backwards compatibility
        '''
        self.show()

class FontOptionsWidget(QtGui.QWidget):
    '''
    a widget, added at runtime to the preferences dialog,
    standard fonts dialog
    '''
    def __init__(self, parent=None):
        super(FontOptionsWidget, self).__init__(parent)
        try:
            self.systemFont = parent.system_font
            self.initialFont = parent.font()
        except AttributeError:
            font = QtGui.QApplication.instance().font()
            self.systemFont = font
            self.initialFont = font

        self.fontdialog = QtGui.QFontDialog()
        self.fontdialog.setCurrentFont(self.initialFont)
        self.fontdialog.setOption(self.fontdialog.NoButtons)

        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.addButton(buttonBox.Apply)
        self.resetBut = buttonBox.addButton(_("Reset to Original Font"),
            buttonBox.RejectRole)
        self.systemBut = buttonBox.addButton(_("Use System Font"),
            buttonBox.ResetRole)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.fontdialog)

        layout.addWidget(buttonBox)

        self.connect(buttonBox, QtCore.SIGNAL("clicked (QAbstractButton *)"),
            self.apply)

    def apply(self, but):
        if but == self.resetBut:
            self.fontdialog.setCurrentFont(self.initialFont)
        elif but == self.systemBut:
            self.fontdialog.setCurrentFont(self.systemFont)
        QtGui.QApplication.instance().setFont(self.fontdialog.currentFont())

def _test():
    app = QtGui.QApplication([])
    dl = PreferencesDialog()
    dl.show()
    app.exec_()

if __name__ == "__main__":
    import gettext
    gettext.install("")
    _test()
