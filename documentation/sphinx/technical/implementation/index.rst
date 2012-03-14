**************************
Openmolar - Implementation
**************************

:Author: Neil Wallace (neil@openmolar.com)

 - *LANGUAGE* Written in `Python <http://python.org>`_ (requires 2.6), 
 
 - *VERSION CONTROL* using the mercurial version control system. To obtain the latest sources execute::
        
        hg clone https://openmolar.googlecode.com/hg/ openmolar

 - *GUI TOOLKIT* `PyQt4 <http://www.riverbankcomputing.co.uk/software/pyqt/intro>`_

 - *DATA STORAGE* Levers the power of the excellent and mature open-source Postgresql Database. (for current schema see :doc:`../misc/postgres`)

 - *EASILY EXTENSIBLE* openmolar uses a custom plugin system, allowing per site or per station customisation. 

 
 - *TRANSLATION* provided via gnu gettext. All translatable strings are wrapped in the function _()::
          
        #example
        label = QtGui.QLabel(_("Please Translate me if necessary"))
  
    
  for those interested in contributing to the translation of openmolar, please visit 
  the translation page on `launchpad <https://translation.launchpad.net/openmolar>`_   
     

 

Detailed Documentation
----------------------

.. toctree::
    :maxdepth: 1

    ../classes/classindex
    
