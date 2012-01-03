#! /usr/bin/env python 

import ConfigParser
import os
import sys

curdir = os.path.dirname(os.path.abspath(__file__))
cnf_path = os.path.join(os.path.dirname(curdir), "setup.cnf")

parser = ConfigParser.RawConfigParser()
parser.read(cnf_path)

if len(sys.argv) == 1:
    sys.exit("usage is get_version [PACKAGE]")

package = sys.argv[1]

version = parser.get(package, "version")
if package == "namespace":
    print (version)
    sys.exit(0)

rev_no =  parser.getint(package, "revision_number")
        
print ("%s+hg%03d"% (version, rev_no))
