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



class ToothDataModel(object):
    '''
    a custom set of dictionaries which holds data about all teeth in the mouth.

    ..note::
        Summary and static chart share one instance of this class.
        the treatment chart and completed chart have an instance each.

    '''
    def __init__(self):
        #:
        self.data = []

        #:
        self.perio_data = []

        #:
        self.views = [] #keep a list of widgets which need
                        #to be informed of changes to this model

    def register_view(self, widget):
        '''
        register all widgets which are attached to this model, so that
        when "endResetModel" is called, they get notified
        :note:
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

    def add_property(self, prop):
        '''
        add a :doc:`ToothData` object to this model
        '''
        self.data.append(prop)

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
            if prop.tooth.ref == tooth_id:
                yield prop

    def get_restorations(self, tooth_id):
        '''
        :param: tooth_id (int)

        a generator returning all :doc:`ToothData` objects of
        type Filling or Crown for this tooth
        '''
        for prop in self.get_properties(tooth_id):
            if prop.type in (prop.Filling, prop.Crown):
                yield prop

    def get_root_info(self, tooth_id):
        '''
        :param: tooth_id (int)

        a generator returning all :doc:`ToothData` objects of
        type Root for this tooth
        '''
        for prop in self.get_properties(tooth_id):
            if prop.type == prop.Root:
                yield prop

    def get_new_fillings(self):
        '''
        a generator returning all :doc:`ToothData` objects of type Filling
        which are NOT in the database (ie have been added by client)
        '''
        for prop in self.data:
            if (prop.type == prop.Filling and not prop.in_database):
                yield prop

    def get_new_crowns(self):
        '''
        a generator returning all :doc:`ToothData` objects of type Crown
        which are NOT in the database (ie have been added by client)
        '''
        for prop in self.data:
            if (prop.type == prop.Crown and not prop.in_database):
                yield prop

    def get_new_roots(self):
        '''
        a generator returning all :doc:`ToothData` objects of type Root
        which are NOT in the database (ie have been added by client)
        '''
        for prop in self.data:
            if (prop.type == prop.Root and not prop.in_database):
                yield prop

    def get_new_comments(self):
        '''
        a generator returning all :doc:`ToothData` objects of type Comment
        which are NOT in the database (ie have been added by client)
        '''
        for prop in self.data:
            if (prop.type == prop.Comment and not prop.in_database):
                yield prop

    def get_perio_data(self, tooth_id):
        '''
        :param: tooth_id (int)

        a generator returning all :doc:`PerioData` for this tooth
        '''
        for prop in self.perio_data:
            if prop.tooth.ref == tooth_id:
                yield prop

    def add_perio_property(self, prop):
        '''
        :param: prop (:doc:`PerioData` )

        add a perio data object to the model
        '''
        self.perio_data.append(prop)

if __name__ == "__main__":
    object = ToothDataModel()
    for fill in object.get_new_fillings():
        print fill