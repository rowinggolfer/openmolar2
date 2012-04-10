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

from lib_openmolar.admin.data_import.importer import Importer


class ImportDialog(ExtendableDialog):
    
    importer = None
    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.setWindowTitle(_("Import Data Wizard"))

        self.label = QtGui.QLabel()
        self.label.setWordWrap(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.insertWidget(self.label)

        self.work_thread = QtCore.QThread(self)
        self.work_thread.run = self.start_import

        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(300, 100)

    def set_importer(self, importer):
        '''
        Set the importer (of type ..doc`Importer` )
        '''
        assert isinstance(importer, Importer)
        self.importer = importer

    def no_importer_message(self):
        return QtGui.QMessageBox.warning(self.parent(), _("error"),
        "No importer has been specified")

    def exec_(self):
        if self.importer is None:
            return self.no_importer_message()

        message = u"%s <b>'%s'</b> ?"% (
        _('Import data into the current database'),
        self.importer.om2_session.databaseName())
        self.label.setText(message)
        
        if not ExtendableDialog.exec_(self):
            return False
        return self.start_()
        
    def start_import(self):
        '''
        creates a thread for the database population
        enabling user to remain informed of progress
        '''
        LOGGER.debug("start importing now!!")
        self.importer.import_all()
        
    def start_(self):
        '''
        TODO
        '''
        self.work_thread.start()
        self.dirty = self.work_thread.isRunning()
        dl = ImportProgressDialog(self.importer, self.parent())
        if not dl.exec_():
            if self.work_thread.isRunning():
                LOGGER.error("you quitted!")
                self.work_thread.terminate()
                return False
        return True

def _test():
    app = QtGui.QApplication([])

    from lib_openmolar.admin.connect import DemoAdminConnection
    from lib_openmolar.admin.data_import.importer import Importer
    
    dc = DemoAdminConnection()
    dc.connect()
    im = Importer()
    im.set_session(dc)
    im.set_import_directory("/home/neil/adp_import")
    
    dl = ImportDialog()
    dl.set_importer(im)
    
    print dl.exec_()

if __name__ == "__main__":
    _test()