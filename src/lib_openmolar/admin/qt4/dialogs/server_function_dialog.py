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

from lib_openmolar.common.qt4.dialogs import ExtendableDialog
from lib_openmolar.common.qt4.dialogs import UserPasswordDialog
from lib_openmolar.common.connect.proxy_user import ProxyUser
from lib_openmolar.common.connect.proxy_client import ProxyClient


class ServerFunctionDialog(ExtendableDialog):

    waiting = QtCore.pyqtSignal(object)
    function_completed = QtCore.pyqtSignal()

    def __init__(self, dbname, proxy_client, parent=None):
        ExtendableDialog.__init__(self, parent)

        self.dbname = dbname
        self.proxy_client = proxy_client

    def switch_to_admin_user(self):
        '''
        try and elevate to admin user of the proxy-server
        '''
        LOGGER.debug("switch_to_admin_user called")
        QtGui.QMessageBox.information(self, _("info"),
            _("only the admin user can perform this function")
            )
        dl = UserPasswordDialog(self)
        dl.set_label_text(
    _("Please enter the password for the admin user of this OpenMolar Server"))
        dl.set_name("admin")

        result = False

        while not result:
            if not dl.exec_():
                break

            user = ProxyUser(dl.name, dl.password)
            self.proxy_client.set_user(user)
            try:
                if self.proxy_client.server is not None:
                    result = True
                    break
            except ProxyClient.ConnectionError:
                pass

            self.proxy_client.use_default_user()
            QtGui.QMessageBox.warning(self, _("error"),
               u"%s '%s'"% (_("no connection established for user"), dl.name))

        return result

def _test():
    app = QtGui.QApplication([])
    from lib_openmolar.common.connect.proxy_client import _test_instance
    proxy_client = _test_instance()
    dl = ServerFunctionDialog("openmolar_demo", proxy_client)
    dl.switch_to_admin_user()

if __name__ == "__main__":
    import lib_openmolar.admin # set up LOGGER
    from gettext import gettext as _
    _test()
