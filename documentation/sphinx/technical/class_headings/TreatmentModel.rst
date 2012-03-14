:Author: Neil Wallace (neil@openmolar.com)
:Release: |release|
:Date: |today|

For Treatment Plans, a model/view design is in place.

This model keeps a list of all :doc:`TreatmentItem` objects for the patient, and is aware whether they are in the
database or not (ie. have just been added).

The model will inform any views of changes.

.. note::
    This is the current focus of development.
