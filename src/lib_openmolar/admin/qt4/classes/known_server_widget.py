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


from PyQt4 import QtCore, QtGui

from lib_openmolar.common.qt4.dialogs import BaseDialog
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

        self.list_widget = QtGui.QListWidget()
        self.browser = Browser()

        label = QtGui.QLabel(
            _("The following OM Servers are configured for use."))
        label.setWordWrap(True)

        r_button = QtGui.QPushButton(_("Refresh"))
        r_button.setToolTip(
            _("Poll all configured OMServers for status and refresh the page"))

        h_button = QtGui.QPushButton(_("View Source"))
        h_button.setToolTip(_("view the html of shown page"))

        left_frame = QtGui.QFrame()
        left_layout = QtGui.QVBoxLayout(left_frame)
        left_layout.setMargin(0)
        left_layout.addWidget(label)
        left_layout.addWidget(self.list_widget)
        left_layout.addWidget(r_button)
        left_layout.addWidget(h_button)


        splitter = QtGui.QSplitter(self)
        splitter.addWidget(left_frame)
        splitter.addWidget(self.browser)
        splitter.setSizes([80,320])
        splitter.setObjectName("KnownServerWidgetSplitter")

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(splitter)

        r_button.clicked.connect(self.call_refresh)
        h_button.clicked.connect(self.view_html)

        self.list_widget.currentRowChanged.connect(self._server_chosen)

        self.browser.shortcut_clicked.connect(self.browser_shortcut_clicked)

    def sizeHint(self):
        return QtCore.QSize(400,400)

    def clear(self):
        self._servers = []
        self.list_widget.clear()

    def refresh(self):
        '''
        update the status of all the clients
        '''
        for i in range(self.list_widget.count()):
            proxy_client = self._servers[i]
            item = self.list_widget.item(i)
            item_text = proxy_client.brief_name
            if proxy_client.is_connected:
                icon = QtGui.QIcon(":icons/openmolar-server.png")
            else:
                icon = QtGui.QIcon(":icons/database.png")
                item_text += u" (%s)"% _("NOT CONNECTED")

            item.setIcon(icon)
            item.setText(item_text)
            item.setToolTip(proxy_client.name)

    def add_proxy_client(self, proxy_client):
        '''
        add a :doc:`ProxyClient`
        '''
        self._servers.append(proxy_client)

        item_text = proxy_client.brief_name

        item = QtGui.QListWidgetItem(item_text, self.list_widget)
        if self.list_widget.currentItem() is None:
            self.list_widget.setCurrentRow(0)
        self.refresh()

    def set_html(self, html):
        '''
        update the html on the embedded browser
        '''
        self.browser.setHtml(html)

    def view_html(self):
        '''
        view the displayed html in plain text
        '''
        html = self.browser.page().currentFrame().toHtml()
        text_browser = QtGui.QTextEdit()
        text_browser.setReadOnly(True)
        text_browser.setFont(QtGui.QFont("courier", 10))
        text_browser.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        text_browser.setPlainText(html)
        dl = BaseDialog(self, remove_stretch=True)
        dl.setWindowTitle("html source view")
        dl.insertWidget(text_browser)
        dl.setMinimumWidth(600)
        dl.cancel_but.hide()
        dl.set_accept_button_text(_("Ok"))
        dl.enableApply()
        dl.exec_()

    def _server_chosen(self, row):
        '''
        private function called by a gui interaction
        '''
        self.refresh()
        self.set_html("please wait....")
        try:
            pm = self._servers[row]
            self.set_html(pm.html)
        except IndexError:
            self.browser.setHtml("<h1>No proxy server chosen</h1>")
        self.server_changed.emit(row)

    def call_refresh(self):
        '''
        function called when the refresh button is clicked.
        '''
        self.refresh()
        row = self.list_widget.currentRow()
        self.server_changed.emit(row)

    @property
    def current_client(self):
        '''
        the active :doc:`ProxyClient`
        '''
        return self._servers[self.list_widget.currentRow()]

    def browser_shortcut_clicked(self, shortcut):
        '''
        pass on the signal from the browser, adding information
        '''
        self.shortcut_clicked.emit(shortcut)
        self.refresh()

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
