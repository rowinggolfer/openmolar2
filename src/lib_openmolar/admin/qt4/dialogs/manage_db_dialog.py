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


class ManageDatabaseDialog(ServerFunctionDialog):

    def __init__(self, dbname, proxy_client, parent=None):
        ServerFunctionDialog.__init__(self, dbname, proxy_client, parent)

        header = u"%s %s"% (_("Manage Database"), dbname)
        self.setWindowTitle(header)

        header_label = QtGui.QLabel("<b>%s</b>"% header)
        header_label.setAlignment(QtCore.Qt.AlignCenter)

        label = QtGui.QLabel("%s<br /><em>%s</em>"% (
            _('The following remote functions can be called.'),
            _('''Please note - some of these functions
            may take a long time to execute and give little feedback''')
            ))
        label.setWordWrap(True)

        self.insertWidget(header_label)
        self.insertWidget(label)


        for func, desc in self.proxy_client.get_management_functions():
            but = QtGui.QPushButton(desc)
            but.func_name = func
            self.insertWidget(but)
            but.clicked.connect(self.but_clicked)

        advanced_label = QtGui.QLabel("no advanced features available")

        self.add_advanced_widget(advanced_label)

        self.cancel_but.setText(_("Close"))
        self.apply_but.hide()

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def but_clicked(self):
        but = self.sender()

        warning = self.proxy_client.pre_execution_warning(but.func_name)
        if warning and not self.get_confirm(warning):
            return
        attempting = True
        result = None
        while attempting:
            try:
                self.waiting.emit(True)
                result = self.proxy_client.call(but.func_name, self.dbname)
                attempting = False
            except ProxyClient.PermissionError:
                LOGGER.info("user '%s' can not perform function '%s'"% (
                    self.proxy_client.user.name, but.func_name))
                self.waiting.emit(False)
                attempting = self.switch_to_admin_user()
            finally:
                self.waiting.emit(False)
        if result is not None:
            LOGGER.debug(result)
            QtGui.QMessageBox.information(self, "result",
                "%s"% result.payload)
        self.accept()
        self.function_completed.emit()

def _test():
    app = QtGui.QApplication([])
    from lib_openmolar.common.connect.proxy_client import _test_instance
    proxy_client = _test_instance()
    dl = ManageDatabaseDialog("openmolar_demo", proxy_client)
    result = True
    while result:
        result = dl.exec_()

if __name__ == "__main__":
    import lib_openmolar.admin # set up LOGGER
    from gettext import gettext as _
    _test()
