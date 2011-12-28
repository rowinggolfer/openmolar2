Tutorial (user manual)
======================

:Author: Neil Wallace (rowinggolfer AT googlemail.com)
:Release: |release|
:Date: |today|


The Client
----------
Installed on every terminal in a dental practice.
A user friendly graphical database interface for surgeries and reception alike. 

.. _client_screenshot:
.. figure::  ../images/screenshots/client.png
   :align:   right
   :width:   20%

.. toctree::
    :maxdepth: 2

    client/index


The Server
----------
Openmolar uses the postgres database for data storage.
This should be installed on a unix-based operating system.
In addition to postgres, a service can be started which provides functionality
for installing, upgrading and backing up the database.

.. toctree::
    :maxdepth: 2

    server/index


    
The Admin Application
---------------------
Commonly only one instance of this would be installed. 
This is a graphical tool giving advanced options for use of the system.

.. _admin_screenshot:
.. figure::  ../images/screenshots/admin.png
   :align:   right
   :width:   20%

.. toctree::
    :maxdepth: 2
    
    admin/index
        

