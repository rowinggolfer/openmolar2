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
provides 3 classes.
ConnectionError - a custom python exception, raised if connection times out
SchemaError - a custom python exception, raised if connection times out
OpenmolarDatabase - a custom class inheriting from Pyqt4.QSql.QSqlDatabase
'''
import logging

from PyQt4 import QtSql, QtGui, QtCore

from lib_openmolar.common.datatypes import ConnectionData

class ConnectionError(Exception):
    '''
    a custom Exception
    '''
    pass
    

class OpenmolarDatabase(QtSql.QSqlDatabase):
    '''
    inherits from PyQt4.QSql.QSqlDatabase
    adds a function "connect", which opens the connection whilst
    using a qt wait cursor.
    Will Raise a Connection error if connection has not been established
    within 10 seconds
    '''
    _schema_version = None
    
    class SchemaVersionError(Exception):
        pass

    def __init__(self, connection_data):
        assert type(connection_data) == ConnectionData, (
            "argument for database connection MUST be of type ConnectionData")

        QtSql.QSqlDatabase.__init__(self, "QPSQL")

        self.connection_data = connection_data

        self.setHostName(connection_data.host)
        self.setPort(connection_data.port)
        self.setUserName(connection_data.user)
        self.setPassword(connection_data.password)
        self.setDatabaseName(connection_data.db_name)
        
        if connection_data.CONNECTION_TYPE == connection_data.TCP_IP:
            self.setConnectOptions("requiressl=1;")
        
        self.driver().notification.connect(self.notification_received)

    def _wait_cursor(self, waiting=False):
        '''
        provides/removes a WaitCursor during connection and parsing functions
        '''
        try:
            if waiting:
                QtGui.QApplication.instance().setOverrideCursor(QtCore.Qt.WaitCursor)
            else:
                QtGui.QApplication.instance().restoreOverrideCursor()
        except AttributeError: #no gui
            pass

    def connect(self, *args):
        '''
        open the connection, raising an error if fails or timeouts
        optional arguments of (user, password)
        '''
        self._schema_version = None

        logging.debug("OpenmolarDatabase connecting")
        
        self._wait_cursor()
        connection_in_progress = True
        def time_out():
            if connection_in_progress:
                self._wait_cursor(False)
                if not self.isOpen():
                    message = self.lastError().text()
                    self.close()
                    raise ConnectionError("Time out Error %s"% message)

        if QtCore.QCoreApplication.instance():
            QtCore.QTimer.singleShot(1000, time_out) ## 10 seconds.
            logging.info("timeout set to 10 seconds")
        if args:
            user = args[0]
            password = args[1]
            logging.debug("connecting with user '%s', password '%s'"% (
                user, "*"* len(password)))
            connected = self.open(user, password)
        else:
            logging.debug("connecting with default params")
            connected = self.open()
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
        logging.warning("classes inheriting from OpenmolarDatabase should "
        "re-implement function subscribeToNotifications")
        #self.driver().subscribeToNotification("new_appointment_made")

    def notification_received(self, notification):
        '''
        the database has emitted a notify signal with text notification
        that we are subscribed to.
        we emit a qt signal, that should be connected by any application.
        '''
        logging.info("db notification received '%s'"% notification)

        QtGui.QApplication.instance().emit(
            QtCore.SIGNAL("db notification"), notification)

    def emit_notification(self, notification):
        q_query = QtSql.QSqlQuery("NOTIFY %s"% notification, self)
        if q_query.lastError().isValid():
            print "error", q_query.lastError().text()

    @property
    def description(self):
        '''
        databasename, host and port
        '''
        return u"%s %s:%s"% (
            self.databaseName(), self.hostName(), self.port())
            
    
    @property
    def schema_version(self):
        '''
        poll the database to get the schema version from settings table
        '''
        if self._schema_version is None:
            logging.debug("polling database for schema version")
            query = "select max(data) from settings where key='schema_version'"
            q_query = QtSql.QSqlQuery(query, self)
            if not q_query.first():
                self._schema_version = "???"
            else:
                self._schema_version = q_query.value(0).toString()
        return self._schema_version
    
def _test():
    logging.basicConfig(level=logging.DEBUG)

    app = QtGui.QApplication([])
    parent = QtGui.QWidget()
    conn_data = ConnectionData()
    conn_data.demo_connection()
    db = OpenmolarDatabase(conn_data)
    logging.debug(db)
    message =  '<body>'
    try:
        db.connect()
        message += '<h4>connection Ok... </h4>'
        message += 'Schema Version %s'% db.schema_version
        db.emit_notification("hello")
        db.close()
    
    except ConnectionError as e:
        message = u"connection error<hr />%s"% e
        app.restoreOverrideCursor()
    message += "</body>"

    QtGui.QMessageBox.information(parent, "result", message)
    
    app.closeAllWindows()

if __name__ == "__main__":
    _test()