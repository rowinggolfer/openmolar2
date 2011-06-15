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


from PyQt4 import QtSql
from PyQt4 import QtGui, QtCore

class ConnectionParamsDialog(QtGui.QDialog):
    def __init__(self, options, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle(_("Transfer connection parameters"))

        frame1 = QtGui.QFrame()
        layout = QtGui.QFormLayout(frame1)

        self.hostname_le = QtGui.QLineEdit()
        self.hostname_le.setText(options.hostname)

        self.port_le = QtGui.QLineEdit()
        self.port_le.setText(str(options.port))

        self.dbname_le = QtGui.QLineEdit()
        self.dbname_le.setText(options.dbname)

        self.username_le = QtGui.QLineEdit(options.username)

        self.password_le = QtGui.QLineEdit(options.password)
        self.password_le.setEchoMode(self.password_le.Password)

        layout.addRow(_("Host"), self.hostname_le)
        layout.addRow(_("Port"), self.port_le)
        layout.addRow(_("Database Name"), self.dbname_le)
        layout.addRow(_("Username"), self.username_le)
        layout.addRow(_("Password"), self.password_le)

        frame2 = QtGui.QFrame()
        layout = QtGui.QFormLayout(frame2)

        self.pg_hostname_le = QtGui.QLineEdit()
        self.pg_hostname_le.setText(options.pg_hostname)

        self.pg_port_le = QtGui.QLineEdit()
        self.pg_port_le.setText(str(options.pg_port))

        self.pg_dbname_le = QtGui.QLineEdit()
        self.pg_dbname_le.setText(options.pg_dbname)

        self.pg_username_le = QtGui.QLineEdit(options.pg_username)

        self.pg_password_le = QtGui.QLineEdit(options.pg_password)
        self.pg_password_le.setEchoMode(self.password_le.Password)

        layout.addRow(_("Host"), self.pg_hostname_le)
        layout.addRow(_("Port"), self.pg_port_le)
        layout.addRow(_("Database Name"), self.pg_dbname_le)
        layout.addRow(_("Username"), self.pg_username_le)
        layout.addRow(_("Password"), self.pg_password_le)


        layout = QtGui.QGridLayout(self)
        layout.addWidget(QtGui.QLabel("MYSQL source"), 0, 0)
        layout.addWidget(frame1,1,0)
        layout.addWidget(QtGui.QLabel("Postgres destination"), 0, 1)
        layout.addWidget(frame2,1,1)

        but_box = QtGui.QDialogButtonBox()
        ok_but = but_box.addButton(but_box.Ok)
        canc_but = but_box.addButton(but_box.Cancel)

        ok_but.clicked.connect(self.accept)
        canc_but.clicked.connect(self.reject)

        layout.addWidget(but_box,2,0,1,2)

    @property
    def hostname(self):
        return self.hostname_le.text()

    @property
    def port(self):
        return int(self.port_le.text())

    @property
    def dbname(self):
        return self.dbname_le.text()

    @property
    def username(self):
        return self.username_le.text()

    @property
    def password(self):
        return self.password_le.text()

    @property
    def pg_hostname(self):
        return self.pg_hostname_le.text()

    @property
    def pg_port(self):
        return int(self.pg_port_le.text())

    @property
    def pg_dbname(self):
        return self.pg_dbname_le.text()

    @property
    def pg_username(self):
        return self.pg_username_le.text()

    @property
    def pg_password(self):
        return self.pg_password_le.text()

class MySQLConnection(QtSql.QSqlDatabase):
    '''
    inherits from PyQt4.QSql.QSqlDatabase
    adds a function "connect", which opens the connection whilst
    using a qt wait cursor.
    Will Raise a Connection error if connection has not been established
    within 10 seconds
    '''
    def __init__(self, host="localhost", user="om_user", passwd="password",
    db_name="openmolar_demo", port=3306):
        super(MySQLConnection, self).__init__("QMYSQL")
        self.setHostName(host)
        self.setPort(port)
        self.setUserName(user)
        self.setPassword(passwd)
        self.setDatabaseName(db_name)

    def connect(self, *args):
        '''
        open the connection, raising an error if fails or timeouts
        optional arguments of (user, password)
        '''
        connection_in_progress = True
        def time_out():
            if connection_in_progress:
                self._wait_cursor(False)
                if not self.isOpen():
                    message = self.lastError().text()
                    self.close()
                    raise IOError("Time out Error %s"% message)

        QtCore.QTimer.singleShot(10000, time_out) ## 10 seconds.
        if args:
            user = args[0]
            password = args[1]
            connected = self.open(user, password)
        else:
            connected = self.open()
        connection_in_progress = False
        if not connected:
            raise IOError(
            "<pre font='courier'>%s</pre>"% self.lastError().text())

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")

    from collections import namedtuple
    duck = namedtuple("Duck", '''hostname, username, password, dbname, port,
        pg_hostname, pg_username, pg_password, pg_dbname, pg_port''')
    duck.hostname="localhost"
    duck.username="om_user"
    duck.password="password"
    duck.dbname="openmolar_demo"
    duck.port=3306

    duck.pg_hostname="localhost"
    duck.pg_username="om_user"
    duck.pg_password="password"
    duck.pg_dbname="openmolar_demo"
    duck.pg_port=5432

    app = QtGui.QApplication([])
    dl = ConnectionParamsDialog(duck)
    if dl.exec_():

        db = MySQLConnection(   host=dl.hostname,
                                user=dl.username,
                                passwd=dl.password,
                                db_name=dl.dbname,
                                port=dl.port)
        try:
            db.connect()
            message =  'connection Ok...'
            db.close()
        except IOError as e:
            message = u"connection error<hr />%s"% e

        QtGui.QMessageBox.information(dl, "result", message)

    app.closeAllWindows()
