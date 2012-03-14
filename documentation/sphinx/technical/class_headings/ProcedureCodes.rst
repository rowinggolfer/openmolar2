:Author: Neil Wallace (neil@openmolar.com)
:Release: |release|
:Date: |today|


This class contains all the applications valid :doc:`ProcCode` objects.


This is a test of the blockdiag extension.

.. blockdiag::

    diagram admin {
      ProcCode -> TreatmentItem -> TreatmentModel;
    }


.. blockdiag::
    
    diagram {
       // Set labels to nodes.
       A [label = "foo"];
       B [label = "bar"];
       C [label = "baz"];

       // Set labels to edges. (short text only)
       A -> B [label = "click bar"];
       B -> C [label = "click baz"];
       C -> A;
    }

