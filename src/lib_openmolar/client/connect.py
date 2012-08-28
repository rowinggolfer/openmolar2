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

'''
ClientConnection - a custom class inheriting from Pyqt4.QSql.QSqlDatabase
'''

from PyQt4 import QtGui, QtCore, QtSql

from lib_openmolar.common.datatypes import ConnectionData
from lib_openmolar.common.qt4.postgres.openmolar_database import \
    OpenmolarDatabase

from lib_openmolar.client.db_orm.client_patient import DuckPatient

class ClientConnection(OpenmolarDatabase):
    '''
    inherits from lib_openmolar.common.connect.OpenmolarDatabase,
    which in turn inherits from PyQt4.QSql.QSqlDatabase
    '''
    _blank_address_record = None

    def connect(self):
        SETTINGS.psql_conn = None
        self.setConnectOptions("%sapplication_name=openmolar-client;"%
            self.connectOptions())
        OpenmolarDatabase.connect(self)
        if self.schema_version not in SETTINGS.schema_versions:
            raise self.SchemaVersionError, (
        "Schema version mismatch schema is at '%s', allowed versions '%s'"% (
            self.schema_version, SETTINGS.schema_versions))


        SETTINGS.psql_conn = self

    @property
    def blank_address_record(self):
        if self._blank_address_record is None:
            query = QtSql.QSqlQuery("select * from addresses limit 1", self)
            #note - not positioned on a valid record
            record = query.record()
            #record.clear()
            self._blank_address_record = record
        return self._blank_address_record

    def fname_completer(self, sname):
        query = 'SELECT DISTINCT(first_name) from patients where last_name=?'
        return self.completer(query, [sname])

    def sname_completer(self):
        query = 'SELECT DISTINCT(last_name) from patients'
        return self.completer(query)

    def completer(self, query, bindings=[]):
        q_query = QtSql.QSqlQuery(self)
        q_query.prepare(query)
        for binding in bindings:
            q_query.addBindValue(binding)
        q_query.exec_()
        values = []
        while q_query.next():
            values.append(q_query.value(0).toString())
        completer = QtGui.QCompleter(values)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        return completer

    def get_matchlist(self, search_values):
        '''
        get's a list of patients who's criteria match a user search
        return a list of BasePatient objects (with address details appended)
        NOTE - also called when a new patient is being added, in which case
        search values is a dictionary)
        '''

        query = '''SELECT DISTINCT ON (patients.ix)
        patients.ix, title, last_name, first_name,
        preferred_name, dob, addr1, addr2, postal_cd, number
        from (patients left outer join
        (addresses join address_link on addresses.ix = address_link.address_id)
        on patients.ix = address_link.patient_id)
        left outer join
        (telephone join telephone_link on telephone.ix = telephone_link.tel_id)
        on telephone_link.patient_id = patients.ix
        WHERE '''

        conds, values = '', []

        sname = search_values.get("sname", "")
        soundex = search_values.get("soundex_sname", False)
        if sname != "":
            sub_cond = 'last_name ilike ? and '
            values.append(sname + "%")
            if soundex:
                sub_cond = '(%s or difference(last_name, ?) > 2) and '% (
                            sub_cond.rstrip("and "))
                values.append(sname)
            conds += sub_cond

        fname = search_values.get("fname", "")
        soundex = search_values.get("soundex_fname", False)
        if fname != "":
            sub_cond = '(first_name ilike ? or preferred_name ilike ?) and '
            values.append(fname + "%")
            values.append(fname + "%")
            if soundex:
                sub_cond = '''(%s or
                (difference(first_name, ?)>2 or
                difference(preferred_name, ?)>2))
                and '''% sub_cond.rstrip("and ")
                values.append(fname)
                values.append(fname)
            conds += sub_cond

        dob = search_values.get("dob", QtCore.QDate(1900,1,1))
        if dob != QtCore.QDate(1900,1,1):
            conds += 'dob = ? and '
            values.append(dob)

        addr = search_values.get("addr")
        if addr:
            conds += '(addr1 ilike ? or addr2 ilike ?) and '
            values.append("%"+addr+"%")
            values.append("%"+addr+"%")

        pcde = search_values.get("pcde")
        if pcde:
            conds += 'postal_cd ilike ? and '
            values.append("%"+pcde+"%")

        tel = search_values.get("tel")
        if tel:
            conds += 'number ilike ? and '
            values.append("%"+tel+"%")

        query = query + conds.rstrip('and ')
        q_query = QtSql.QSqlQuery(self)
        q_query.prepare(query)
        for value in values:
            q_query.addBindValue(value)

        if not q_query.exec_():
            print "BAD QUERY?"
            print query
            self.emit_caught_error(q_query.lastError())
        matches = []
        while q_query.next():
            patient = DuckPatient()
            patient.patient_id = q_query.value(0).toInt()[0]
            patient.title = unicode(q_query.value(1).toString())
            patient.last_name = unicode(q_query.value(2).toString())
            patient.first_name = unicode(q_query.value(3).toString())
            patient.preferred_name = unicode(q_query.value(4).toString())
            patient.dob = q_query.value(5).toDate()

            ## attribute for search only
            patient.addr1 = q_query.value(6).toString()
            patient.addr2 = q_query.value(7).toString()
            patient.pcde = q_query.value(8).toString()
            patient.number = q_query.value(9).toString()

            matches.append(patient)

        return matches

    def get_address_matchmodel(self, search_values):
        '''
        get's a list of addresses who's criteria match a user search
        '''
        query = '''SELECT ix, addr1, addr2, addr3, city,
        county, country, postal_cd from addresses
        WHERE '''

        conds, values = '', []

        address_id = search_values.get("address_id")
        if address_id:
            conds += "ix = ?"
            values.append(address_id)
        else:
            addr = search_values.get("addr1")
            if addr:
                values.append(u"%%%s%%"% addr)
                values.append(u"%%%s%%"% addr)
                values.append(u"%%%s%%"% addr)
                conds += "(addr1 like ? or addr2 like ? or addr3 like ?) and "

            addr = search_values.get("addr2")
            if addr:
                values.append(u"%%%s%%"% addr)
                values.append(u"%%%s%%"% addr)
                values.append(u"%%%s%%"% addr)
                conds += "(addr1 like ? or addr2 like ? or addr3 like ?) and "

            city = search_values.get("city")
            if city:
                conds += 'city like ? '
                values.append("%"+city+"%")

            country = search_values.get("country")
            if country:
                conds += 'country like ? '
                values.append("%"+country+"%")

            pcde = search_values.get("postal_cd")
            if pcde:
                conds += 'postal_cd like ? '
                values.append("%"+pcde+"%")

        query = query + conds.rstrip("and ")
        q_query = QtSql.QSqlQuery(self)
        q_query.prepare(query)
        for value in values:
            q_query.addBindValue(value)

        if not q_query.exec_():
            print "error with query", query
            self.emit_caught_error(q_query.lastError())
        model = QtSql.QSqlQueryModel()
        model.setQuery(q_query)

        return model

    def subscribeToNotifications(self):
        '''
        this should be overwritten when this connection is implemented
        postgres can emit signals when the database is changed by another
        client.
        the query is simple
        NOTIFY new_appointment_made
        '''
        self.driver().subscribeToNotification("todays_book_changed")

    def emit_caught_error(self, error):
        '''
        emits a signal with signature "db error" hopefully someone will see it!
        '''
        if error.isValid():
            print "emiting error", error.text()
            QtGui.QApplication.instance().emit(
                QtCore.SIGNAL("db error"), error.text())

class DemoClientConnection(ClientConnection):
    '''
    A connection to the demo database (on localhost)
    used for testing purposes.
    '''
    def __init__(self):
        conn_data = ConnectionData()
        conn_data.demo_connection()

        ClientConnection.__init__(self, conn_data)

def test_soundex(cc):
    '''
    this will fail if the soundex function (from postgres contrib)
    has not be installed into the database
    '''
    values = {"sname":"POTTA", "soundex_sname":True}
    #values = {"sname":"POTTER"}
    print cc.get_matchlist(values)

if __name__ == "__main__":
    from lib_openmolar import client

    app = QtGui.QApplication([])

    cc = DemoClientConnection()
    cc.connect()

    #test_soundex(cc)
    print cc.blank_address_record
