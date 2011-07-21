:Author: Neil Wallace (rowinggolfer AT googlemail.com)
:Release: |release|
:Date: |today|
   
This class is used to create the custom datatypes stored in the postgres database.


Let's take a trivial example.. how to store an individual's sex.

It is common to do have a field defined something like this::

    sex char(1) NOT NULL;
    CONSTRAINT chk_sex CHECK (sex = 'M' or sex = 'F')

however, another way is to create a postgres data type::
    
    CREATE TYPE sex_type AS ENUM ('M','F') 
    
and use it thus::
    
    sex sex_type NOT NULL
    
The OMType class does this for us, but is also a useful python object in it's own right, 
storing default values, translations etc.

"Sex" is a trivial example, it quickly becomes more complex when I store an enumeration of 
allowed crown types, or patient statuses etc. 
