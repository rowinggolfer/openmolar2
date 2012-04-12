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
from lib_openmolar.common.qt4.widgets import ProgressWidget

class ImportProgressDialog(BaseDialog):
    def __init__(self, functions, parent=None):
        BaseDialog.__init__(self, parent)

        self.setWindowTitle(_("Import"))
        label = QtGui.QLabel(_("Importing Data"))
        self.insertWidget(label)

        frame = QtGui.QFrame()
        layout = QtGui.QVBoxLayout(frame)

        self.progress_widgets = {}
        for att in functions:
            pw = ProgressWidget(self)
            pw.setText(att.__name__)
            layout.addWidget(pw)
            self.progress_widgets[att.__name__] = pw

        self.scroll_area = QtGui.QScrollArea(self)
        self.scroll_area.setWidget(frame)
        self.scroll_area.setWidgetResizable(True)
        self.insertWidget(self.scroll_area)

        self.apply_but.hide()
        self.dirty = False
        self.set_check_on_cancel(True)
        
        self.connect(QtCore.QCoreApplication.instance(), 
            QtCore.SIGNAL("Import Finished"), self.finished)
        
        self.connect(QtGui.QApplication.instance(),
            QtCore.SIGNAL("import progress"), self.progress)

    def sizeHint(self):
        return QtCore.QSize(350, 300)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)
    
    def finished(self):
        if self.successful_import:
            QtGui.QMessageBox.information(self, _("Success"),
                "Import finished")
            self.accept()
        else:
            QtGui.QMessageBox.warning(self, _("Error"),
                _("Some errors were encountered, please check the log"))
    
            self.apply_but.show()
            self.apply_but.setText(_("Finish"))
            self.enableApply()
            self.cancel_but.hide()

    @property
    def successful_import(self):
        success = True
        for progress_widget in self.progress_widgets.values():
            success = success and progress_widget.value() == 100
        return success
    
    def progress(self, att, percentage):
        current_pb = self.progress_widgets[att]
        current_pb.setValue(percentage)
        self.scroll_area.ensureWidgetVisible(current_pb)


if __name__ == "__main__":
    import gettext
    gettext.install("")

    app = QtGui.QApplication([])

    dl = ImportProgressDialog([ImportProgressDialog.progress])
    dl.exec_()