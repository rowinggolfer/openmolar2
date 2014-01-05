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

import os
import shutil
from PyQt4 import QtCore, QtGui

from server_function_dialog import ServerFunctionDialog
from lib_openmolar.common.connect.proxy_client import ProxyClient

##TODO - this will need to be changed for windows.
TEMPLATE = "/usr/share/openmolar/templates/conf.sample"

class ConfigureDatabaseDialog(ServerFunctionDialog):

    def __init__(self, dbname, proxy_client, parent=None):
        ServerFunctionDialog.__init__(self, dbname, proxy_client, parent)

        header = u"%s %s"% (_("Configure Sessions for"), dbname)
        self.setWindowTitle(header)

        header_label = QtGui.QLabel("<b>%s</b>"% header)
        header_label.setAlignment(QtCore.Qt.AlignCenter)

        label = QtGui.QLabel(
            _("please check the following text, then save the file"))
        label.setWordWrap(True)

        self.insertWidget(header_label)
        self.insertWidget(label)

        try:
            f = open(TEMPLATE, "r")
            data = f.read()
            f.close()
        except Exception as exc:
            LOGGER.exception("error opening file")
            data = u"%s<pre>%s</pre>"% (
                _("couldn't open template file"), exc)

        self.text_edit = QtGui.QTextEdit()
        self.text_edit.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.text_edit.setFontFamily("Courier")
        self.text_edit.setText(data)

        self.insertWidget(self.text_edit)

        advanced_label = QtGui.QLabel("no advanced features available")

        self.add_advanced_widget(advanced_label)

        self.apply_but.setText("Save")
        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(600, 400)

    def accept(self):
        dest_dir = "%s"% SETTINGS.USER_CONNECTIONS_AVAILABLE_FOLDER
        
        filepath = unicode(QtGui.QFileDialog.getSaveFileName(self,
            directory=dest_dir, filter="conf"))
        if filepath:
            LOGGER.info("saving %s"% filepath)
            f = open(filepath, "w")
            f.write(self.text_edit.toPlainText())
            f.close()
            
            # make a symlink for the admin application
            linkpath = os.path.join(SETTINGS.CONNECTION_CONFDIRS[0], 
                    os.path.basename(filepath))
            
            LOGGER.info("making link %s"% linkpath)
                
            try:
                if os.path.exists(linkpath):
                    os.remove(linkpath)
                os.symlink(filepath, linkpath)
            except AttributeError:
                # for python2.7 on windows. os.symlink doesn't work.
                shutil.copyfile(filepath, linkpath)
            ServerFunctionDialog.accept(self)

def _test():
    app = QtGui.QApplication([])
    from lib_openmolar.common.connect.proxy_client import _test_instance
    proxy_client = _test_instance()
    dl = ConfigureDatabaseDialog("openmolar_demo", proxy_client)
    dl.exec_()

if __name__ == "__main__":
    import lib_openmolar.admin # set up LOGGER
    from gettext import gettext as _
    _test()
