#! /bin/sh

# this script creates the postgres user "openmolar"
# who is allowed to create new roles and databases.
# This user will be the owner of ALL openmolar's databases,
# and as such be of use for backups etc..

echo "CREATE ROLE openmolar;"
echo "CREATE ROLE openmolar;" | su postgres -c psql

