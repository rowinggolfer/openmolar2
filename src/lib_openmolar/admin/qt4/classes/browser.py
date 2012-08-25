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


from PyQt4 import QtCore, QtGui, QtWebKit

class _WebPage(QtWebKit.QWebPage):
    '''
    subclass Webpage so that links and forms are handled.
    '''
    def __init__(self, parent=None):
        QtWebKit.QWebPage.__init__(self, parent)
        self.setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)

    def acceptNavigationRequest(self, frame, request, type_):
        if type_==self.NavigationTypeFormSubmitted:
            self.linkClicked.emit(request.url())
        return QtWebKit.QWebPage.acceptNavigationRequest(
            self, frame, request, type_)

class Browser(QtWebKit.QWebView):
    '''
    A browser which is aware of some of the shortcuts offered by the server.
    '''
    shortcut_clicked = QtCore.pyqtSignal(object)
    
    css_link = False

    def __init__(self, parent=None):
        QtWebKit.QWebView.__init__(self, parent)
        
        self._page = _WebPage()
        self.setPage(self._page)
       
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.linkClicked.connect(self._link_clicked)
        try:
            QtCore.QUrl.isLocalFile
            css_url = QtCore.QUrl.fromLocalFile(SETTINGS.PROXY_CSS)            
            self.settings().setUserStyleSheetUrl(css_url)
        except AttributeError:
            #QUrl was handled differently in older pyqts (lucid)
            css_url = QtCore.QUrl("file://" + SETTINGS.PROXY_CSS)
            self.css_link = True
        
    def setHtml(self, html):
        # a hack so that lucid qt works...
        if self.css_link:
            html = html.replace("</head>",
            '''<link rel="stylesheet" type="text/css" 
            href="file://%s" rel="text/css" /> 
            </head>'''% SETTINGS.PROXY_CSS)

        QtWebKit.QWebView.setHtml(self, html)

    def _link_clicked(self, url):
        url_string = unicode(url.toString())
        LOGGER.info("link clicked - '%s'"% url_string)
        self.shortcut_clicked.emit(url_string)

if __name__ == "__main__":
    import lib_openmolar.admin # for LOGGER
    
    def sig_catcher(*args):
        print (args)

    app = QtGui.QApplication([])
    mw = QtGui.QMainWindow()
    mw.setMinimumSize(400,200)

    browser = Browser()
    browser.setHtml(
    '''<html><body>
        <div class='loc_header'><h3>Test Header</h3>
        </div>
        <a href='url.html'>test link</a>
        <form action="button_clicked.html" method="get">
            <button type="submit">test_button</button>
         </form>
        </body></html>''')

    browser.shortcut_clicked.connect(sig_catcher)

    mw.setCentralWidget(browser)

    mw.show()
    
    app.exec_()
