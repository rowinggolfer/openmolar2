#! /bin/sh

# this script creates the postgres user "openmolar"
# who is allowed to create new roles and databases.
# This user will be the owner of ALL openmolar's databases,
# and as such be of use for backups etc..

PWORD_LOCATION='/etc/openmolar/server/server.conf'
echo "ATTEMPTING RESET OF PASSWORD FOR PG_USER 'openmolar'"

if [ ! -f $PWORD_LOCATION ]
then
    echo 'FATAL ERROR!' $PWORD_LOCATION 'does not exist'
    exit 0
fi

PWORD=`grep 'password = ' $PWORD_LOCATION | awk -F' = ' {'print $2'}`

echo "ALTER ROLE openmolar WITH SUPERUSER CREATEDB CREATEROLE NOINHERIT LOGIN ENCRYPTED PASSWORD '************';"
echo "ALTER ROLE openmolar WITH SUPERUSER CREATEDB CREATEROLE NOINHERIT LOGIN ENCRYPTED PASSWORD '$PWORD';" | su postgres -c psql

