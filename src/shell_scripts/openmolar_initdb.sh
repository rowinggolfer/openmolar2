#! /bin/sh

# this script creates a demo database 'openmolar_demo'
# and creates 2 roles...
# "openmolar" which is able to create new roles and databases.
# This user will be the owner of ALL openmolar's databases, and as such be of use for backups etc..
# "om_demo" which will have writes to the openmolar_demo database.

DATABASE="openmolar_demo"
echo $DATABASE

echo "RUNNING openmolar's postgres init script....\n"
echo "these commands are executed via a shell of user 'postgres'"
echo "which is the default postgresql superuser installed with most distributions"
echo "if this script fails.. please report a bug"

echo "############################################################################"
echo "##                                                                        ##"
echo "## dropping existing $DATABASE database (if present)                 ##"
echo "##                                                                        ##"
echo "############################################################################\n"

echo "DROP DATABASE if exists $DATABASE;"
echo "DROP DATABASE if exists $DATABASE;" | su postgres -c psql

echo "\n############################################################################"
echo "##                                                                        ##"
echo "## creating a priviliged postgres user 'openmolar'                        ##"
echo "## and regular user 'om_demo'                                             ##"
echo "## you can ignore any warnings here if these users already exist          ##"
echo "##                                                                        ##"
echo "############################################################################\n"

echo "CREATE ROLE openmolar WITH CREATEDB CREATEROLE LOGIN ENCRYPTED PASSWORD 'initial_password';"
echo "CREATE ROLE openmolar WITH CREATEDB CREATEROLE LOGIN ENCRYPTED PASSWORD 'initial_password';" | su postgres -c psql

echo "CREATE ROLE om_demo WITH LOGIN ENCRYPTED PASSWORD 'password';"
echo "CREATE ROLE om_demo WITH LOGIN ENCRYPTED PASSWORD 'password';" | su postgres -c psql

echo "\n############################################################################"
echo "## creating database $DATABASE                                       ##"
echo "## this may take some time                                                ##"
echo "##                                                                        ##"
echo "############################################################################\n"

echo "CREATE DATABASE $DATABASE WITH OWNER openmolar ENCODING 'UTF8';"
echo "CREATE DATABASE $DATABASE WITH OWNER openmolar ENCODING 'UTF8';" | su postgres -c psql

echo "\n############################################################################"
echo "##                                                                        ##"
echo "## installing fuzzymatch functions  (soundex etc..)                       ##"
echo "## from /usr/share/postgresql/8.4/contrib/fuzzystrmatch.sql               ##"
echo "##                                                                        ##"
echo "############################################################################\n"

cat /usr/share/postgresql/8.4/contrib/fuzzystrmatch.sql | su postgres -c "psql $DATABASE" 

echo "\nALL DONE!"
