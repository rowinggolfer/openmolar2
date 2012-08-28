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

class ManagePGUsersDialog(ServerFunctionDialog):

    def __init__(self, dbname, proxy_client, parent=None):
        ServerFunctionDialog.__init__(self, dbname, proxy_client, parent)

        header = u"%s %s"% (_("Manage User Permissions for database"), dbname)

        self.setWindowTitle(header)

        header_label = QtGui.QLabel("<b>%s</b>"% header)
        header_label.setWordWrap(True)
        header_label.setAlignment(QtCore.Qt.AlignCenter)

        help_label = QtGui.QLabel(u"<p>%s</p><p>%s</p><hr /><em>%s</em>" % (
            _('The supported way of setting permissions is by adding '
            'a user to the one of the predefined permission groups.'),
            _('Check or Uncheck a box to allow this to happen.'),
            _('NOTE - superusers are a special case, and should NEVER be used '
            'as a database user by the openmolar applications.')
            ))
        help_label.setWordWrap(True)

        self.insertWidget(header_label)

        frame = QtGui.QFrame()
        self.insertWidget(frame)
        self.set_advanced_but_text(_("Help"))
        self.add_advanced_widget(help_label)

        self.privileged_cbs = {}
        self.standard_cbs = {}

        layout = QtGui.QGridLayout(frame)

        label = QtGui.QLabel(u"<b>%s</b>"% _("User"))
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label, 0, 0)

        label = QtGui.QLabel(u"<b>%s</b>"% _("Privilege Level"))
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label, 0, 1, 1, 2)

        label = QtGui.QLabel(u"<b>%s</b>"% _("Full"))
        label.setAlignment(QtCore.Qt.AlignRight)
        layout.addWidget(label, 1, 1)

        label = QtGui.QLabel(u"<b>%s</b>"% _("Standard"))
        label.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(label, 1, 2)


        self.users = self.proxy_client.get_pg_user_list()
        for i, user in enumerate(self.users):
            row = i+2

            label = QtGui.QLabel(user)
            label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
            layout.addWidget(label, row, 0)

            if user in SUPERUSERS:
                label.setEnabled(False)
                su_label = QtGui.QLabel("N/A - superuser")
                su_label.setAlignment(QtCore.Qt.AlignCenter)
                su_label.setEnabled(False)
                layout.addWidget(su_label, row, 1, 1, 2)
                continue

            perms = self.proxy_client.get_pg_user_perms(user, self.dbname)

            cb1 = QtGui.QCheckBox()
            cb1.setLayoutDirection(QtCore.Qt.RightToLeft)
            cb1.setChecked(perms.get("admin", False))
            self.privileged_cbs[user] = cb1

            cb2 = QtGui.QCheckBox()
            cb2.setChecked(perms.get("client", False))
            self.standard_cbs[user] = cb2

            layout.addWidget(cb1, row, 1)
            layout.addWidget(cb2, row, 2)

            cb1.toggled.connect(self._enable)
            cb2.toggled.connect(self._enable)

    def sizeHint(self):
        return QtCore.QSize(300,300)

    def _enable(self):
        self.enableApply(True)

    def accept(self):
        attempting = True
        result = None
        while attempting:
            try:
                self.waiting.emit(True)
                result = self.apply_changes()
                attempting = False
            except ProxyClient.PermissionError:
                LOGGER.info("user '%s' can not alter postgres groups"%
                    self.proxy_client.user.name)
                self.waiting.emit(False)
                attempting = self.switch_to_admin_user()
            finally:
                self.waiting.emit(False)
        if result is not None:
            LOGGER.debug(result)
            QtGui.QMessageBox.information(self, _("Result"),
                _("Changes Applied"))
        ServerFunctionDialog.accept(self)
        self.function_completed.emit()

    def apply_changes(self):
        for user in self.users:
            if user in SUPERUSERS:
                continue
            admin = self.privileged_cbs[user].isChecked()
            client = self.standard_cbs[user].isChecked()
            self.proxy_client.grant_pg_user_perms(
                user, self.dbname, admin, client)

        return True

def _test():
    app = QtGui.QApplication([])
    from lib_openmolar.common.connect.proxy_client import _test_instance
    proxy_client = _test_instance()
    dl = ManagePGUsersDialog("openmolar_demo", proxy_client)

    result = dl.exec_()

if __name__ == "__main__":
    import lib_openmolar.admin # set up LOGGER
    from gettext import gettext as _
    _test()
