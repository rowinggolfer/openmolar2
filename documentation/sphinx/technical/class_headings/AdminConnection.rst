:Author: Neil Wallace (neil@openmolar.com)
:Release: |release|
:Date: |today|

Inherits from :doc:`PostgresDatabase` adding some functionality required only by the openmolar admin application.

A very important function is :func:`~<KLASS>.populateDemo` which populates the current database with demo data. 
This dangerous action is only performed if the database name ends with *_demo* or *_test* to prevent random data going into a real database.


.. note::    
    If this class is initiated with no arguments, a connection to the openmolar_demo on localhost will be established if possible.
    

