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
Provides the TreatmentItem Class
'''

import logging
import re
import types

from PyQt4 import QtSql, QtCore

from lib_openmolar.common.classes import proc_codes
from insertable_record import InsertableRecord

PROCEDURE_CODES = proc_codes.ProcedureCodesInstance()

class TreatmentItemException(Exception):
    '''
    a custom exception raised by treatment item errors
    '''
    def __init__(self, value="unknown"):
        self.value = value
    def __str__(self):
        return repr(self.value)

class TreatmentItemMetadata(object):
    '''
    every treatment item can have multiple metadata objects associated with it
    for example..
    a periodontal splint needs to know which teeth are splinted.
    a partial denture needs to know which teeth it replaces
    '''
    def __init__(self, parent_item, record=None):

        #: keep a pointer to the qslqrecord
        self.qsql_record = record

        #: keep a pointer to the parent item
        self.parent_item = parent_item

        self._tx_type = None
        self._surfaces = ""
        self._tooth = None
        self._crown_type = None
        self._technition = None

    @property
    def is_chartable(self):
        '''
        all metadata items are chartable?
        '''
        return True

    @property
    def tx_type(self):
        '''
        what metadata type is this?
        this value will be one defined by the om_types
        '''
        if self.in_database:
            return self.qsql_record.value("tx_type").toString()
        else:
            return self._tx_type

    @property
    def is_fill(self):
        return self.parent_item.code.is_fill

    @property
    def is_crown(self):
        return self.parent_item.code.is_crown

    @property
    def is_root(self):
        return self.parent_item.code.is_root

    @property
    def is_splint(self):
        return self.parent_item.code.tx_type == "splint"

    @property
    def is_pontic(self):
        return self.tx_type == "pontic"

    @property
    def is_wing(self):
        return self.tx_type == "wing"

    @property
    def is_abutment(self):
        return self.tx_type == "abutment"

    @property
    def surfaces_required(self):
        return self.parent_item.code.surfaces_required

    @property
    def tooth(self):
        if self.in_database:
            return self.qsql_record.value("tooth").toInt()[0]
        else:
            return self._tooth

    @property
    def surfaces(self):
        if self.in_database:
            return str(self.qsql_record.value("surfaces").toString())
        else:
            return self._surfaces

    @property
    def crown_type(self):
        '''
        crown type
        '''
        if self.in_database:
            return str(self.qsql_record.value("type").toString())
        else:
            return self._crown_type

    @property
    def technition(self):
        if self.in_database:
            return str(self.qsql_record.value("technition").toString())
        else:
            return self._technition

    @property
    def material(self):
        '''
        the material for charting purposes eg ("AM","CO" etc...)
        '''
        return self.parent_item.code.material

    def set_tx_type(self, tx_type):
        '''
        :param: tx_type (string)

        string should be enumerable by :doc:`OMType` tooth_tx_type
        '''
        self._tx_type = tx_type

    def set_tooth(self, tooth):
        '''
        :param: tooth_id (int)

        int should comply with :doc:`../../misc/tooth_notation`
        '''
        self._tooth = tooth

    def set_surfaces(self, surfaces):
        '''
        :param: surfaces(string)

        set the surfaces for a restoration

        .. note::
            an exception will be raised if surfaces are invalid

        '''
        self._surfaces = ""
        if self.surfaces_required:
            surf = surfaces.replace("I","O")
            surf = surf.replace("P","L")

            if (not re.match("[MODBL]{1,5}$", surf) or
            len(set(surf)) != len(surf)):
                raise TreatmentItemException("INVALID SURFACES '%s'"% surfaces)
            else:
                self._surfaces = surf

    @property
    def in_database(self):
        '''
        returns true if the item is in the database
        if it is, then it will have a valid :attr:`qsql_record` .
        '''
        return self.qsql_record != None

    def commit_db(self, database, treatment_id):
        record = InsertableRecord(database, "treatment_teeth")

        record.setValue("treatment_id", treatment_id)
        record.setValue("tooth", self.tooth)
        record.setValue("tx_type", self.tx_type)

        query, values = record.insert_query

        q_query = QtSql.QSqlQuery(database)
        q_query.prepare(query + "returning ix")
        for value in values:
            q_query.addBindValue(value)
        q_query.exec_()

        if q_query.lastError().isValid():
            error = q_query.lastError()
            database.emit_caught_error(error)
            return False

        if self.is_fill:
            q_query.first()
            ix = q_query.value(0).toInt()[0]

            record = InsertableRecord(database, "treatment_fills")

            record.setValue("tooth_tx_id", ix)
            record.setValue("surfaces", self.surfaces)
            record.setValue("material", self.material)

            query, values = record.insert_query

            q_query = QtSql.QSqlQuery(database)
            q_query.prepare(query)
            for value in values:
                q_query.addBindValue(value)
            q_query.exec_()

            if q_query.lastError().isValid():
                error = q_query.lastError()
                database.emit_caught_error(error)
                return False

    def errors(self):
        if self.surfaces_required:
            expected_surfaces = self.parent_item.code.no_surfaces
            n = re.match("\d+", expected_surfaces)
            if n:
                no_surfaces = int(n.group())
                surfs_entered = len(self.surfaces)
                if not (no_surfaces == surfs_entered or
                ("+" in expected_surfaces and surfs_entered > no_surfaces)):
                    return [u"%s (%s %s)"% (
                        _("Incorrect number of surfaces entered"),
                        expected_surfaces, _("required"))]
        return []

    @property
    def brief_description(self):
        return SETTINGS.TOOTHGRID_SHORTNAMES.get(self.tooth)

    @property
    def description(self):
        return self.parent_item.code.description

    def __repr__(self):
        return "%s metadata tooth=%s"% (self.tx_type, self.tooth)

class TreatmentItem(object):
    '''
    .. note::
        this custom data object represents an item of treatment.
        the underlying procedure code can be accessed with TreatmentItem.code

    raises a :doc:`TreatmentItemException` if errors are encountered
    '''
    #:
    SIMPLE = proc_codes.ProcCode.SIMPLE
    #:
    TOOTH = proc_codes.ProcCode.TOOTH
    #:
    TEETH = proc_codes.ProcCode.TEETH
    #:
    ROOT = proc_codes.ProcCode.ROOT
    #:
    FILL = proc_codes.ProcCode.FILL
    #:
    CROWN = proc_codes.ProcCode.CROWN
    #:
    BRIDGE = proc_codes.ProcCode.BRIDGE
    #:
    PROSTHETICS = proc_codes.ProcCode.PROSTHETICS
    #:
    OTHER = proc_codes.ProcCode.OTHER

    def __init__(self, param):
        '''
        *overloaded function*

        :param: QSql.QSqlrecord

        will load values from the Record

        :param: string

        string should be of the form "A01"
        ie. uniquely identify a proc code

        :param: :class:`ProcCode`

        pass in a :doc:`ProcCode` object directly
        '''

        if type(param) == QtSql.QSqlRecord:
            self.qsql_record = param
            param = str(param.value("om_code").toString())
        else:
            #:
            self.qsql_record = None

        if type(param) == types.StringType:
            #:
            self.code = PROCEDURE_CODES[param]
        else:
            self.code = param

        self._px_clinician = None
        self._tx_clinician = None
        self._cmp_date = None
        self._metadata = None

        #:
        self._comment = ""
        #:
        self.is_completed = False

        if self.in_database:
            self._from_record()
        else:
            if SETTINGS.current_practitioner:
                self.set_px_clinician(SETTINGS.current_practitioner.id)

    def _from_record(self):
        '''
        An extension of __init__, loading data from the database
        when initiated by a QSqlRecord.
        '''
        logging.debug("converting QsqlRecord to TreatmentItem")
        self.set_px_clinician(self.qsql_record.value("px_clinician").toInt()[0])
        tx_clinician, valid = self.qsql_record.value("tx_clinician").toInt()
        self.set_comment(unicode(self.qsql_record.value("comment").toString()))
        self.set_completed(self.qsql_record.value("completed").toBool())
        if valid and tx_clinician !=0 :
            self.set_tx_clinician(tx_clinician)
        tx_date = self.qsql_record.value("tx_date").toDate()
        if tx_date:
            self.set_cmp_date(tx_date)

    def _get_metadata(self):
        '''
        poll the database to get metadata associated with this item
        '''
        self._metadata = []
        query = '''select
