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

import copy, sys
from PyQt4 import QtGui, QtCore
from lib_openmolar.common.dialogs import ExtendableDialog

class AdvancedWidget(QtGui.QTextEdit):
    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setStyleSheet("background-color: black; color: white")
        self.setFont(QtGui.QFont("courier"))

    def sizeHint(self):
        return QtCore.QSize(200,150)

    def setText(self, text):
        QtGui.QTextEdit.setText(self, u"%s\n\n%s"% (
        _("OpenMolar should be started with the following parameters"), text))

class ChoiceDialog(ExtendableDialog):
    def __init__(self, parser, parent=None):
        '''
        *args*
        parser (type = optparse.OptionParser.values)
        *kwds*
        parent (QObject or None)
        '''
        ExtendableDialog.__init__(self, parent, remove_stretch=False)

        self.sys_argv_init = sys.argv[:]

        self.setWindowTitle(_("OpenMolar2 Control Panel"))
        self.setMinimumSize(300, 200)
        message = _("Please supply some parameters for openmolar")

        label = QtGui.QLabel(message)
        label.setMinimumHeight(50)
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.insertWidget(label)

        i = -1
        for option in parser.option_list:
            i += 1
            if option.get_opt_string() == "--help":
                continue
            check_box = QtGui.QCheckBox(option.get_opt_string(), self)
            check_box.toggled.connect(self._check)
            if option.help:
                check_box.setToolTip(option.help)

            self.insertWidget(check_box)

        self.advanced_widget = AdvancedWidget()
        self.add_advanced_widget(self.advanced_widget)
        self.advanced_widget.setText(parser.format_help())

        self.set_advanced_but_text(_("command line options"))

    def sizeHint(self):
        return QtCore.QSize(400,300)

    def _check(self, value):
        '''
        if user has selected one or both guis.. enable the apply button
        '''
        cli_text = str(self.sender().text())
        if value:
            sys.argv.append(cli_text)
        else:
            sys.argv.remove(cli_text)

        self.enableApply(len(self.sys_argv_init) != len(sys.argv))


def main(parser):
    app = QtGui.QApplication(sys.argv)
    dl = ChoiceDialog(parser)
    if not dl.exec_():
        sys.argv = dl.sys_argv_init
    app.closeAllWindows()
    app = None

    return parser

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--admin")
    options, args = parser.parse_args()
    print main(parser)
