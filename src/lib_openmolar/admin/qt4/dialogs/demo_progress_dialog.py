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
from lib_openmolar.common.qt4.widgets import ProgressWidget

class DemoProgressDialog(BaseDialog):
    def __init__(self, connection, ommisions, parent=None):
        BaseDialog.__init__(self, parent)

        self.setWindowTitle(_("Progress"))
        label = QtGui.QLabel(_("Populating Tables with demo data"))
        self.insertWidget(label)

        frame = QtGui.QFrame()
        layout = QtGui.QVBoxLayout(frame)

        self.module_dict = {}
        for module in connection.admin_modules:
            if module in ommisions:
                continue
            pw = ProgressWidget(self)
            pw.setText(module.TABLENAME)
            layout.addWidget(pw)
            self.module_dict[module] = pw

        self.scroll_area = QtGui.QScrollArea(self)
        self.scroll_area.setWidget(frame)
        self.scroll_area.setWidgetResizable(True)
        self.insertWidget(self.scroll_area)

        self.apply_but.hide()
        self.dirty = True
        self.set_check_on_cancel(True)

        self.connect_signals()

    def sizeHint(self):
        return QtCore.QSize(350, 300)

    def connect_signals(self):
        LOGGER.debug("listening for signals from the application")
        self.connect(QtGui.QApplication.instance(),
            QtCore.SIGNAL("demo install complete"), self.finished)

        self.connect(QtGui.QApplication.instance(),
            QtCore.SIGNAL("demo progress"), self.progress)

    def finished(self):
        if self.successful_install:
            QtGui.QMessageBox.information(self, _("Success"),
                _("Demo Data Installed Sucessfully!"))
        else:
            QtGui.QMessageBox.warning(self, _("Error"),
                _("Some errors were encountered, please check the log"))

        self.accept()

    @property
    def successful_install(self):
        success = True
        for progress_widget in self.module_dict.values():
            success = success and progress_widget.value() == 100
        return success

    def progress(self, module, percentage):
        current_pb = self.module_dict[module]
        current_pb.setValue(percentage)
        self.scroll_area.ensureWidgetVisible(current_pb)

if __name__ == "__main__":
    import gettext
    gettext.install("")

    class DuckLog(object):
        def log(self, *args):
            print args

    app = QtGui.QApplication([])

    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()

    dl = DemoProgressDialog(sc, [])
    dl.exec_()