tooth, tx_type, surfaces, material, type, technition from treatment_teeth
left join treatment_fills  on treatment_fills.tooth_tx_id = treatment_teeth.ix
left join treatment_crowns on treatment_crowns.tooth_tx_id = treatment_teeth.ix
where treatment_teeth.treatment_id = ?
'''
        q_query = QtSql.QSqlQuery(SETTINGS.database)
        q_query.prepare(query)
        q_query.addBindValue(self.id)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()

            treatment_item_metadata = TreatmentItemMetadata(self, record)
            self._metadata.append(treatment_item_metadata)

    def add_metadata(self):
        '''
        create a new :doc:`TreatmentItemMetadata` object and append to this
        treatment item.
        note - returns the item so that values can be set

        .. typical useage::
            metadata = TreatmentItem().add_metadata()
            metadata.set_tooth(18)
            metadata.set_type("splint")

        '''
        t_i_meta = TreatmentItemMetadata(self)
        self.metadata.append(t_i_meta)

        return t_i_meta

    @property
    def metadata(self):
        '''
        returns a list of all :doc:`TreatmentItemMetadata` objects
        '''
        if self._metadata is None:
            if self.in_database:
                self._get_metadata()
            else:
                self._metadata = []
        return self._metadata

    @property
    def id(self):
        '''
        returns the primary key of the treatments table for this item,
        or None if the item is not in the database
        '''
        return None if not self.in_database else self.qsql_record.value("ix")

    def set_cmp_date(self, date=QtCore.QDate.currentDate()):
        '''
        :param: date

        sets the item as completed, on date date
        '''
        self.set_completed()
        self._cmp_date = date

    @property
    def in_database(self):
        '''
        returns true if the item is in the database
        if it is, then it will have a valid :attr:`qsql_record` .
        '''
        return self.qsql_record != None

    @property
    def cmp_date(self):
        '''
        date the item was completed (returns None if tx incomplete)
        '''
        return self._cmp_date

    @property
    def tooth_required(self):
        '''
        returns True if this code needs tooth metadata (some don't)
        '''
        return self.code.tooth_required and self.metadata == []

    @property
    def type(self):
        return self.code.type

    @property
    def is_chartable(self):
        '''
        a bool indicating whether this treatment item can be represented
        on a dental chart.
        example, an examination is not, but a filling in the UR5 is
        '''
        for data in self.metadata:
            if data.is_chartable:
                return True
        return False

    @property
    def is_bridge(self):
        return self.code.is_bridge

    @property
    def is_prosthetics(self):
        return self.code.is_prosthetics

    @property
    def category(self):
        return self.code.category

    @property
    def description(self):
        return self.code.description

    @property
    def comment(self):
        '''
        any comment made by the user
        '''
        return self._comment

    @property
    def pontics(self):
        '''
        a list of all metadata items which are pontics
        '''
        pontics = []
        for data in self.metadata:
            if data.is_pontic:
                pontics.append(data)
        return pontics

    @property
    def abutments(self):
        '''
        a list of all metadata items which are bridge abutments
        '''
        abutments = []
        for data in self.metadata:
            if data.is_abutment:
                abutments.append(data)
        return abutments

    @property
    def allowed_pontics(self):
        '''
        which teeth are acceptable as pontics
        eg upper partial pontics should be in range(1,18)
        '''
        return self.code.allowed_pontics

    @property
    def further_info_needed(self):
        return self.code.further_info_needed

    @property
    def pontics_required(self):
        return self.code.pontics_required

    @property
    def total_span(self):
        return self.code.total_span

    @property
    def surfaces_required(self):
        for data in self.metadata:
            if data.surfaces != "":
                return False
        return self.code.surfaces_required

    @property
    def comment_required(self):
        return self.code.comment_required

    def clear_metadata(self):
        '''
        reset the metadata
        '''
        self._metadata = []

    def set_teeth(self, teeth):
        '''
        :param: [int, int, int...]

        ints should comply with :doc:`../../misc/tooth_notation`
        '''
        #print "setting teeth", teeth
        for tooth in teeth:
            metadata = self.add_metadata()
            metadata.set_tooth(tooth)

    def set_abutments(self, teeth):
        '''
        :param: list of pontics [int, int, int...]

        ints should comply with :doc:`../../misc/tooth_notation`
        '''
        for tooth in teeth:
            metadata = self.add_metadata()
            metadata.set_tooth(tooth)
            metadata.set_tx_type("abutment")

    def set_pontics(self, pontics):
        '''
        :param: list of pontics [int, int, int...]

        ints should comply with :doc:`../../misc/tooth_notation`
        '''
        #print "setting pontics %s"% pontics
        if self.pontics_required:
            for pontic in pontics:
                metadata = self.add_metadata()
                metadata.set_tooth(pontic)
                metadata.set_tx_type("pontic")

    def set_surfaces(self, surfaces):
        for data in self.metadata:
            data.set_surfaces(surfaces)

    def set_comment(self, comment):
        '''
        :param: string

        '''
        self._comment = comment

    def set_completed(self, completed=True):
        '''
        :kword: completed=bool
        '''
        self.is_completed = completed

    def set_px_clinician(self, clinician_id):
        '''
        :param: clinician_id (int)

        .. note::
            who prescribed this treatment
            int should be the unique id of a clinician
        '''

        assert (clinician_id is None or
        type(clinician_id) == types.IntType), "error setting_px_clinician"

        self._px_clinician = clinician_id

    def set_tx_clinician(self, clinician_id):
        '''
        :param: clinician_id (int)

        .. note::
            who prescribed this treatment
            int should be the unique id of a clinician
        '''
        assert (clinician_id is None or
        type(clinician_id) == types.IntType), "error setting_tx_clinician"
        self._tx_clinician = clinician_id

    @property
    def px_clinician(self):
        '''
        the unique id of a clinician who prescribed the treatment
        '''
        return self._px_clinician

    @property
    def tx_clinician(self):
        '''
        the unique id of a clinician who performed the treatment
        '''
        return self._tx_clinician

    @property
    def allow_multiple_teeth(self):
        '''
        True if this treatment can related to multiple teeth

        .. note::
            an example would be a periodontal splint
        '''
        return self.is_bridge or self.is_prosthetics or self.type == self.TEETH

    @property
    def required_span(self):
        '''
        how many units should this be if it is to be a bridge?
        returns an integer or None
        '''
        expected_span = str(self.total_span)
        n = re.match("\d+", expected_span)
        if n:
            return int(n.group())

    @property
    def entered_span(self):
        '''
        returns the entered total span of a bridge (if this is a bridge)
        '''
        return len(self.pontics) + len(self.abutments)

    @property
    def is_valid(self):
        return self.check_valid()[0]

    @property
    def errors(self):
        '''
        convenience function to get the errors for this item (if any)
        '''
        return self.check_valid()[1]

    def check_valid(self):
        '''
        a tuple (valid, errors),
        where valid is a boolean, and errors a list of errors

        check to see that the item has all the attributes required by the
        underlying procedure code

        .. note::
            our 3 surface filling will need to know tooth and surfaces
            returns a tuple (valid, errors),
            where valid is a boolean, and errors a list of errors
        '''
        errors = []
        if self.tooth_required and not self.metadata:
            errors.append(_("No Tooth Selected"))

        if self.pontics_required and self.pontics == []:
            errors.append(_("No Pontics Selected"))

        if self.px_clinician is None:
            errors.append(_("Unknown Prescribing Clinician"))

        if self.is_completed and self.tx_clinician is None:
            errors.append(_("Unknown Treating Clinician"))

        if self.is_completed and self.cmp_date is None:
            errors.append(_("Unknown Completion Date"))

        if self.is_bridge:
            entered, required = self.entered_span, self.required_span
            if not ( entered == required or
            ("+" in self.total_span and entered > required)):

                errors.append(u"%s (%s %s - %s %s)"% (
                    _("Incorrect Bridge Span"),
                    required, _("units required"),
                    entered, _("entered")))

        for pontic in self.pontics:
            if not pontic.tooth in self.allowed_pontics:
                errors.append("invalid pontic (%s)"% (
                    SETTINGS.TOOTHGRID_LONGNAMES[pontic.tooth]))

        for data in self.metadata:
            errors += data.errors()

        if self.comment_required and self.comment == "":
            errors.append(_("A comment is required"))

        return (errors==[], errors)

    def commit_to_db(self, database):
        '''
        :param: database

        write this item to the database

        will raise an exception if item is not :func:`is_valid`

        '''

        valid, reason = self.check_valid()
        if not valid:
            raise Exception, "Invalid Treatment Item <hr />%s"% reason

        record = InsertableRecord(database, "treatments")

        record.setValue("patient_id", SETTINGS.current_patient.patient_id)
        record.setValue("om_code", self.code.code)
        record.setValue("completed", self.is_completed)
        record.setValue("px_clinician", self.px_clinician)
        record.setValue("tx_clinician", self.tx_clinician)
        record.setValue("px_date", QtCore.QDate.currentDate())
        record.setValue("tx_date", self.cmp_date)
        record.setValue("added_by", SETTINGS.user)
        record.setValue("comment", self.comment)

        query, values = record.insert_query

        q_query = QtSql.QSqlQuery(database)
        q_query.prepare(query+ " returning ix")
        for value in values:
            q_query.addBindValue(value)
        q_query.exec_()

        if q_query.lastError().isValid():
            logging.error(query)
            error = q_query.lastError()
            database.emit_caught_error(error)
            return False

        q_query.first()
        ix = q_query.value(0).toInt()[0]

        for data in self.metadata:
            data.commit_db(database, ix)

        return True


    def __repr__(self):
        item = '''TreatmentItem
        code='%s'
        completed='%s' date='%s' in_db='%s'
        '''% (
                self.code,
                self.is_completed, self.cmp_date,
                self.in_database,
                )
        return item

    def __cmp__(self, other):
        try:
            return cmp(self.code, other.code)
        except AttributeError as e:
            return -1


if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)

