#! /bin/sh

# this script creates the master database "openmolar_master"

echo "createdb -e --owner=openmolar openmolar_master" | su postgres

echo "\nALL DONE!"
