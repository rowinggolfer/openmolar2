Interacting with the Database
=============================

:Author: Neil Wallace (neil@openmolar.com)


Introduction
------------

To Interact with the postgresql database, I utilise the QtSql Module of PyQt4.

It is therefore a condition that this module is installed (on all client and admin machines), along with the correct PSQL driver.

With few exceptions (namely the way the admin application creates large read/write tables), Openmolar uses an object orientated model approach *(ORM)* to interaction with the underlying database. 

By this I mean that every table row read is mapped to a python object. This object allows user interaction, and then updates the database in the appropriate manner.

Such an approach is pretty commonplace (those familiar with SqlAlchemy will know this concept).

The python objects generated, however, inherit from the QtSql.QSqlRecord class. Data is stored as QVariants.

In cases where an object has a complex underlying data structure, I create a "View" in the schema of Postgres, and a set of rules to ensure that updates on that view are handled correctly by the database.

A good example of this is the way postal address data is stored.

Address Example.
----------------

Addresses are stored in a table "addresses" with metadata about that address (home/work/etc.. or date patient moved in etc..) stored in a seperate table "address_link".

Address table columns (simplified example only - see schema for the real situation)

#. id
#. house name
#. street
#. city
#. postal_cd

Address_link table columns (simplified example only - see schema for the real situation)

1. ix
2. id
3. type
4. to_date
5. from_date

This design enables a *many-to-many* approach. 

-  several patients may have the same address (and corrections to one will be a correction to all) 
-  one patient may have several addresses.

In the admin application, or by direct sql statements via any method, the basic tables can be altered.

However, for the client application, we need to present some further information to the user, and derive some simple logic from the more complicated column data.

- how many people share this address?  (performed by a row-count in the address_link table where the address_id is specified)
- is it the patient's current address? (converted to a boolean from logic on the to-date and from-date fields)


A view is created "view_addresses", which creates a "pseudo-table" with the following columns.

#. id
#. house_name
#. street
#. city
#. postal_cd
#. ix
#. type
#. to_date
#. from_date
#. *known_residents*
#. *in_current_use*


The ORM objects have those attributes, and rules in the postgres schema *should* make sure that from the programmer's point of view, that table actually exists!  

Example Code
____________

The following 2 classes demonstrate this functionality.

AddressObjects will be a list of AddressObject types.

Each AddressObject has display and update functions, 
and hopefully this demonstrates how it would be trivial to add more. ::

    class AddressObject(QtSql.QSqlRecord):
        def __init__(self, connection, record):
            QtSql.QSqlRecord.__init__(self, record)
            self.connection = connection
            
        def display_as_html(self):
            'something like this'
            return "<html><body>Address - %s %s.... </body></html>" % (
                self.value("street").toString(), 
                self.value("house_name").toString())
                
        def move_out(self):
            self.value("to_date").setDate(QtCore.QDate.currentDate())
            
        def update(self):
            '''
            send an update to the view (which will handle it)
            '''
            changes = ""
            values = []
            for i in self.count():
                field = self.field(i)
                if field.name() != "id":
                    changes += "%s = ?,"% field.name()
                    values.append(field.value())

                changes = changes.rstrip(",")
                query = "UPDATE view_addresses set %s WHERE id=?"% changes
                q_query = QtSql.QSqlQuery(self.connection)
                q_query.prepare(query)
                for value in values + [self.value('id')]:
                    q_query.addBindValue(value)
                q_query.exec_()

    class AddressObjects(list):
        def __init__(self, connection, patient_id):
            self.patient_id = patient_id
            
            query = 'select * from view_addresses where patient_id=?'
            
            q_query = QtSql.QSqlQuery(connection)
            q_query.prepare(query)
            q_query.addBindValue(self.patient_id)
            q_query.exec_()
            while q_query.next():
                record = q_query.record()

                address_object = AddressObject(connection, record)
                self.append(address_object)





