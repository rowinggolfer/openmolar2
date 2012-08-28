#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
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

from lib_openmolar.common.qt4.widgets import Advisor
from lib_openmolar.common.qt4.widgets import Preference
from lib_openmolar.common.qt4.widgets import FontOptionsWidget

class PreferencesDialog(QtGui.QDialog, Advisor):
    '''
    A custom dialog providing a listWidget and a connected panel
    '''
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        Advisor.__init__(self, parent)
        self.setWindowTitle(u"Openmolar %s"% _("Preferences"))

        self.listwidget = QtGui.QListWidget()
        close_but = QtGui.QPushButton(_("Close"))

        left_frame = QtGui.QFrame()

        layout = QtGui.QVBoxLayout(left_frame)
        layout.addWidget(QtGui.QLabel(_("Preference Options")))
        layout.addWidget(self.listwidget)
        layout.addWidget(close_but)

        self.stackedwidget = QtGui.QStackedWidget(self)

        splitter = QtGui.QSplitter(self)
        splitter.addWidget(left_frame)
        splitter.addWidget(self.stackedwidget)

        self.listwidget.currentRowChanged.connect(
            self.stackedwidget.setCurrentIndex)

        self.add_font_option()

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(splitter)

        close_but.clicked.connect(self.accept)

    def add_font_option(self):
        '''
        this is so useful, I include it by default
        '''
        pref = Preference(_("Fonts"))
        pref.setWidget(FontOptionsWidget(self.parent()))
        pref.setIcon(QtGui.QIcon.fromTheme("applications-fonts"))
        self.add_preference_dialog(pref)

    def iter_items(self):
        '''
        a hack because I couldn't get QListWidget.items() to work!!
        '''
        for i in range(self.listwidget.count()):
            yield self.listwidget.item(i)

    def select_preference(self, preference):
        '''
        pass in a string, and if it exists in the list, it will be selected
        typical usage would be PreferencesDialog.show_preference(_("Fonts"))
        '''
        for item in self.iter_items():
            if item.text() == preference:
                self.listwidget.setCurrentItem(item)
                return
        QtGui.QMessageBox.warning(self, "error",
            "couldn't find prefence %s"% preference)

    def minimumSizeHint(self):
        return QtCore.QSize(400, 400)

    def sizeHint(self):
        return QtCore.QSize(800, 500)

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

def _test():
    app = QtGui.QApplication([])
    dl = PreferencesDialog()
    dl.show()
    dl.select_preference(_("Fonts"))
    app.exec_()

if __name__ == "__main__":
    import gettext
    gettext.install("")
    _test()
