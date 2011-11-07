#! /bin/sh

# this script creates the postgres user "openmolar"
# who is allowed to create new roles and databases.
# This user will be the owner of ALL openmolar's databases, 
# and as such be of use for backups etc..

PWORD_LOCATION='/etc/openmolar/server/master_pword.txt'

if [ ! -f $PWORD_LOCATION ]
then
    echo 'FATAL ERROR!' $PWORD_LOCATION 'does not exist'
    exit 0
fi

PWORD=`cat $PWORD_LOCATION`

echo "CREATE ROLE openmolar WITH CREATEDB CREATEROLE LOGIN ENCRYPTED PASSWORD '$PWORD';"
echo "CREATE ROLE openmolar WITH CREATEDB CREATEROLE LOGIN ENCRYPTED PASSWORD '$PWORD';" | su postgres -c psql

echo "\nALL DONE!"
