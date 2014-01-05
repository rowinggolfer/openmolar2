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

from server_function_dialog import ServerFunctionDialog
from lib_openmolar.common.connect.proxy_client import ProxyClient

SUPERUSERS = ("openmolar", "postgres")

class DropPGUserDialog(ServerFunctionDialog):

    def __init__(self, proxy_client, parent=None):
        ServerFunctionDialog.__init__(self, None, proxy_client, parent)

        header = _("Drop Postgres Users")

        self.setWindowTitle(header)

        header_label = QtGui.QLabel("<b>%s</b>"% header)
        header_label.setWordWrap(True)
        header_label.setAlignment(QtCore.Qt.AlignCenter)

        label = QtGui.QLabel(u"<em>%s?</em>"%
            _("Which user do you wish to remove"))
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.insertWidget(header_label)
        self.insertWidget(label)

        frame = QtGui.QFrame()
        self.insertWidget(frame)
        self.set_advanced_but_text(_("Help"))
        #self.add_advanced_widget()

        self.privileged_cbs = {}
        self.standard_cbs = {}

        for user in self.proxy_client.get_pg_user_list():
            if user in SUPERUSERS:
                continue
            but = QtGui.QPushButton(user)
            self.insertWidget(but)
            but.clicked.connect(self.but_clicked)

        advanced_label = QtGui.QLabel("no advanced features available")

        self.add_advanced_widget(advanced_label)

        self.cancel_but.setText(_("Close"))
        self.apply_but.hide()

    def but_clicked(self):
        but = self.sender()
        user = unicode(but.text())
        if QtGui.QMessageBox.question(self, _("Confirm"),
            u"%s '%s'?"% (_("Remove user"), user),
            QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
            QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Cancel:
            return

        attempting = True
        result = None
        while attempting:
            try:
                self.waiting.emit(True)
                result = self.proxy_client.call("drop_user", user)
                attempting = False
            except ProxyClient.PermissionError:
                LOGGER.info("user '%s' can not drop a postgres user"%
                    self.proxy_client.user.name)
                self.waiting.emit(False)
                attempting = self.switch_to_admin_user()
            finally:
                self.waiting.emit(False)
        if result is not None:
            if result.payload == True:
                message = u"%s '%s'"% (_("Successfully removed user"), user)
                mess_func = QtGui.QMessageBox.information
            else:
                message = u"%s '%s'<hr />%s"% (
                    _("Unable to remove user"), user,
                    _("For information, please check the server log")
                    )
                mess_func = QtGui.QMessageBox.warning

            mess_func(self, _("Result"), message)

            LOGGER.info(message)
        ServerFunctionDialog.accept(self)
        self.function_completed.emit()

def _test():
    app = QtGui.QApplication([])
    from lib_openmolar.common.connect.proxy_client import _test_instance
    proxy_client = _test_instance()
    dl = DropPGUserDialog(proxy_client)

    result = dl.exec_()

if __name__ == "__main__":
    import lib_openmolar.admin # set up LOGGER
    from gettext import gettext as _
    _test()
