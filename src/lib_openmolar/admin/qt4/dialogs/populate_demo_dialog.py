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

from demo_progress_dialog import DemoProgressDialog

class _AdvancedPanel(QtGui.QWidget):
    def __init__(self, modules, parent = None):
        QtGui.QWidget.__init__(self, parent)
        label = QtGui.QLabel(_("Only Populate the following Tables"))
        check_master = QtGui.QCheckBox(_('check / uncheck all'))
        check_master.setChecked(True)
        check_master.toggled.connect(self.check_all)

        frame = QtGui.QFrame(self)
        f_layout = QtGui.QVBoxLayout(frame)
        self.module_dict = {}
        for module in modules:
            cb = QtGui.QCheckBox(module.TABLENAME)
            cb.setChecked(True)
            f_layout.addWidget(cb)
            self.module_dict[module] = cb

        scroll_area = QtGui.QScrollArea(self)
        scroll_area.setWidget(frame)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(scroll_area)
        layout.addWidget(check_master)

    def check_all(self, i):
        for cb in self.module_dict.values():
            cb.setChecked(i)

    @property
    def ommitted_modules(self):
        ommitted = []
        for module in self.module_dict.keys():
            cb = self.module_dict[module]
            if not cb.isChecked():
                ommitted.append(module)
        return ommitted

class PopulateDemoDialog(ExtendableDialog):
    def __init__(self, connection, parent=None):
        ExtendableDialog.__init__(self, parent)

        self.connection = connection

        self.setWindowTitle(_("Demo Generator"))

        label = QtGui.QLabel(u"%s <b>'%s'</b> %s?"% (
            _('Populate the current database'),
            self.connection.databaseName(),
            _('with a full set of demo data')))
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.insertWidget(label)

        self.adv_widg = _AdvancedPanel(self.connection.admin_modules, self)
        self.add_advanced_widget(self.adv_widg)

        self.work_thread = QtCore.QThread(self)
        self.work_thread.run = self.call_populate

        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(300, 100)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def exec_(self, check_first=True):
        if check_first and not ExtendableDialog.exec_(self):
            return (False, "")
        dbname = self.connection.databaseName()

        if QtGui.QMessageBox.warning(self.parent(), _("Populating Demo"),
        u"<b>%s '%s'</b><hr />%s"%(
_("continuing may corrupt/overwrite any existing data in the database named"),
        dbname, _("do you wish to continue?")),
        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Cancel:
            return ("", False)

        self.Advise(u"%s %s"% (_("Populating Database"), dbname))

        return self.populate_demo()

    def call_populate(self):
        '''
        creates a thread for the database population
        enabling user to remain informed of progress
        '''
        self.connection.populateDemo(self.ommisions)

    def populate_demo(self):
        '''
        adds the hogwarts dental practice to the demo
        '''
        self.ommisions = self.adv_widg.ommitted_modules

        self.work_thread.start()
        self.dirty = self.work_thread.isRunning()

        dl = DemoProgressDialog(self.connection, 
            self.ommisions, self.parent())
        
        if not dl.exec_():
            if self.work_thread.isRunning():
                LOGGER.error("you quitted!")
                self.work_thread.terminate()
                return False

        return True

if __name__ == "__main__":
    import gettext
    gettext.install("")

    class DuckLog(object):
        def log(self, *args):
            print args

    app = QtGui.QApplication([])

    from lib_openmolar.admin.connect import DemoAdminConnection
    sc = DemoAdminConnection()
    sc.connect()

    dl = PopulateDemoDialog(sc)

    print dl.exec_()
