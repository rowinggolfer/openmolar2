#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2012, Neil Wallace <neil@openmolar.com>                        ##
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

from PyQt4 import QtGui, QtCore, QtNetwork, QtWebKit

class OnlinePluginsWidget(QtGui.QFrame):
    '''
    a widget capable of ssl connection to plugins.openmolar.com
    '''
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)

        self.webview = QtWebKit.QWebView()

        network_access_manager = QtNetwork.QNetworkAccessManager(self)
        network_access_manager.sslErrors.connect(self.ssl_errors)

        f = open("/home/neil/www/certificates/openmolar.com.cert", "rb")
        data = f.read()
        f.close()

        certificate = QtNetwork.QSslCertificate(data)

        self.config = QtNetwork.QSslConfiguration()
        self.config.setCaCertificates([certificate])
        self.config.setProtocol(QtNetwork.QSsl.AnyProtocol)

        webpage = self.webview.page()
        webpage.setLinkDelegationPolicy(webpage.DelegateAllLinks)
        webpage.setNetworkAccessManager(network_access_manager)

        icon1 = QtGui.QIcon.fromTheme("applications-internet",
            QtGui.QIcon(":icons/applications-internet.png"))

        url = "https://www.openmolar.com/plugins/index.html"
        #url = "http://www.openmolar.com/plugins/index.html"
        label = QtGui.QLabel("Connecting to %s"% url)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.webview)
        layout.addWidget(label)

        self.network_request = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        self.network_request.setSslConfiguration(self.config)

        QtCore.QTimer.singleShot(0, self._load)

    def sizeHint(self):
        return QtCore.QSize(520,400)

    def _load(self):
        self.webview.load(self.network_request)

    def format_cert_info(self, cert):
        html = ""
        html += "<li>%s</li>"% cert.subjectInfo(cert.CommonName)
        html += "<ul><li>%s</li>"% cert.issuerInfo(cert.CommonName)
        html += "<li>START   %s</li>"% cert.effectiveDate().toString()
        html += "<li>EXPIRES %s</li></ul>"% cert.expiryDate().toString()
        return html

    def ssl_errors(self, reply, errors):
        remote_cert = reply.sslConfiguration().peerCertificate()

        for cert in self.config.caCertificates():
            if cert == remote_cert:
                reply.ignoreSslErrors()
                return

        message = "<b>SSL Errors</b><ul>"
        for error in errors:
            message += "<li>%s</li>"% error.errorString()
        message += "</ul><hr /><b>Ignore warnings?</b>"

        if QtGui.QMessageBox.warning(self, "ssl error", message,
        QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Ok) == QtGui.QMessageBox.Ok:
            reply.ignoreSslErrors()
        else:
            message = "<b>SSL Errors</b><ul>"
            for error in errors:
                message += self.format_cert_info(error.certificate())

            self.webview.setHtml("%s</ul>"% message)

def _test():

    app = QtGui.QApplication([])
    mw = QtGui.QMainWindow()
    w = OnlinePluginsWidget()
    mw.setCentralWidget(w)
    mw.show()
    app.exec_()

if __name__ == "__main__":
    _test()