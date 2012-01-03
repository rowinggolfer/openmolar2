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

'''
provides 2 classes.
ConnectionError - a custom python exception, raised if connection times out
DatabaseConnection - a custom class inheriting from Pyqt4.QSql.QSqlDatabase
'''
import logging

from PyQt4 import QtSql
from PyQt4 import QtGui, QtCore

class ConnectionError(Exception):
    '''
    a custom Exception
    '''
    pass

class DatabaseConnection(QtSql.QSqlDatabase):
    '''
    inherits from PyQt4.QSql.QSqlDatabase
    adds a function "connect", which opens the connection whilst
    using a qt wait cursor.
    Will Raise a Connection error if connection has not been established
    within 10 seconds
    '''
    def __init__(self, host="127.0.0.1", user="om_demo", passwd="password",
    db_name="openmolar_demo", port=5432, options="requiressl=1",
    connect_timeout=10):
        super(DatabaseConnection, self).__init__("QPSQL")
        self.setHostName(host)
        self.setPort(port)
        self.setConnectOptions(options)
        self.setUserName(user)
        self.setPassword(passwd)
        self.setDatabaseName(db_name)

        self.driver().notification.connect(self.notification_received)

    def from_connection_data(self, cd):
        '''
        load the connection from a connection_data object
        '''
        logging.debug("loading connection params from connection data object")
        self.setHostName(cd.host)
        self.setPort(cd.port)
        self.setUserName(cd.username)
        self.setPassword(cd.password)
        self.setDatabaseName(cd.db_name)

    def _wait_cursor(self, waiting=False):
        '''
        provides/removes a WaitCursor during connection and parsing functions
        '''
        app_instance = QtGui.QApplication.instance()
        if not app_instance: # could be the case if non-gui connection
            pass
        elif waiting:
            app_instance.setOverrideCursor(QtCore.Qt.WaitCursor)
        else:
            app_instance.restoreOverrideCursor()

    def connect(self, *args):
        '''
        open the connection, raising an error if fails or timeouts
        optional arguments of (user, password)
        '''
        logging.debug("connecting")
        self._wait_cursor()
        connection_in_progress = True
        def time_out():
            logging.debug("time out")
            if connection_in_progress:
                self._wait_cursor(False)
                if not self.isOpen():
                    message = self.lastError().text()
                    self.close()
                    raise ConnectionError("Time out Error %s"% message)

        logging.debug("setting timeout to 10 seconds")
        QtCore.QTimer.singleShot(1000, time_out) ## 10 seconds.
        logging.debug("timer set")
        if args:
            user = args[0]
            password = args[1]
            logging.debug("connecting with user '%s', password '%s'"% (
                user, "*"* len(password)))
            connected = self.open(user, password)
        else:
            logging.debug("connecting with default params")
            connected = self.open()
        logging.debug("connected??")
        connection_in_progress = False
        self._wait_cursor(False)
        if not connected:
            raise ConnectionError(
            "<pre font='courier'>%s</pre>"% self.lastError().text())
        else:
            self.subscribeToNotifications()

    def subscribeToNotifications(self):
        '''
        this should be overwritten when this connection is implemented
        postgres can emit signals when the database is changed by another
        client.
        the query is simple
        NOTIFY new_appointment_made
        '''
        print "re-implement DatabaseConnection.subscribeToNotifications"
        #self.driver().subscribeToNotification("new_appointment_made")

    def notification_received(self, notification):
        '''
        the database has emitted a notify signal with text notification
        that we are subscribed to.
        we emit a qt signal, that should be connected by any application.
        '''
        print "db notification received by base class '%s'"% notification
        QtGui.QApplication.instance().emit(
            QtCore.SIGNAL("db notification"), notification)

    def emit_notification(self, notification):
        q_query = QtSql.QSqlQuery("NOTIFY %s"% notification, self)
        if q_query.lastError().isValid():
            print "error", q_query.lastError().text()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    app = QtGui.QApplication([])
    parent = QtGui.QWidget()
    db = DatabaseConnection()
    logging.debug(db)
    message =  '<body>'
    try:
        db.connect()
        message += '<h4>connection Ok... </h4>'
        db.emit_notification("hello")
        db.close()
    except ConnectionError as e:
        message = u"connection error<hr />%s"% e
        app.restoreOverrideCursor()
    message += "</body>"

    QtGui.QMessageBox.information(parent, "result", message)

    app.closeAllWindows()
