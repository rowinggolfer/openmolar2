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
provides the BaseMainWindow class
a basic re-implementation of QtGui.QMainWindow that can save state etc..
'''

from PyQt4 import QtGui, QtCore
from lib_openmolar.common.widgets import Advisor, DockAwareToolBar, \
    DockableMenuBar

class BaseMainWindow(QtGui.QMainWindow, Advisor):
    '''
    This class is a MainWindow, with menu, toolbar and statusbar.
    Some of the layout signals/slots already connected.
    Provides about, about QT and license dialogs.
    '''
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        Advisor.__init__(self, parent)

        self.setMinimumSize(300, 300)

        #####          setup menu and headers                              ####

        self.main_toolbar = DockAwareToolBar()
        self.menubar = DockableMenuBar(self)

        ## the menu bar needs this action adding
        self.menubar.addViewOption(self.main_toolbar.toggleViewAction())

        ## add them to the app
        self.setMenuBar(self.menubar)

        self.addToolBar(QtCore.Qt.TopToolBarArea, self.main_toolbar)

        ## make them aware of one another
        self.connect(self.menuBar(), QtCore.SIGNAL("mini menu required"),
            self.main_toolbar.add_mini_menu)
        self.connect(self.menuBar(), QtCore.SIGNAL("hide mini menu"),
            self.main_toolbar.clear_mini_menu)
        self.main_toolbar.toggleViewAction().triggered.connect(
            self.menuBar().setNotVisible)

        ####          setup a statusbar with a label                       ####

        self.statusbar = QtGui.QStatusBar()
        self.setStatusBar(self.statusbar)
        self.status_label = QtGui.QLabel()
        self.statusbar.addPermanentWidget(self.status_label)

        self.menu_file = QtGui.QMenu(_("&File"), self)
        self.menubar.addMenu(self.menu_file)

        self.menu_edit = QtGui.QMenu(_("&Edit"), self)
        self.menubar.addMenu(self.menu_edit)

        self.menu_view = self.menubar.menu_view #QtGui.QMenu(_("&View"), self)
        #self.menubar.addMenu(self.menu_view)

        self.menu_help = QtGui.QMenu(_("&Help"), self)
        self.menubar.addMenu(self.menu_help)

        ####          file menu                                            ####

        icon = QtGui.QIcon.fromTheme("application-exit")

        self.action_quit = QtGui.QAction(icon, _("Quit"), self)

        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_quit)

        ####         edit menu                                             ####

        icon = QtGui.QIcon.fromTheme("preferences-desktop")
        self.action_preferences = QtGui.QAction(icon, _("&Preferences"), self)

        self.menu_edit.addAction(self.action_preferences)

        ####         view menu                                             ####

        self.action_show_toolbar = self.main_toolbar.toggleViewAction()
        self.action_show_toolbar.setText(_("Show &ToolBar"))

        self.action_show_statusbar = QtGui.QAction(_("Show Status&bar"), self)
        self.action_show_statusbar.setCheckable(True)
        self.action_show_statusbar.setChecked(True)

        self.action_toolbar_opt4 = QtGui.QAction(_("Default View"), self)
        self.action_toolbar_opt4.setData(QtCore.Qt.ToolButtonFollowStyle)

        self.action_toolbar_opt0 = QtGui.QAction(_("Icon Only"), self)
        self.action_toolbar_opt0.setData(QtCore.Qt.ToolButtonIconOnly)

        self.action_toolbar_opt1 = QtGui.QAction(_("Text Only"), self)
        self.action_toolbar_opt1.setData(QtCore.Qt.ToolButtonTextOnly)

        self.action_toolbar_opt2 = QtGui.QAction(_("Text Beside Icon"), self)
        self.action_toolbar_opt2.setData(QtCore.Qt.ToolButtonTextBesideIcon)

        self.action_toolbar_opt3 = QtGui.QAction(_("Text Under Icon"), self)
        self.action_toolbar_opt3.setData(QtCore.Qt.ToolButtonTextUnderIcon)

        icon = QtGui.QIcon.fromTheme("view-fullscreen")
        self.action_fullscreen = QtGui.QAction(icon,
            _("FullScreen Mode"), self)
        self.action_fullscreen.setCheckable(True)
        self.action_fullscreen.setShortcut("f11")

        self.menu_view.addAction(self.action_show_toolbar)
        self.menu_view.addAction(self.action_show_statusbar)

        self.menu_view.addSeparator()
        #submenu2 - toolbar options is a child of view
        self.menu_toolbar = QtGui.QMenu(_("&Toolbar"), self)
        self.menu_view.addMenu(self.menu_toolbar)
        self.menu_toolbar.addAction(self.action_toolbar_opt4)
        self.menu_toolbar.addAction(self.action_toolbar_opt0)
        self.menu_toolbar.addAction(self.action_toolbar_opt1)
        self.menu_toolbar.addAction(self.action_toolbar_opt2)
        self.menu_toolbar.addAction(self.action_toolbar_opt3)

        self.menu_view.addSeparator()
        self.menu_view.addAction(self.action_fullscreen)

        ####         about menu                                            ####

        icon = QtGui.QIcon.fromTheme("help-about")
        self.action_about = QtGui.QAction(icon, _("About"), self)

        self.action_about_qt = QtGui.QAction(icon, _("About Qt"), self)

        self.action_license = QtGui.QAction(icon, _("License"), self)

        icon = QtGui.QIcon.fromTheme("help", QtGui.QIcon("icons/help.png"))
        self.action_help = QtGui.QAction(icon, _("Help"), self)

        self.menu_help.addAction(self.action_about)
        self.menu_help.addAction(self.action_license)
        self.menu_help.addAction(self.action_about_qt)
        self.menu_help.addSeparator()
        self.menu_help.addAction(self.action_help)

        ####         toolbar                                               ####
        ####         add selected menu items to the toolbar                ####

        self.main_toolbar.addAction(self.action_help)

        self.connect_default_signals()

    def connect_default_signals(self):
        self.connect(self.action_quit, QtCore.SIGNAL("triggered()"),
        QtGui.QApplication.instance().closeAllWindows)

        self.action_preferences.triggered.connect(self.show_preferences_dialog)
        self.action_show_toolbar.triggered.connect(self.show_toolbar)
        self.action_show_statusbar.triggered.connect(self.show_statusbar)
        self.action_fullscreen.triggered.connect(self.fullscreen)

        for action in (self.action_toolbar_opt4, self.action_toolbar_opt3,
        self.action_toolbar_opt2, self.action_toolbar_opt1,
        self.action_toolbar_opt0):
            action.triggered.connect(self.toolbarButtonType)

        self.action_fullscreen.triggered.connect(self.fullscreen)
        self.action_about.triggered.connect(self.show_about)
        self.action_license.triggered.connect(self.show_license)

        self.connect(self.action_about_qt, QtCore.SIGNAL("triggered()"),
            QtGui.qApp, QtCore.SLOT("aboutQt()"))

        self.action_help.triggered.connect(self.show_help)

    def resizeEvent(self, event):
        self.setBriefMessageLocation()

    def setBriefMessageLocation(self):
        '''
        make the Advisor sub class aware of the windows geometry.
        set it top right, and right_to_left
        '''
        widg = self.menubar
        brief_pos_x = (widg.pos().x() + widg.width())
        brief_pos_y = (widg.pos().y() + widg.height())

        brief_pos = QtCore.QPoint(brief_pos_x, brief_pos_y)
        self.setBriefMessagePosition(brief_pos, True)

    def insertMenu_(self, menu):
        '''
        a convenience function that slots new actions in just before the
        "help" menu item on the menubar
        '''
        insertpoint = self.menu_help.menuAction()
        return self.menubar.insertMenu(insertpoint, menu)

    def insertToolBarWidget(self, action, sep=False):
        '''
        a convenience function that slots new widgets in just before the
        "help" menu item on the main Toolbar.
        accepts either a QAction, or a widget.
        If option 2nd argument (sep) is True, a separator is also added.
        '''
        added = []
        insertpoint = self.action_help
        if sep:
            insertpoint = self.main_toolbar.insertSeparator(insertpoint)
            added.append(insertpoint)
        if type(action) == QtGui.QAction:
            added.append(self.main_toolbar.insertAction(insertpoint, action))
        else:
            added.append(self.main_toolbar.insertWidget(insertpoint, action))
        return added

    def loadSettings(self):
        settings = QtCore.QSettings()
        #Qt settings
        self.restoreGeometry(settings.value("geometry").toByteArray())
        self.restoreState(settings.value("windowState").toByteArray())
        statusbar_hidden = settings.value("statusbar_hidden").toBool()
        self.statusbar.setVisible(not statusbar_hidden)
        self.action_show_statusbar.setChecked(not self.statusbar.isHidden())

        font = settings.value("Font").toPyObject()
        if font:
            QtGui.QApplication.instance().setFont(font)
        toolbar = settings.value("Toolbar", QtCore.Qt.ToolButtonTextUnderIcon)
        self.main_toolbar.setToolButtonStyle(toolbar.toInt()[0])
        tiny_menu = settings.value("TinyMenu").toBool()
        if tiny_menu:
            self.menubar.toggle_visability(True)
            self.menubar.toggleViewAction.setChecked(True)

    def saveSettings(self):
        settings = QtCore.QSettings()
        #Qt settings
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("statusbar_hidden", self.statusbar.isHidden())
        settings.setValue("Font", self.font())
        settings.setValue("Toolbar", self.main_toolbar.toolButtonStyle())
        settings.setValue("TinyMenu", not self.menubar.isVisible())


    def show_toolbar(self):
        if self.action_show_toolbar.isChecked():
            self.main_toolbar.show()
        else:
            self.main_toolbar.hide()

    def show_statusbar(self):
        if self.action_show_statusbar.isChecked():
            self.statusbar.show()
        else:
            self.statusbar.hide()

    def toolbarButtonType(self):
        styleVariant = self.sender().data()
        style, result = styleVariant.toInt()
        self.main_toolbar.setToolButtonStyle(style)
        for widg in self.main_toolbar.children():
            if type(widg) == QtGui.QToolButton:
                widg.setToolButtonStyle(style)

    def reimplement_needed(self, func_name):
        QtGui.QMessageBox.information(self, "please re-implement",
        '''please overwrite function <b>'%s'</b><br />
        in any class which inherits from 'BaseMainWindow' '''% func_name)

    def show_preferences_dialog(self):
        self.reimplement_needed('show_preferences_dialog')

    def show_about(self):
        self.reimplement_needed('show_about')

    def show_help(self):
        self.reimplement_needed('show_help')

    def show_license(self):
        '''
        attempts to read and show the license text
        from file COPYRIGHT.txt in the apps directory
        on failure, gives a simple message box with link.
        '''
        message = '''
        GPLv3 - see <a href='http://www.gnu.org/licenses/gpl.html'>
        http://www.gnu.org/licenses/gpl.html</a>'''
        try:
            f = open("../COPYING.txt")
            data = f.read()
            f.close()

            dl = QtGui.QDialog(self)
            dl.setWindowTitle(_("License"))
            dl.setFixedSize(400, 400)

            layout = QtGui.QVBoxLayout(dl)

            buttonBox = QtGui.QDialogButtonBox(dl)
            buttonBox.setOrientation(QtCore.Qt.Horizontal)
            buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)

            te = QtGui.QTextBrowser()
            te.setText(data)

            label = QtGui.QLabel(message)
            label.setWordWrap(True)

            layout.addWidget(te)
            layout.addWidget(label)
            layout.addWidget(buttonBox)

            buttonBox.accepted.connect(dl.accept)

            dl.exec_()
        except IOError:
            QtGui.QMessageBox.information(self, _("License"), message)

    def fullscreen(self):
        if self.action_fullscreen.isChecked():
            self.setWindowState(QtCore.Qt.WindowFullScreen)
        else:
            self.setWindowState(QtCore.Qt.WindowNoState)

    def closeEvent(self, event=None):
        '''
        re-implement the close event of QtGui.QMainWindow, and check the user
        really meant to do this.
        '''
        if QtGui.QMessageBox.question(self, _("Confirm"),
        _("Quit Application?"),
        QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
        QtGui.QMessageBox.Yes) == QtGui.QMessageBox.No:
            event.ignore()
        else:
            self.saveSettings()


if __name__ == "__main__":
    import gettext
    gettext.install("")

    app = QtGui.QApplication([])
    mw = BaseMainWindow()
    mw.show()
    app.exec_()