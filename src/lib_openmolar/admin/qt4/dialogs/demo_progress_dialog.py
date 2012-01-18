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

from lib_openmolar.common.qt4.dialogs import BaseDialog

class DialogThread(QtCore.QThread):
    def __init__(self, dialog):
        super(DialogThread, self).__init__(dialog)
        self.dialog = dialog

    def run(self):
        self.dialog.open()


class ProgressWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self)
        self.progress_bar = QtGui.QProgressBar()
        self.label = QtGui.QLabel()
        self.label.setMinimumWidth(150)

        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)

    def setText(self, text):
        self.label.setText(text)

class DemoProgressDialog(BaseDialog):
    def __init__(self, connection, ommisions, parent=None):
        BaseDialog.__init__(self, parent)

        self.connection = connection

        self.setWindowTitle(_("Progress"))
        label = QtGui.QLabel(_("Populating Tables with demo data"))
        self.insertWidget(label)

        frame = QtGui.QFrame()
        layout = QtGui.QVBoxLayout(frame)

        self.module_dict = {}
        for module in self.connection.admin_modules:
            if module in ommisions:
                continue
            #instanstiate a class to get some information about the table
            sg = module.SchemaGenerator()
            pw = ProgressWidget(self)
            pw.setText(sg.tablename)
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

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def connect_signals(self):
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
            success = success and progress_widget.progress_bar.value() == 100
        return success

    def progress(self, module, percentage):
        current_pb = self.module_dict[module].progress_bar
        current_pb.setValue(percentage)
        self.scroll_area.ensureWidgetVisible(current_pb)

if __name__ == "__main__":
    import time
    import gettext
    gettext.install("")

    class DuckLog(object):
        def log(self, *args):
            print args

    app = QtGui.QApplication([])

    from lib_openmolar.admin.connect import AdminConnection
    sc = AdminConnection()
    sc.connect()

    dl = DemoProgressDialog(sc, [])
    dl.exec_()