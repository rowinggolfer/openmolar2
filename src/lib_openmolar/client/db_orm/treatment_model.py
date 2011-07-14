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

'''
Provides the TreatmentModel Class
'''

from PyQt4 import QtCore, QtSql

from lib_openmolar.common.settings import om_types
from lib_openmolar.common import common_db_orm

from lib_openmolar.client.qt4gui.client_widgets import ChartDataModel
from lib_openmolar.client.qt4gui.client_widgets import ToothData
from lib_openmolar.client.qt4gui.client_widgets import TreatmentTreeModel


class TreatmentModel(object):
    def __init__(self):
        '''
        instanciates with no params
        '''
        self.tree_model = TreatmentTreeModel()

        #:a pointer to the treatment plan :doc:`ChartDataModel`
        self.tooth_tx_plan_model = ChartDataModel()

        #:a pointer to the treatment completed :doc:`ChartDataModel`
        self.tooth_tx_cmp_model = ChartDataModel()

        self._treatment_items = []

    def load_patient(self, patient_id):
        '''
        :param patient_id: integer
        '''
        #:
        self.patient_id = patient_id

        self.clear()
        self.get_records()

    def clear(self):
        '''
        reset this model
        '''
        SETTINGS.log("clearing treatment_model")
        self._treatment_items = []
        self.tooth_tx_plan_model.clear()
        self.tooth_tx_cmp_model.clear()
        self.tree_model.update_treatments()

    def get_records(self):
        '''
        pulls all treatment items in the database
        (for the patient with the id specified at class initiation)
        '''
        ## long query - only time will tell if this is a performance hit

        if not self.patient_id:
            return
        query =    '''select
treatments.ix, patient_id, parent_id, om_code, description,
completed, comment, px_clinician, tx_clinician, tx_date, added_by,
tooth, surfaces, material, type, technition
from treatments
left join procedure_codes on procedure_codes.code = treatments.om_code
left join treatment_teeth on treatments.ix = treatment_teeth.treatment_id
left join treatment_fills  on treatment_fills.tooth_tx_id = treatment_teeth.ix
left join treatment_crowns on treatment_crowns.tooth_tx_id = treatment_teeth.ix
where patient_id = ?
'''

        q_query = QtSql.QSqlQuery(SETTINGS.database)
        q_query.prepare(query)
        q_query.addBindValue(self.patient_id)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()

            treatment_item = common_db_orm.TreatmentItem(record)
            self.add_treatment_item(treatment_item, charted=False)

    @property
    def treatment_items(self):
        '''
        returns a list of all :doc:`TreatmentItem` in the model
        '''
        return self._treatment_items

    @property
    def is_dirty(self):
        '''
        will return True if the model differs from that in the database
        '''
        dirty = False
        for treatment_item in self.treatment_items:
            dirty = dirty or not treatment_item.in_database
        return dirty

    def add_treatment_item(self, treatment_item, charted=False):
        '''
        add a :doc:`TreatmentItem` Object
        returns True if the TreatmentItem is valid, else False
        '''
        if treatment_item.is_valid:
            self._treatment_items.append(treatment_item)

            if not charted and treatment_item.is_chartable:
                self.add_to_chart_model(treatment_item)

            self.tree_model.update_treatments()
            return True

        SETTINGS.log("invalid tratment item %s"% treatment_item)
        return False

    def add_to_chart_model(self, treatment_item):
        '''
        represent the treatment_item on the charts page somehow.
        '''
        if treatment_item.is_completed:
            chartmodel = self.tooth_tx_cmp_model
        else:
            chartmodel = self.tooth_tx_plan_model

        tooth_data = ToothData(treatment_item.tooth)
        tooth_data.from_treatment_item(treatment_item)

        chartmodel.add_property(tooth_data)
        chartmodel.endResetModel()

    def update_views(self):
        '''
        this should be called after adding to the model
        update all submodels (treeview, charts etc.)
        '''
        self.tree_model.update_treatments()
        self.tooth_tx_cmp_model.endResetModel()
        self.tooth_tx_plan_model.endResetModel()

    def commit_changes(self):
        '''
        push all changes to the database
        '''
        if not self.is_dirty:
            return
        print "treatment model, commiting changes"
        result = True
        for item in self.treatment_items:
            if not item.in_database:
                result = result and self.commit_item(item)

        return result

    def commit_item(self, item):
        '''
        Commit the item to the database
        '''
        return item.commit_to_db(SETTINGS.database)

if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    from lib_openmolar.client.db_orm import PatientModel

    cc = ClientConnection()
    cc.connect()

    pt = PatientModel(1)

    obj = pt.treatment_model

    for record in obj.treatment_items:
        print record

    SETTINGS.set_current_patient(pt)

    print obj.is_dirty
    ti = common_db_orm.TreatmentItem("D01")
    ti.set_px_clinician(1)
    ti.set_tooth(3)
    ti.set_surfaces("O")

    print "adding", ti
    print ti.in_database
    obj.add_treatment_item(ti)
    print obj.is_dirty
    print obj.commit_changes()

    print obj.tooth_tx_plan_model


