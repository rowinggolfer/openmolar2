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

from lib_openmolar.client.qt4gui.client_widgets.chart_widgets import tooth_data
from lib_openmolar.client.qt4gui.client_widgets.chart_widgets import perio_data

class ChartDataModel(object):
    '''
    a custom set of dictionaries which holds data about all teeth in the mouth.

    ChartWidgets hold no data, but are "views" to this model.

    .. note::

        Summary and static chart share one instance of this class.
        the treatment chart and completed chart have an instance each.

    '''

    def __init__(self):
        #:
        self.data = []

        #:
        self.perio_data = []

        self.views = []
        '''
        a list of widgets which need to be informed whenever
        this model changes
        '''

    def register_view(self, widget):
        '''
        register all widgets which are attached to this model, so that
        when "endResetModel" is called, they get notified
        
        .. note::
            widgets registered this way must have a method model_changed()

        '''
        self.views.append(widget)

    def endResetModel(self):
        '''
        call this function after altering the data if you need to inform
        registered views of the change
        '''
        for view in self.views:
            view.model_changed()

    def has_properties(self, tooth_id):
        '''
        :param: tooth_id (int)

        returns True if this model has data for tooth with this id
        '''
        try:
            self.get_properties(tooth_id).next()
        except StopIteration:
            return False
        return True

    def add_property(self, tooth_data):
        '''
        add a :doc:`ToothData` object to this model
        '''
        self.data.append(tooth_data)

    def clear(self):
        '''
        resets the model, and any attached views
        '''
        self.perio_data = []
        self.data = []
        self.endResetModel()

    def get_properties(self, tooth_id):
        '''
        :param: tooth_id (int)

        a generator returning all :doc:`ToothData` objects for this tooth
        '''
        for prop in self.data:
            if prop.tooth_id == tooth_id:
                yield prop

    def get_restorations(self, tooth_id):
        '''
        :param: tooth_id (int)

        a generator returning all :doc:`ToothData` objects of
        type Filling or Crown for this tooth
        '''
        for prop in self.get_properties(tooth_id):
            if prop.type in (prop.FILLING, prop.CROWN):
                yield prop

    def get_root_info(self, tooth_id):
        '''
        :param: tooth_id (int)

        a generator returning all :doc:`ToothData` objects of
        type Root for this tooth
        '''
        for prop in self.get_properties(tooth_id):
            if prop.type == prop.ROOT:
                yield prop

    def get_new_fillings(self):
        '''
        a generator returning all :doc:`ToothData` objects of type Filling
        which are NOT in the database (ie have been added by client)
        '''
        for prop in self.data:
            if (prop.type == prop.FILLING and not prop.in_database):
                yield prop

    def get_new_crowns(self):
        '''
        a generator returning all :doc:`ToothData` objects of type Crown
        which are NOT in the database (ie have been added by client)
        '''
        for prop in self.data:
            if (prop.type == prop.CROWN and not prop.in_database):
                yield prop

    def get_new_roots(self):
        '''
        a generator returning all :doc:`ToothData` objects of type Root
        which are NOT in the database (ie have been added by client)
        '''
        for prop in self.data:
            if (prop.type == prop.ROOT and not prop.in_database):
                yield prop

    def get_new_comments(self):
        '''
        a generator returning all :doc:`ToothData` objects of type Comment
        which are NOT in the database (ie have been added by client)
        '''
        for prop in self.data:
            if (prop.type == prop.COMMENT and not prop.in_database):
                yield prop

    def get_perio_data(self, tooth_id):
        '''
        :param: tooth_id (int)

        a generator returning all :doc:`PerioData` for this tooth
        '''
        for prop in self.perio_data:
            if prop.tooth_id == tooth_id:
                yield prop

    def add_perio_property(self, prop):
        '''
        :param: prop (:doc:`PerioData` )

        add a perio data object to the model
        '''
        self.perio_data.append(prop)



    def add_root(self, root_record):
        '''
        add root data from the database orm
        root_record is an instance of QtSqlQRecord, with some customisations
        see lib_openmolar.common.common_db_orm.static_roots for details
        '''
        root_id = root_record.tooth_id
        if root_id:
            prop = tooth_data.ToothData(root_id)
            prop.set_type(prop.ROOT)
            prop.set_root_type(root_record.description)
            prop.set_comment(root_record.comment)
            prop.in_database = True
            self.add_property(prop)

    def add_crown(self, crown_record):
        '''
        add crown from the database orm
        crown is an instance of QtSqlQRecord, with some customisations
        see lib_openmolar.common.common_db_orm.static_crowns for details
        '''
        tooth_id = crown_record.tooth_id
        if tooth_id:
            prop = tooth_data.ToothData(tooth_id)
            prop.set_type(prop.CROWN)
            prop.set_crown_type(crown_record.crown_type)
            prop.set_technition(crown_record.technition)
            prop.set_comment(crown_record.comment)
            prop.in_database = True
            self.add_property(prop)

    def add_fill(self, fill_record):
        '''
        add fill from the database orm
        fill is an instance of QtSqlQRecord, with some customisations
        see lib_openmolar.common.common_db_orm.static_fills for details
        '''
        tooth_id = fill_record.tooth_id
        if tooth_id:
            prop = tooth_data.ToothData(tooth_id)
            prop.set_type(prop.FILLING)
            prop.set_surfaces(fill_record.surfaces)
            prop.set_material(fill_record.material)
            prop.set_comment(fill_record.comment)
            prop.in_database = True
            self.add_property(prop)

    def add_comment(self, record):
        '''
        add comment from the database orm
        fill is an instance of QtSqlQRecord, with some customisations
        see lib_openmolar.common.common_db_orm.static_comments for details
        '''
        tooth_id = record.tooth_id
        if tooth_id:
            prop = tooth_data.ToothData(tooth_id)
            prop.set_type(prop.COMMENT)
            prop.set_comment(record.text)
            prop.in_database = True
            self.add_property(prop)

    def add_fill_from_string(self, tooth_id, input):
        '''
        :param: int
        :param: string

        allows the addition of a fill in the form "MOD,CO"
        '''

        if tooth_id:
            prop = tooth_data.ToothData(tooth_id)
            prop.set_type(prop.FILLING)
            prop.from_fill_string(input)
            self.add_property(prop)

    def add_data(self, data_list):
        for record, data_type in data_list:
            if data_type == 'fill':
                self.add_fill(record)
            elif data_type == 'crown':
                self.add_crown(record)
            elif data_type == 'root':
                self.add_root(record)
            elif data_type == 'comment':
                self.add_comment(record)
            else:
                print "chart - add_data - unknown data type", record

    def add_perio_records(self, records):
        '''
        add records from database
        '''
        for record, type in records:
            if type == "pocket":
                tooth, values = record
                self.add_perio_data(tooth, perio_data.PerioData.POCKETING, values)

    def add_perio_data(self, tooth_id, type_, values):

        prop = perio_data.PerioData(tooth_id)
        prop.set_type(type_)
        prop.set_values(values)
        self.add_perio_property(prop)

    def load_test_data(self):
        from random import randint
        #- two ways to add a filling
        self.add_fill_from_string(5, "MO,AM")

        #-- let's add a few (at random)
        for fill in ("MOD,CO", "B,GL", "DO,AM", "O,GO", "B,PO", "FS"):
            self.add_fill_from_string(randint(1,32), fill)

        self.add_perio_data(3, perio_data.PerioData.POCKETING, (3,6,4,4,5,6))
        self.add_perio_data(4, perio_data.PerioData.POCKETING, (5,8,6,4,5,6))
        self.add_perio_data(5, perio_data.PerioData.POCKETING, (3,6,4,4,5,6))
        self.add_perio_data(6, perio_data.PerioData.POCKETING, (1,4,2,4,5,6))

        self.add_perio_data(19, perio_data.PerioData.POCKETING, (3,6,4,4,5,6))
        self.add_perio_data(20, perio_data.PerioData.POCKETING, (5,8,6,4,5,6))
        self.add_perio_data(21, perio_data.PerioData.POCKETING, (3,6,4,4,5,6))
        self.add_perio_data(22, perio_data.PerioData.POCKETING, (1,4,2,4,5,6))

    def __repr__(self):
        message = "ChartDataModel for views %s"%self.views
        for data in self.data:
            message += "\n\t%s"% data
        return message

if __name__ == "__main__":
    obj = ChartDataModel()
    obj.load_test_data()
    print obj
