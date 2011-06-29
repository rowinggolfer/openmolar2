A ProcCode instance is a custom data object of high importance to the 
openmolar application.

this is the object sent to the application when user selects a code
from the procedure code widget.

ProcCodes are ALWAYS initiated at application startup
when the :doc:`ProcedureCodes` object is created.

Their properties are obtained by decoding the file 
resources/proc_codes/om_codes.txt

(which is actually stored as a QResources, so editing the file will only
take effect once QResources are refreshed)

.. note::
    it is my intention that openmolar codes remain unique.
    If a practice needs additional codes, then this should NOT be done by 
    modifying the file mentioned above.
    

