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
from lib_openmolar.admin.qt4.dialogs import ImportProgressDialog

class ImportDialog(ExtendableDialog):
    def __init__(self, pg_session, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.setWindowTitle(_("Import Data Wizard"))

        self.pg_session = pg_session
        SETTINGS.PLUGIN_DIRS = QtCore.QSettings().value("plugin_dirs").toStringList()
        SETTINGS.load_plugins()

        label = QtGui.QLabel(u"%s <b>'%s'</b> ?"% (
            _('Import data into the current database'),
            self.pg_session.databaseName()))
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.insertWidget(label)

        for dir_ in self.plugin_dirs:
            cb = QtGui.QCheckBox(dir_)
            self.insertWidget(cb)

        self.work_thread = QtCore.QThread(self)
        self.work_thread.run = self.start_import

        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(300, 100)

    @property
    def plugin_dirs(self):
        settings = QtCore.QSettings()
        dirs = settings.value("plugin_dirs").toStringList()
        return dirs

    def exec_(self):
        if not ExtendableDialog.exec_(self):
            return False
        return self.start_()

    def start_import(self):
        '''
        creates a thread for the database population
        enabling user to remain informed of progress
        '''
        print "start importing now!!"

    def start_(self):
        '''
        TODO
        '''
        self.work_thread.start()
        self.dirty = self.work_thread.isRunning()
        dl = ImportProgressDialog(self.pg_session, self.parent())
        if not dl.exec_():
            if self.work_thread.isRunning():
                LOGGER.error("you quitted!")
                self.work_thread.terminate()
                return False
        return True

def _test():
    app = QtGui.QApplication([])

    settings = QtCore.QSettings()
    settings.setValue("plugin_dirs",
        ["/etc/openmolar/plugins",
        "/home/neil/openmolar/hg_openmolar/plugins/admin"])

    from lib_openmolar.admin.connect import DemoAdminConnection
    dc = DemoAdminConnection()
    dc.connect()

    dl = ImportDialog(dc)

    print dl.exec_()

if __name__ == "__main__":
    _test()