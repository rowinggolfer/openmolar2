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

import re
from PyQt4 import QtCore, QtGui

from lib_openmolar.common.dialogs import BaseDialog, ExtendableDialog

CREATE_INSTRUCTIONS = '''<html>
EXAMPLE -
To create a database called 'openmolar_demo' with a user 'om_user'<br />
Please do the following<hr />
drop to a terminal and type the following
<pre>

~$ sudo su - postgres
~$ createdb openmolar_demo
~$ createuser -P om_user
Enter password for new role:
Enter it again:
Shall the new role be a superuser? (y/n) n
Shall the new role be allowed to create databases? (y/n) n
Shall the new role be allowed to create more new roles? (y/n) n

</pre>
<br />
(instructions valid for debian based distributions, for other server types,
please consult their documentation)
</html>
'''

class NoDatabaseDialog(BaseDialog):
    def __init__(self, parent=None):
        super(NoDatabaseDialog, self).__init__(parent)
        self.setWindowTitle(_("New Database"))

        label = QtGui.QLabel(CREATE_INSTRUCTIONS)
        self.insertWidget(label)

class NewDatabaseDialog(ExtendableDialog):
    def __init__(self, connection, log, parent=None):
        super(NewDatabaseDialog, self).__init__(parent)

        self.connection = connection
        self.log = log

        self.setWindowTitle(_("Install Schema"))

        label = QtGui.QLabel(_("Install ALL required openmolar tables and datatypes into the current database?"))
        label.setWordWrap(True)
        self.insertWidget(label)

        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(300, 200)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def exec_(self):
        if not ExtendableDialog.exec_(self):
            self.Advise(_("Action Cancelled"))
            return

        dbname = self.connection.databaseName()

        if self.connection.get_available_tables() != [] and (
        QtGui.QMessageBox.warning(self.parent(), _("Warning"),
        u"%s<hr /><b>%s '%s' %s</b><br />%s"%(
        _("POTENTIAL DATA LOSS WARNING"),
        _("database"), dbname, _("has existing tables"),
        _("do you wish to continue?")),
        QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
        QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Cancel):
            return ("", False)

        self.Advise(u"%s %s"% (_("Creating Database"), dbname))

        return (dbname, self.layout_schema())

    def layout_schema(self):
        '''
        will layout a schema DESTRUCTIVELY!!!
        '''
        dbname = self.connection.databaseName()

        self.Advise(u"%s %s"% (_("laying out schema for database"), dbname))

        result, message = self.connection.create_openmolar_tables(self.log)
        self.log(message)

        if not result:
            self.Advise(message, 2)
        else:
            self.Advise(message, 1)

        return result

if __name__ == "__main__":
    import gettext
    gettext.install("")

    class DuckLog(object):
        def log(self, *args):
            print args

    app = QtGui.QApplication([])

    from lib_openmolar.admin.connect import AdminConnection
    sc = AdminConnection()
    sc.connect()

    dl = NewDatabaseDialog(sc, DuckLog().log)

    print dl.exec_()

