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

from lib_openmolar.admin.qt4.classes.browser import Browser

class KnownServerWidget(QtGui.QFrame):
    '''
    loads the 230 servers @ startup.
    shows status of each.
    (most users will never use more than one 230 server)
    '''
    _servers = []

    shortcut_clicked = QtCore.pyqtSignal(object)
    '''
    emits a signal containing a tuple
    (proxyclient, shortcut)
    '''

    server_changed = QtCore.pyqtSignal(object)
    '''
    emits a signal when the server number changes
    '''

    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)

        self.listWidget = QtGui.QListWidget()
        self.browser = Browser()

        splitter = QtGui.QSplitter(self)
        splitter.addWidget(self.listWidget)
        splitter.addWidget(self.browser)
        splitter.setSizes([100,300])

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(splitter)

        self.listWidget.currentRowChanged.connect(self._server_chosen)

        self.browser.shortcut_clicked.connect(self.browser_shortcut_clicked)

    def sizeHint(self):
        return QtCore.QSize(400,400)

    def clear(self):
        self._servers = []
        self.listWidget.clear()

    def add_proxy_client(self, proxy_client):
        '''
        add a :doc:`ProxyClient`
        '''
        self._servers.append(proxy_client)
        if proxy_client.is_connected:
            icon = QtGui.QIcon(":icons/openmolar-server.png")
        else:
            icon = QtGui.QIcon(":icons/database.png")

        item = QtGui.QListWidgetItem(icon, proxy_client.brief_name,
            self.listWidget)
        item.setToolTip(proxy_client.name)
        if self.listWidget.currentItem() is None:
            self.listWidget.setCurrentRow(0)

    def _server_chosen(self, row):
        try:
            pm = self._servers[row]
            self.browser.setHtml(pm.html)
        except IndexError:
            self.browser.setHtml("<h1>No proxy server chosen</h1>")
        self.server_changed.emit(row)

    @property
    def current_client(self):
        '''
        the active :doc:`ProxyClient`
        '''
        return self._servers[self.listWidget.currentRow()]

    def browser_shortcut_clicked(self, shortcut):
        '''
        pass on the signal from the browser, adding information
        '''
        self.shortcut_clicked.emit(shortcut)

def _test():
    class duck_client(object):
        def __init__(self, i):
            self.brief_name = "item %d"% i
            self.name = "test tool tip for client %d"% i
            self.html = "<h1>Client %d Works!</h1>"% i
            self.is_connected = False

    import gettext
    gettext.install("")

    app = QtGui.QApplication([])

    ksw = KnownServerWidget()

    ksw.add_proxy_client(duck_client(1))
    ksw.add_proxy_client(duck_client(2))

    mw = QtGui.QMainWindow()
    mw.setCentralWidget(ksw)

    mw.show()
    app.exec_()


if __name__ == "__main__":
    _test()
