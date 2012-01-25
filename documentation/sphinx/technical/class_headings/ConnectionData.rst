A custom datatype, capable of parsing conf files in the following format::

    [CONNECTION]
    # the name you use to identify this connection. must be unique.
    name = demo

    # information use to specify the connection type.
    type = TCP/IP
    auth = password

    # the following fields are required for connection to a postgres database

    host = localhost
    port = 5432
    db_name = openmolar_demo
    user = om_demo
    password = password
