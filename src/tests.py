#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
This module runs all unit tests for openmolar2
'''

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

import inspect, os, re, sys, unittest

def get_test_modules():
    '''
    get all modules in "unit_tests" directory
    '''
    unittest_dir = os.path.join(".","tests")
    for root, dir_, files in os.walk(unittest_dir):
        sys.path.insert(0, root)
        for file_ in files:
            if re.match("test.*\.py$", file_):
                module = __import__(re.sub("\.py$", "", file_))
                yield module

def get_tests():
    '''
    yields a test suite for all TestCases found in get_test_modules
    NOTE - this code works.. and works well, but perhaps I could utilise
    code from the unitest module itself??
    '''
    for mod in get_test_modules():
        for name in dir(mod):
            obj = getattr(mod, name)

            # look for all subclasses of TestCase
            if (inspect.isclass(obj) and unittest.TestCase in obj.mro()):
                yield unittest.TestLoader().loadTestsFromTestCase(obj)

def main():
    '''
    entry point for the application
    '''
    test_suite = unittest.TestSuite()
    for test in get_tests():
        test_suite.addTest(test)

    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    return not result.wasSuccessful()

if __name__ == "__main__":

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
    raw_input("press enter to exit")
