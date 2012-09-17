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

'''
Provides the TreatmentModel Class
'''

import logging
from PyQt4 import QtCore, QtSql

from lib_openmolar.common.datatypes import OMType
from lib_openmolar.common.db_orm import InsertableRecord
from lib_openmolar.common.db_orm import TreatmentItem

from lib_openmolar.client.qt4.widgets import ChartDataModel
from lib_openmolar.client.qt4.widgets import ToothData
from lib_openmolar.client.qt4.widgets import TreatmentTreeModel


class TreatmentModel(object):
    def __init__(self):
        '''
        instanciates with no params
        '''
        self.tree_model = TreatmentTreeModel()

        #:a pointer to the treatment plan :doc:`ChartDataModel`
        self.plan_tx_chartmodel = ChartDataModel()

        #:a pointer to the treatment completed :doc:`ChartDataModel`
        self.cmp_tx_chartmodel = ChartDataModel()

        self._treatment_items = []
        self._deleted_items = []

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
        LOGGER.debug("clearing treatment_model")
        self._treatment_items = []
        self._deleted_items = []
        self.plan_tx_chartmodel.clear()
        self.cmp_tx_chartmodel.clear()
        self.tree_model.update_treatments()

    def get_records(self):
        '''
        pulls all treatment items in the database
        (for the patient with the id specified at class initiation)
        '''
        ## long query - only time will tell if this is a performance hit

        if not self.patient_id:
            return

        query =  '''select
treatments.ix, patient_id, parent_id, om_code, description,
completed, comment, px_clinician, tx_clinician, tx_date, added_by
from treatments
left join procedure_codes on procedure_codes.code = treatments.om_code
where patient_id = ?'''

        q_query = QtSql.QSqlQuery(SETTINGS.psql_conn)
        q_query.prepare(query)
        q_query.addBindValue(self.patient_id)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()

            treatment_item = TreatmentItem(record)
            self.add_treatment_item(treatment_item)

    @property
    def treatment_items(self):
        '''
        returns a list of all :doc:`TreatmentItem` in the model
        '''
        return self._treatment_items

    @property
    def deleted_items(self):
        '''
        returns a list of all :doc:`TreatmentItem` which have been deleted
        '''
        return self._deleted_items

    @property
    def is_dirty(self):
        '''
        will return True if the model differs from that in the database
        '''
        if self.deleted_items != []:
            return True
        dirty = False
        for treatment_item in self.treatment_items:
            dirty = dirty or not treatment_item.in_database
        return dirty

    def add_treatment_item(self, treatment_item):
        '''
        add a :doc:`TreatmentItem` Object
        returns True if the TreatmentItem is valid, else False
        '''
        if treatment_item.is_valid:
            self._treatment_items.append(treatment_item)

            if treatment_item.is_chartable:
                self.add_to_chart_model(treatment_item)

            self.tree_model.update_treatments()
            return True

        LOGGER.debug(treatment_item.errors)

        if treatment_item.in_database:
            raise IOError, "invalid treatment in database treatments id=%s"% (
                treatment_item.id.toInt()[0])

        return False

    def add_to_chart_model(self, treatment_item):
        '''
        represent the treatment_item on the charts page somehow.
        '''
        if treatment_item.is_completed:
            chartmodel = self.cmp_tx_chartmodel
        else:
            chartmodel = self.plan_tx_chartmodel

        for data in treatment_item.metadata:
            tooth_data = ToothData(data.tooth)
            tooth_data.from_treatment_item_metadata(data)

            chartmodel.add_property(tooth_data)
        chartmodel.endResetModel()

    def remove_treatment_item(self, treatment_item):
        '''
        removes a :doc:`TreatmentItem` Object
        '''
        self._treatment_items.remove(treatment_item)
        self._deleted_items.append(treatment_item)

        if treatment_item.is_chartable:
            self.update_chart_models()

        self.tree_model.update_treatments()

    def complete_treatment_item(self, treatment_item, completed=True):
        '''
        :param: treatment_item (:doc:`TreatmentItem`)
        :kword: completed=bool (default True)

        toggles the state of a :doc:`TreatmentItem` to completed
        '''
        orig_value = treatment_item.is_completed

        treatment_item.set_completed(completed)
        treatment_item.set_cmp_date()

        if not treatment_item.is_valid:
            treatment_item.set_completed(orig_value)
            return False

        if treatment_item.is_chartable:
            self.update_chart_models()

        self.tree_model.update_treatments()
        return True

    def update_chart_models(self):
        '''
        completely reloads the chart models.
        '''
        self.cmp_tx_chartmodel.clear()
        self.plan_tx_chartmodel.clear()

        for treatment_item in self.treatment_items:
            if treatment_item.is_completed:
                chartmodel = self.cmp_tx_chartmodel
            else:
                chartmodel = self.plan_tx_chartmodel

            for data in treatment_item.metadata:
                tooth_data = ToothData(data.tooth)
                tooth_data.from_treatment_item_metadata(data)

                chartmodel.add_property(tooth_data)

        self.cmp_tx_chartmodel.endResetModel()
        self.plan_tx_chartmodel.endResetModel()

    def update_views(self):
        '''
        this should be called after adding to the model
        update all submodels (treeview, charts etc.)
        '''
        self.tree_model.update_treatments()
        self.cmp_tx_chartmodel.endResetModel()
        self.plan_tx_chartmodel.endResetModel()

    def commit_changes(self):
        '''
        push all changes to the database
        '''
        LOGGER.debug("Committing treament item changes")

        if not self.is_dirty:
            return
        result = True
        for item in self.treatment_items:
            if not item.in_database:
                result = result and self.commit_item(item)

        for item in self.deleted_items:
            #sliently drop any items which never got committed
            if item.in_database:
                LOGGER.debug("remove %s from database"% item)
        return result

    def commit_item(self, item):
        '''
        Commit the item to the database
        '''
        return item.commit_to_db(SETTINGS.psql_conn)

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)

    from lib_openmolar.client.connect import DemoClientConnection
    from lib_openmolar.client.db_orm import PatientModel

    cc = DemoClientConnection()
    cc.connect()

    pt = PatientModel(1)

    obj = pt.treatment_model

    for record in obj.treatment_items:
        print record
        print record.metadata
