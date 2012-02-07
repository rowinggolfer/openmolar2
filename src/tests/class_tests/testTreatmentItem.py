#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010, Neil Wallace <rowinggolfer@googlemail.com>               ##
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

from lib_openmolar.common.common_db_orm.treatment_item import TreatmentItem

from lib_openmolar.client.connect import ClientConnection
from lib_openmolar.client.db_orm.patient_model import PatientModel
from lib_openmolar.client.qt4.client_widgets import ToothData


import unittest

class TestCase(unittest.TestCase):
    def setUp(self):
        #ClientConnection().connect()
        #pt = PatientModel(2)
        #SETTINGS.set_current_patient(pt)
        pass

    def tearDown(self):
        pass

    def spawn_all_proc_code_tis(self):
        '''
        create all treatment items generated from procedure codes
        '''
        for proc_code in SETTINGS.PROCEDURE_CODES:
            item = TreatmentItem(proc_code)
            item.set_px_clinician(1)
            if item.tooth_required:
                item.set_teeth([7])
            if item.surfaces_required:
                fill, surfs = "MODBL",""
                for char in fill:
                    surfs += char
                    try:
                        item.set_surfaces(surfs)
                    except TreatmentItemException:
                        pass
            if item.pontics_required:
                continue

                ##TODO - this is busted!
                if item.is_bridge:
                    pontics = [2,3,4,5,6]
                    i = 0
                    while i < 5 and item.entered_span < item.required_span:
                        i += 1
                        item.set_pontics(pontics[:i])
                elif item.is_prosthetics:
                    item.set_pontics([3,4])

            yield item

    def test_proc_codes(self):
        for item in self.spawn_all_proc_code_tis():
            valid, errors = item.check_valid()
            self.assertTrue(valid, "%s %s"% (item, errors))

    def test_proc_codes_are_chartable(self):
        for item in self.spawn_all_proc_code_tis():
            if item.is_chartable:
                td = ToothData(item.tooth)
                td.from_treatment_item(item)


if __name__ == "__main__":
    unittest.main()
