#! /bin/sh
#
### BEGIN INIT INFO
# Required-Start:    $local_fs $remote_fs $network
# Required-Stop:     $local_fs $remote_fs $network
# Provides:          openmolar-server
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: the remote procedure server of openmolar 
# Description:       the remote procedure server of openmolar
#                    provides functions for maintenance of the postgres database
### END INIT INFO


PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
NAME=openmolar-server
DESC=openmolar-server

set -e

case "$1" in
  start)
        echo "Checking for running $DESC: "
	    openmolar-server -q --start
	    ;;
  stop)
        echo "Checking for running $DESC: "
	    openmolar-server -q --stop
	    ;;
  restart)
        echo "Checking for running $DESC: "
	    openmolar-server -q --restart
	    ;;      
  force-reload)
	# nothing
	;;
  status)
        echo "Checking for running $DESC: "
	    openmolar-server -q --status
	    ;;      
  *)
    N=/etc/init.d/$NAME
    echo "Usage: $N {start|stop|restart|force-reload|status}" >&2
    exit 1
    ;;
esac

