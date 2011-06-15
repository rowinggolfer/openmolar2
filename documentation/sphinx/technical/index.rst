***********************
Technical Documentation
***********************

:Author: Neil Wallace (rowinggolfer AT googlemail.com)
:Release: |release|
:Date: |today|
   

Welcome to the technical documentation for OpenMolar.

.. note::
    I use these documents daily whenever I work on openmolar. The :doc:`classes/classindex` in particular is an essential reference guide for
    me to remember how this application works!
    

Basic Information
-----------------

 - *LANGUAGE* Written in `Python <http://python.org>`_ (requires 2.6), 
 
 - *GUI TOOLKIT* `PyQt4 <http://www.riverbankcomputing.co.uk/software/pyqt/intro>`_

 - *DATA STORAGE* Levers the power of the excellent and mature open-source Postgresql Database. (for current schema see :doc:`postgres/index`)

 - *TRANSLATION* provided via gnu gettext. All translatable strings are wrapped in the function _()::
          
        #example
        label = QtGui.QLabel(_("Please Translate me if necessary"))
  
    
  for those interested in contributing to the translation of openmolar, please visit 
  the translation page on `launchpad <https://translation.launchpad.net/openmolar>`_   
 
 - *EASILY EXTENSIBLE* openmolar uses a custom plugin system, allowing per site or per station customisation. 


 - *VERSION CONTROL* using the bzr version control system. To obtain the latest sources execute::
        
        bzr branch lp:openmolar/0.2.1

Detailed Documentation
----------------------

.. toctree::
    :maxdepth: 2

    postgres/index
    
    database_interaction/index

    classes/classindex
    

     

