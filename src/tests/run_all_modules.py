#! /usr/bin/env python

'''
runs all modules in the source directory (except those listed in exclusions)
'''

import os
import subprocess

EXCLUSIONS = ["tests.py",]

for root, dirs, files in os.walk(os.path.abspath("../lib_openmolar")):
    for file_ in files:
        filepath = os.path.join(root, file_)
        if "/tests/" in filepath or file_ in EXCLUSIONS:
            continue
        if file_.endswith(".py"):
            print "="*80
            print "Executing %s"% filepath
            p = subprocess.Popen(["python", filepath])
            p.wait()
            print "="*80
