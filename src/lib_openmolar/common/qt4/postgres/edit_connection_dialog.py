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

from PyQt4 import QtGui, QtCore

import logging
import os

from lib_openmolar.common.qt4.dialogs import ExtendableDialog
from lib_openmolar.common.datatypes import ConnectionData

class EditConnectionDialog(ExtendableDialog):
    def __init__(self, conn_data, parent=None):
        ExtendableDialog.__init__(self, parent)
        self.setWindowTitle(_("Edit connection"))

        self.location = conn_data.conf_file
        f = open(self.location)
        self.orig = f.read()
        f.close()
        self.text_edit = QtGui.QTextEdit()
        self.insertWidget(self.text_edit)
        self.text_edit.setText(self.orig)

        save_as_button = QtGui.QPushButton(_("Save&As"))
        save_as_button.clicked.connect(self.save_as)
        self.add_advanced_widget(save_as_button)

        self.set_accept_button_text(_("&Save"))
        self.set_check_on_cancel(True)

        self.text_edit.textChanged.connect(self._check)

    def sizeHint(self):
        return QtCore.QSize(400,400)

    @property
    def text(self):
        '''
        the current text
        '''
        return self.text_edit.document().toPlainText()

    @property
    def has_text_changed(self):
        '''
        boolean property to show if text has been altered.
        '''
        self.dirty = self.text != self.orig
        return self.dirty

    def _check(self):
        self.enableApply(self.has_text_changed)

    def accept(self):
        self.save()

    def save(self, location=None):
        '''
        save the connection file
        '''
        if location is not None:
            self.location = location
        try:
            logging.debug("saving connection file %s"% self.location)
            f = open(self.location, "w")
            f.write(self.text)
            f.close()
            self.orig = self.text
        except Exception as exc:
            logging.exception("error saving connection conffile")
            QtGui.QMessageBox.warning(self, _("error"),
            "%s<hr />%s"% (_("error saving file"), exc))
        self._check()

    def save_as(self):
        location = QtGui.QFileDialog().getSaveFileName(self,
            _("Please choose where to save this conf file"),
            os.path.dirname(self.location))
        self.save(location)

if __name__ == "__main__":
    class DuckCD(object):
        conf_file = "/etc/openmolar/client-connections/demo"

    import gettext
    gettext.install("openmolar")

    app = QtGui.QApplication([])

    dl = EditConnectionDialog(DuckCD())
    dl.exec_()


