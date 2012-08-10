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

from lib_openmolar.common.qt4.dialogs import ExtendableDialog
from lib_openmolar.common.connect.proxy_client import ProxyClient

class ManageDatabaseDialog(ExtendableDialog):

    def __init__(self, dbname, proxy_client, parent=None):
        ExtendableDialog.__init__(self, parent)

        self.dbname = dbname
        self.proxy_client = proxy_client
        
        header = u"%s %s"% (_("Manage Database"), dbname)
        self.setWindowTitle(header)

        header_label = QtGui.QLabel("<b>%s</b>"% header)
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
        result = "Failed"
        if not self.get_confirm( 
            "You have selected '%s' this will perform function %s"% (
            but.text(), but.func_name)):
            return
        attempting = True
        while attempting:
            try:
                result = self.proxy_client.call(but.func_name, self.dbname)
            except ProxyClient.PermissionError:
                LOGGER.info("need to raise permissions")
                attempting = not self.parent().switch_server_user()
        LOGGER.debug(result)

    def drop_but_clicked(self):
        if self.get_confirm(u"%s '%s'?<br /><b>%s</b>"% (_("Drop Database"),
        self.dbname, _("This operation cannot be undone!"))):
            self.drop_db = True
            self.accept()

    def users_but_clicked(self):
        self.manage_users = True
        self.accept()

    def truncate_but_clicked(self):
        if self.get_confirm(u"%s '%s'?<br /><b>%s</b>"% (
        _("Remove all data from"),
        self.dbname, _("This operation cannot be undone!"))):
            self.truncate_db = True
            self.accept()

def _test():
    app = QtGui.QApplication([])
    from lib_openmolar.common.connect.proxy_client import _test_instance
    proxy_client = _test_instance()
    dl = ManageDatabaseDialog("openmolar_demo", proxy_client)
    result = True
    while result:
        try:
            result = dl.exec_()
        except ProxyClient.PermissionError:
            print "raise permissions"
            
if __name__ == "__main__":
    import lib_openmolar.admin # set up LOGGER
    from gettext import gettext as _
    _test()
