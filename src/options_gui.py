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


class OptionWidget(QtGui.QWidget):
    def __init__(self, option, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.option = option

        if option.help:
            cb_text = option.help
        else:
            cb_text = self.long_opt

        self.check_box = QtGui.QCheckBox(cb_text, self)
        self.check_box.setChecked(
            self.short_opt in sys.argv or self.long_opt in sys.argv)

        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(self.check_box)

        self.toggled.connect(self.action)

    @property
    def toggled(self):
        return self.check_box.toggled

    @property
    def long_opt(self):
        try:
            return self.option._long_opts[0]
        except IndexError:
            return None
            
    @property
    def short_opt(self):
        try:
            return self.option._short_opts[0]
        except IndexError:
            return None
        
    def action(self, value):
        if value:
            if self.short_opt is not None:
                sys.argv.append(self.short_opt)
            else:
                sys.argv.append(self.long_opt)
        else:        
            for cli_text in (self.short_opt, self.long_opt):
                try:
                    sys.argv.remove(cli_text)
                except ValueError:
                    pass
        
class OptionsWidget(QtGui.QScrollArea):
    def __init__(self, parent=None):
        QtGui.QScrollArea.__init__(self, parent)

        self.options_frame = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(self.options_frame)
        layout.setMargin(0)
        layout.addStretch(0)

        self.setWidget(self.options_frame)
        self.setWidgetResizable(True)

    def add_widget(self, widget):
        self.options_frame.layout().insertWidget(0, widget)

    def sizeHint(self):
        return QtCore.QSize(200,150)

class ChoiceDialog(ExtendableDialog):
    def __init__(self, parser, parent=None):
        '''
        *args*
        parser (type = optparse.OptionParser.values)
        *kwds*
        parent (QObject or None)
        '''
        ExtendableDialog.__init__(self, parent, remove_stretch=False)

        self.parser = parser
        self.sys_argv_init = sys.argv[:]

        self.setWindowTitle(_("OpenMolar2 Control Panel"))
        self.setMinimumSize(300, 200)

        message = _("Openmolar should be started with parameters"
                    " "
                    "yet none were supplied."
                    "\n"
                    "This is why you are seeing this screen, which"
                    " ""is primarily intended for developer use only."
                    "\n\n"
                    "Please supply some parameters for openmolar.")
        button = QtGui.QPushButton(_("CLI useage"))

        label = QtGui.QLabel(message)
        label.setWordWrap(True)

        header = QtGui.QWidget()
        layout = QtGui.QHBoxLayout(header)
        layout.addWidget(label)
        layout.addWidget(button)


        standard_widg = OptionsWidget()
        advanced_widg = OptionsWidget()

        self.insertWidget(header)
        self.insertWidget(standard_widg)
        self.add_advanced_widget(advanced_widg)

        for option in parser.option_list:
            if option.get_opt_string() in ("--help", "--version"):
                continue

            option_widget = OptionWidget(option, self)

            parent = advanced_widg if option.ADVANCED else standard_widg
            parent.add_widget(option_widget)

            option_widget.toggled.connect(self._check)

        button.clicked.connect(self.show_cli_text)

    def sizeHint(self):
        return QtCore.QSize(400,300)

    def _check(self, value):
        '''
        if user has selected one or both guis.. enable the apply button
        '''
        self.enableApply(not self.parser.needs_more)

    def show_cli_text(self):
        message = self.parser.format_help()

        mb = QtGui.QMessageBox(self)
        mb.setWindowTitle(_("CLI useage"))
        mb.setFont(QtGui.QFont("courier"))
        mb.setInformativeText(message)
        mb.show()

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
    parser.needs_more = False
    option = parser.add_option("--admin")
    option.ADVANCED = False
    print main(parser)
