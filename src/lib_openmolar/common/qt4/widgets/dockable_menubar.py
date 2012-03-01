#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011, Neil Wallace <rowinggolfer@googlemail.com>               ##
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
A simple application with a shrinkable menu bar.
(similar functionality to firefox)

At any point either the tiny menu or menubar should be visible.
Therefore if the toolbar is hidden, the menu will re-appear.

to experience this... either

    click View -> Tiny Menu
    or use the keyboard shortcut "ctrl M"
'''

import logging
from PyQt4 import QtGui, QtCore

class _DockableToolButton(QtGui.QToolButton):
    '''
    A toolbutton which acts nicely with a toolbar.
    '''
    def __init__(self, parent=None):
        QtGui.QToolButton.__init__(self, parent)
        try:
            icon = self.parent().windowIcon()
        except AttributeError:
            logging.debug("using fallback icon for tiny menu")
            icon = QtGui.QIcon.fromTheme("go-down")
        self.setIcon(icon)
        self.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.setText(_("Menu"))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)

class _MenuToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        QtGui.QToolBar.__init__(self, parent)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.setObjectName("_MenuToolbar") #for QSettings

        # this should happen by default IMO.
        self.toggleViewAction().setText(_("TinyMenu"))
        self.toggleViewAction().setShortcut('ctrl+M')
        #self.toggleViewAction().toggled.connect(self.clear_mini_menu)
        self._menu_button = None
        self.hide()

    def add_mini_menu(self, menu_button):
        if not self._menu_button is None:
            self.clear_mini_menu(True)
        self._menu_button = menu_button
        if self.actions():
            self.insertWidget(self.actions()[0], menu_button)
        else:
            self.addWidget(menu_button)
        self.show()

    def clear_mini_menu(self, clear=False):
        '''
        by default this does nothing,
        if called by a positive action (only possible if the menu is already
        initiated) then the menu is cleared and hidden
        '''
        if clear:
            self._menu_button.hide()
            self._menu_button.setParent(None)
            self._menu_button.deleteLater()
            self._menu_button = None
            self.hide()

class DockableMenuBar(QtGui.QMenuBar):
    '''
    inherits from QMenuBar, adding the functionality to become a
    standalone widget (thus saving screen estate)
    '''
    def __init__(self, parent):
        QtGui.QMenuBar.__init__(self, parent)
        self._menu_button = None
        #: the toolbar for the mini menu
        self.menu_toolbar = _MenuToolBar(parent)
        self.parent().addToolBar(self.menu_toolbar)

        self.menu_toolbar.toggleViewAction().triggered.connect(
            self.toggle_visability)

        #:
        self.menu_view = QtGui.QMenu(_("&View"), self)
        self.addMenu(self.menu_view)
        self.menu_view.addAction(self.menu_toolbar.toggleViewAction())
        self.menu_view.addSeparator()
        #:
        self.toolbar_menu = QtGui.QMenu(_("&Toolbars"), self)
        self.menu_view.addMenu(self.toolbar_menu)
        #:
        self.toolbar_options_menu = QtGui.QMenu(_("&Options"), self)
        self._populate_toolbar_options()
        self.toolbar_menu.addMenu(self.toolbar_options_menu)

        self.update_toolbars()

    def _populate_toolbar_options(self):

        action_toolbar_opt4 = QtGui.QAction(_("Default View"), self)
        action_toolbar_opt4.setData(QtCore.Qt.ToolButtonFollowStyle)

        action_toolbar_opt0 = QtGui.QAction(_("Icon Only"), self)
        action_toolbar_opt0.setData(QtCore.Qt.ToolButtonIconOnly)

        action_toolbar_opt1 = QtGui.QAction(_("Text Only"), self)
        action_toolbar_opt1.setData(QtCore.Qt.ToolButtonTextOnly)

        action_toolbar_opt2 = QtGui.QAction(_("Text Beside Icon"), self)
        action_toolbar_opt2.setData(QtCore.Qt.ToolButtonTextBesideIcon)

        action_toolbar_opt3 = QtGui.QAction(_("Text Under Icon"), self)
        action_toolbar_opt3.setData(QtCore.Qt.ToolButtonTextUnderIcon)

        self.toolbar_options_menu.addAction(action_toolbar_opt4)
        self.toolbar_options_menu.addAction(action_toolbar_opt0)
        self.toolbar_options_menu.addAction(action_toolbar_opt1)
        self.toolbar_options_menu.addAction(action_toolbar_opt2)
        self.toolbar_options_menu.addAction(action_toolbar_opt3)

        for action in (action_toolbar_opt4, action_toolbar_opt3,
        action_toolbar_opt2, action_toolbar_opt1,
        action_toolbar_opt0):
            action.triggered.connect(self.toolbarButtonType)

    @property
    def menu_button(self):
        self._menu_button = _DockableToolButton(self.parent())
        self._menu_button.setMenu(self.mini_menu)
        return self._menu_button

    @property
    def mini_menu(self):
        self._mini_menu = QtGui.QMenu()
        for action in self.actions():
            self._mini_menu.addAction(action)
        return self._mini_menu

    def refresh_mini_menu(self):
        '''
        called when an item is added to the menuBar
        '''
        if self._menu_button:
            self._menu_button.setMenu(self.mini_menu)

    def addViewOption(self, action):
        '''
        add an action to the 'view' category of the menubar
        '''
        self.menu_view.addAction(action)
        self.refresh_mini_menu()

    def update_toolbars(self):
        '''
        updates the view menu for all the parent application's toolbars
        '''
        for toolbar in self.parent().toolbar_list:
            self.toolbar_menu.addAction(toolbar.toggleViewAction())
        self.refresh_mini_menu()

    def toolbarButtonType(self):
        '''
        change the appearance of the toolbars
        '''
        styleVariant = self.sender().data()
        style, result = styleVariant.toInt()
        for toolbar in self.known_toolbars():
            toolbar.setToolButtonStyle(style)
            for widg in toolbar.children():
                if type(widg) == QtGui.QToolButton:
                    widg.setToolButtonStyle(style)

    def addMenu(self, *args):
        try:
            retval = self.insertMenu(self.actions()[-1], *args)
        except IndexError:
            retval = QtGui.QMenuBar.addMenu(self, *args)

        self.refresh_mini_menu()
        return retval

    def addAction(self, *args):
        try:
            retval = self.insertAction(self.actions()[-1], *args)
        except IndexError:
            retval = QtGui.QMenuBar.addAction(self, *args)
        self.refresh_mini_menu()
        return retval

    def toggle_visability(self, set_visible):
        self.setVisible(not set_visible)
        self.menu_toolbar.setVisible(set_visible)
        if set_visible:
            self.menu_toolbar.add_mini_menu(self.menu_button)
        else:
            self.menu_toolbar.clear_mini_menu()

    def setNotVisible(self, menu_bar_visible):
        '''
        make sure that we don't end up with neither menu visible!
        '''
        if not menu_bar_visible:
            self.setVisible(True)
            self.toggleViewAction.setChecked(False)

def _test():
    class _TestMainWindow(QtGui.QMainWindow):
        def __init__(self, parent=None):
            QtGui.QMainWindow.__init__(self, parent)
            self.setWindowIcon(QtGui.QIcon.fromTheme("application-exit"))

            menu_bar = DockableMenuBar(self)
            self.setMenuBar(menu_bar)

            ## initiate instances of our classes

            self.toolbar1 = QtGui.QToolBar(self)
            self.toolbar1.toggleViewAction().setText("%s %s"% (_("&ToolBar"), 1))

            self.toolbar2 = QtGui.QToolBar(self)
            self.toolbar2.toggleViewAction().setText("%s %s"% (_("&ToolBar"), 2))

            self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar1)
            self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar2)

            menu_bar.update_toolbars()

            ## some arbitrary stuff to make the app more realistic
            file_action = QtGui.QAction("&File", self)
            self.menuBar().addAction(file_action)

            edit_action = QtGui.QAction("&Edit", self)
            self.menuBar().addAction(edit_action)

            help_icon = QtGui.QIcon.fromTheme("help")
            self.action_help = QtGui.QAction(help_icon, _("Help"), self)

            menu_help = QtGui.QMenu(_("&Help"), self)
            menu_help.addAction(self.action_help)
            self.menuBar().addMenu(menu_help)

            ## and a couple of extras for the toolbar
            icon = QtGui.QIcon.fromTheme("system-file-manager")
            random_action = QtGui.QAction(icon, "function", self)
            self.toolbar1.addAction(random_action)

            ## a typical web address widget
            address_widget = QtGui.QWidget()
            layout = QtGui.QHBoxLayout(address_widget)
            layout.setMargin(0)
            line_edit = QtGui.QLineEdit("http://google.com")
            go_but = QtGui.QPushButton("Go!")
            go_but.setFixedWidth(60)
            layout.addWidget(line_edit)
            layout.addWidget(go_but)
            self.toolbar1.addWidget(address_widget)

            ## and give the second toolbar some content
            self.toolbar2.addAction(self.action_help)

            ## set a central widget
            te = QtGui.QTextEdit()
            self.setCentralWidget(te)
            te.setText(__doc__)

        def sizeHint(self):
            return QtCore.QSize(400,400)

    app = QtGui.QApplication([])
    mw = _TestMainWindow()
    mw.show()
    app.exec_()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    import gettext
    gettext.install("")

    _test()