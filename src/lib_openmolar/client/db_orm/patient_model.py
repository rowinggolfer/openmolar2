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
This module provides the PatientModel Class, which pulls together
functionality from all the ORM classes as and when required.
'''

from PyQt4 import QtCore, QtSql

from lib_openmolar.client.db_orm import *


class PatientModel(object):
    '''
This very important class represents the full patient record.

The behaviour of this object is very much like a dictionary.
    '''
    _dict = {}

    _notes_summary_html = None

    def __init__(self, patient_id):
        self["patient"] = PatientDB(patient_id)
        self["addresses"] = AddressObjects(patient_id)
        self["telephone"] = TelephoneDB(patient_id)
        self["teeth_present"] = TeethPresentDB(patient_id)
        self["static_fills"] = StaticFillsDB(patient_id)
        self["static_crowns"] = StaticCrownsDB(patient_id)
        self["static_roots"] = StaticRootsDB(patient_id)
        self["static_comments"] = StaticCommentsDB(patient_id)
        self["notes_clinical"] = NotesClinicalDB(patient_id)
        self["notes_clerical"] = NotesClericalDB(patient_id)
        self["memo_clinical"] = MemoClinicalDB(patient_id)
        self["memo_clerical"] = MemoClericalDB(patient_id)
        self["treatment_model"] = SETTINGS.treatment_model
        SETTINGS.treatment_model.load_patient(patient_id)
        self["perio_bpe"] = PerioBpeDB(patient_id)
        self["perio_pocketing"] = PerioPocketingDB(patient_id)
        self["contracted_practitioners"] = ContractedPractitionerDB(patient_id)

        self.patient_id = patient_id

    @property
    def is_dirty(self):
        '''
        A Boolean.
        If True, then the record differs from the database state
        '''
        dirty = False
        for att in ("patient", "addresses", "teeth_present",
        "static_fills", 'static_crowns', 'static_roots', 'static_comments',
        'memo_clinical', 'memo_clerical', 'treatment_model'):
            if self[att].is_dirty:
                dirty = True
                break
        return dirty

    def what_has_changed(self):
        '''
        returns a stringlist of what has changed.

        TODO could be much improved
        '''
        changes = []
        for att in ("patient", "addresses", "teeth_present",
        "static_fills", 'static_crowns', 'static_roots', 'static_comments',
        'memo_clinical', 'memo_clerical', 'treatment_model'):
            if self[att].is_dirty:
                changes.append(att)
        return changes

    def commit_changes(self):
        '''
        commits any user edits to the database
        '''
        for att in ("patient", "addresses", "teeth_present",
        "static_fills", 'static_crowns', 'static_roots', 'static_comments',
        'memo_clinical', 'memo_clerical', 'treatment_model'):
            self[att].commit_changes()

    @property
    def current_contracted_dentist(self):
        return self["contracted_practitioners"].current_contracted_dentist

    @property
    def static_chart_records(self):
        '''
        returns all data needed about teeth in the static chart
        see also ..func::`dent_key`
        '''
        for record in self['static_fills'].records:
            yield (record, 'fill')
        for record in self['static_crowns'].records:
            yield (record, 'crown')
        for record in self['static_roots'].records:
            yield (record, 'root')
        for record in self['static_comments'].records:
            yield (record, 'comment')

    @property
    def perio_data(self):
        '''
        A convenience function to access perio data.
        TODO only pocketing data is returned at the moment
        '''
        for record in self['perio_pocketing'].records:
            yield (record, 'pocket')

    @property
    def dent_key(self):
        '''
        this property is an integer, which represents which teeth are present
        '''
        dk, result = self['teeth_present'].value('dent_key').toLongLong()
        if not result:
            pass
            print "no dent-key"
        return dk

    def set_dent_key(self, key):
        '''
        sets the ..func::`dent_key` for this patient
        '''
        self["teeth_present"].setValue("patient_id", self.patient_id)
        self["teeth_present"].setValue("dent_key", key)
        self["teeth_present"].setValue("checked_date",
            QtCore.QDate.currentDate())
        self["teeth_present"].setValue("checked_by", SETTINGS.user)

    def details_html(self):
        '''
        an html representation of the patient
            this is a combination of html data from several tables
        '''
        html = u"<body><div>"
        html += self["patient"].details_html()
        html += "<br />"
        html += self["contracted_practitioners"].details_html()
        html += "<br />"
        html += self["addresses"].details_html()
        html += "<br />"
        html += self["telephone"].details_html()
        html += '''<hr /><div align='center'>
            <b>%s</b><a href='edit_memo'>%s</a>
            <br />%s'''% (_("MEMO"), SETTINGS.PENCIL, self.clerical_memo)
        return html + "<hr /></div></body>"

    @property
    def age_years(self):
        '''
        returns an integer of the patient's age in years
        '''
        return self["patient"].age_tuple()[0]

    @property
    def full_name(self):
        '''
        the patient's full name
        '''
        return self["patient"].full_name

    @property
    def notes_summary_html(self):
        '''
        returns an html representation of the *clinical* notes
        '''
        if self._notes_summary_html is None:
            self._notes_summary_html = self['notes_clinical'].to_html()
        return self._notes_summary_html

    @property
    def notes_reception_html(self):
        '''
        returns an html representation of the *reception* notes
        '''
        return self['notes_clerical'].to_html()

    @property
    def treatment_summary_html(self):
        '''
        returns an html summary of the treatment plan
        TODO - this is a placeholder function
        '''
        return "Treatment Plan for %s"% self.full_name

    @property
    def clinical_memo(self):
        '''
        returns the clinical memo for this patient
            displayed under the chart on the *summary* page
        '''
        return self["memo_clinical"].memo

    @property
    def clerical_memo(self):
        '''
        returns the clerical memo for this patient
            displayed prominently on the *reception* page
        '''
        return self["memo_clerical"].memo

    def refresh_bpe(self):
        '''
        reloads bpe data from the database
            this function should be called if a BPE dialog
            is raised and accepted
        '''
        self["perio_bpe"] = PerioBpeDB(self.patient_id)

    @property
    def current_bpe(self):
        '''
        a patient will potentially have many bpes recorded.
        this is the most recent one
        '''
        return self["perio_bpe"].current_bpe

    @property
    def treatment_model(self):
        '''
        A pointer to the relevant ..class: TreatmentModel
        '''
        return SETTINGS.treatment_model

    def get(self, key, fallback=None):
        '''
        PatientModel.get(self, key, fallback=None)
        '''
        try:
            return self._dict[key]
        except KeyError:
            return fallback

    def __setitem__(self, key, val):
        self._dict[key] = val

    def __getitem__(self, key):
        return self._dict[key]


if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    obj = PatientModel(1)

    print obj.details_html()
    print "DENT KEY", obj.dent_key
    print "ROOTS", obj["static_roots"].records
    print "BPE", obj["perio_bpe"].records
    print "contracted practitioners", obj["contracted_practitioners"].records
    print "Perio Data", obj.perio_data
    print "Age Years", obj.age_years


