#! /bin/sh

# this script creates the master database "openmolar_master"

DATABASE="openmolar_master"

echo "CREATING MASTER DATABASE"

echo "createdb -e --owner=openmolar "$DATABASE" 'contains information about openmolar databases on this server' " | su postgres

echo "LAYING OUT SCHEMA"

cat /etc/openmolar/master_schema.sql | su postgres -c "psql $DATABASE"


echo "\nALL DONE!"
