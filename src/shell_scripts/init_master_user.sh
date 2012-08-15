#! /bin/sh

# this script creates the postgres user "openmolar"
# who is allowed to create new roles and databases.
# This user will be the owner of ALL openmolar's databases,
# and as such be of use for backups etc..

PWORD_LOCATION='/etc/openmolar/server/server.conf'

if [ ! -f $PWORD_LOCATION ]
then
    echo 'FATAL ERROR!' $PWORD_LOCATION 'does not exist'
    exit 0
fi

PWORD=`grep 'password = ' /etc/openmolar/server.conf | awk -F' = ' {'print $2'}`

echo "CREATE ROLE openmolar;"
echo "ALTER ROLE openmolar WITH CREATEDB CREATEROLE LOGIN ENCRYPTED PASSWORD '************';"
echo "CREATE ROLE openmolar;ALTER ROLE openmolar WITH CREATEDB CREATEROLE LOGIN ENCRYPTED PASSWORD '$PWORD';" | su postgres -c psql

echo "\nALL DONE!"
