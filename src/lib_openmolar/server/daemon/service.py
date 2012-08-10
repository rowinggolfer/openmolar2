#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011, Neil Wallace <rowinggolfer@googlemail.com>               ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

'''
"borrows" heavily from http://code.google.com/p/supay/
and the book python for sysadmins (which I own)
'''

import os
import sys

from signal import SIGTERM

PIDFILE = "/var/run/openmolar/server.pid"

class Service(object):
    
    def write_pidfile(self):
        dirname = os.path.dirname(PIDFILE)
        try:
            os.mkdir(dirname)
        except OSError as exc:
            if exc.errno == 17:
                pass
            else:
                LOGGER.error('Unable to create %s - Are you root?'% dirname)
                return False

        pid = os.getpid()
        try:
            f = open(PIDFILE, "w")
            f.write("%s\n"% pid)
            f.close()

        except IOError, exc:
            if exc.errno == 13:
                LOGGER.error('Unable to create %s - Are you root?' % pid)
            else:
                LOGGER.exception('The service module had an IO error:')
            return False

        return True

    def start_(self, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null"):
        '''
        checks for a PIDfile,
        daemonises the process,
        writes the new PIDfile
        '''
        if self.is_running:
            LOGGER.warning("openmolar-server is already started")
            
        self.daemonise(stdin, stdout, stderr)
        return self.write_pidfile()

    def daemonise(self, stdin, stdout, stderr):
        """
        Double forks the process in the background
        to avoid zombies, writes a PID.
        """

        #we are about to fork the process... so clear any output first
        sys.stdout.flush()
        sys.stderr.flush()

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, exc:
            LOGGER.exception("fork 1 failed")
            sys.exit("%s: fork #1 failed: (%d) %s\n" % (sys.argv[0],
            exc.errno, exc.strerror))

        os.chdir("/")
        os.umask(0)
        os.setsid()

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, exc:
            LOGGER.exception("fork 2 failed")
            sys.exit("%s: fork #2 failed: (%d) %s\n" % (sys.argv[0],
            exc.errno, exc.strerror))

        si = file(stdin, "r")
        so = file(stdout, "a+")
        se = file(stderr, "a+", 0)

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def stop_(self):
        try:
            pidfile = open(PIDFILE, "r")
            pid = pidfile.readline()
            LOGGER.info("Stopping the openmolar_server. " +
                "With pid number %s" % pid)
            os.kill(int(pid), SIGTERM)
            os.remove(PIDFILE)

        except OSError, e:
            LOGGER.error("Could not kill process")
            if e.errno == 3: # catch a 'no such process'
                os.remove(PIDFILE)
                LOGGER.info("Removed defunct PID file.")
                LOGGER.info("Try restarting openmolar-server now")

        except IOError:
            LOGGER.warning("PID file not found when stopping server.")
            LOGGER.warning("openmolar-server may not be running?")

    def status_(self):
        '''
        Check the status of the process (running | not running)
        '''
        LOGGER.info('checking status of openmolar-server process')
        try:
            pidfile = open(PIDFILE)
            pid = pidfile.readline()
            os.kill(int(pid), 0)
        except OSError:
            LOGGER.warning('openmolar-server process not running')
        except IOError:
            LOGGER.warning('openmolar-server process not running')
        else:
            LOGGER.info(
                'openmolar-server process is running with PID: %s'% pid)

    @property
    def is_running(self):
        '''
        true is the process already exists.
        '''
        return os.path.isfile(PIDFILE)
            

def _test():
    sd = Service()
    if "start" in sys.argv:
        sd.start_()
    elif "stop" in sys.argv:
        sd.stop_()
    elif "status" in sys.argv:
        sd.status_()
    else:
        LOGGER.warning("nothing to do")
        LOGGER.info("please pass 'start | stop | status' as arguments")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    LOGGER = logging.getLogger("test")
    
    _test()