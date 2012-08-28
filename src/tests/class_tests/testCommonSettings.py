#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
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

import os, sys

lib_openmolar_path = os.path.abspath("../../")
if not lib_openmolar_path == sys.path[0]:
    sys.path.insert(0, lib_openmolar_path)

from lib_openmolar.common.settings import CommonSettings

import unittest

class TestCase(unittest.TestCase):
    def setUp(self):
        self.settings = CommonSettings()

    def tearDown(self):
        pass

    def test_convert_tooth_shortname(self):
        self.assertEqual(self.settings.convert_tooth_shortname("UR8"), 1)



if __name__ == "__main__":
    unittest.main()
