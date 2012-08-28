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
Provides custom postgres "enum" types used in the openmolar database
'''

class OMType(object):
    '''
    custom postgres data type creator
    '''
    def __init__(self, name):
        #:
        self.name = name

        #:
        self.allowed_values = []

        #:
        self.readable_dict = {}

        self._default = None

    def allow(self, val, readable):
        self.allowed_values.append(val)
        self.readable_dict[val] = readable

    @property
    def selections(self):
        '''
        values as required for combobox selection
        '''
        selections = []
        for val in sorted(self.allowed_values):
            selections.append(self.readable_dict[val])
        return selections

    @property
    def default(self):
        '''
        the value to use as a default
        returns None by default
        '''
        return self._default

    def set_default(self, default):
        assert default in self.allowed_values, (
            "%s is not in allowed values for this type"% default)

        self._default = default

    @property
    def creation_queries(self):
        '''
        a list of queries to register this type in the database
        '''
        if self.allowed_values == []:
            return []
        allowed_value_list = ""
        for val in self.allowed_values:
            allowed_value_list += "'%s', "% val
        allowed_value_list = allowed_value_list.rstrip(", ")
        sql = "CREATE TYPE %s AS ENUM (%s)"% (self.name, allowed_value_list)
        return [sql]

    @property
    def removal_queries(self):
        '''
        a list of queries to remove this type from the database
        '''
        sql = "DROP TYPE IF EXISTS %s CASCADE"% self.name
        return [sql]

    def translate(self, val):
        '''
        returns a translated version of the key
        '''
        return self.translation_dict.get(val, val)

    def __repr__(self):
        return u"OMType object - %s %s default=%s"% (
            self.name, self.allowed_values, self.default)

class OMTypes(object):
    '''
    a container for the custom data types used in openmolar
    '''
    _dict = {}
    __getitem__ = _dict.__getitem__
    __setitem__ = _dict.__setitem__
    values = _dict.values
    get = _dict.get

    def __init__(self):

        new_type = OMType("sex_type")
        new_type.allow(u'M', _('Male'))
        new_type.allow(u'F', _('Female'))
        self["sex"] = new_type

        new_type = OMType("pt_status_type")
        new_type.allow(u'unknown', _('Unknown')) #often the case with imported data
        new_type.allow(u'active', _('Active'))
        new_type.allow(u'banned', _('Banned'))
        new_type.allow(u'bad_debt', _('Bad Debt'))
        new_type.allow(u'casual', _('Casual'))
        new_type.allow(u'deceased', _('Deceased'))
        new_type.allow(u'moved away', _('Moved Away'))
        new_type.set_default("unknown")
        self["pt_status"] = new_type

        new_type = OMType("address_type")
        new_type.allow(u'home', _('Home'))
        new_type.allow(u'work', _('Work'))
        new_type.allow(u'holiday', _('On Holiday'))
        new_type.allow(u'care_of', _('c/o'))
        new_type.allow(u'student_accomodation', _('Student Accomodation'))
        new_type.allow(u'other', _('Other'))
        new_type.set_default("home")
        self["address"] = new_type

        new_type = OMType("mailing_pref_type")
        new_type.allow(u'default', _('Preferred Mailing address'))
        new_type.allow(u'dont_use', _('Do Not Use!'))
        new_type.allow(u'duplicate', _('Copy all mail to this address also'))
        new_type.allow(u'other', _('Other'))
        new_type.set_default("default")
        self["mailing_pref"] = new_type

        new_type = OMType("telephone_type")
        new_type.allow(u'home', _('Home'))
        new_type.allow(u'work', _('Work'))
        new_type.allow(u'mobile', _('Mobile'))
        new_type.allow(u'other', _('Other'))
        new_type.set_default("home")
        self["telephone"] = new_type

        new_type = OMType("root_description_type")
        new_type.allow(u'normal', "")
        new_type.allow(u'UNKNOWN', _('Unknown status'))
        new_type.allow(u'TM', _('Missing'))
        new_type.allow(u'RT', _('Root Treated'))
        new_type.allow(u'CA', _('Congenitally absent'))
        new_type.allow(u'UE', _('Present but Unerupted'))
        new_type.allow(u'PE', _('Partially Erupted'))
        new_type.allow(u'AP', _('Apicected'))
        new_type.allow(u'IMPACT_H', _('Horizontally Impacted'))
        new_type.allow(u'IMPACT_V', _('Vertically Impacted'))
        new_type.allow(u'IMPACTED', _('Impacted'))
        new_type.allow(u'FRAG_BURIED', _('Buried Fragment'))
        new_type.allow(u'FRAG_EXPOSED', _('Visible Fragment'))
        new_type.allow(u'OD', _('Overdenture Abutment'))
        new_type.allow(u'HEMI', _('Hemisected'))
        new_type.allow(u'IM', _('Titanium Implant'))
        new_type.allow(u'IM_OT', _('Other Implant'))
        new_type.allow(u'OT', _('Other Root Type'))
        new_type.set_default("normal")

        self["root_description"] = new_type

        new_type = OMType("fill_material_type")
        new_type.allow(u'AM', _('Amalgam'))
        new_type.allow(u'CO', _('Composite Resin'))
        new_type.allow(u'GL', _('Glass Ionomer'))
        new_type.allow(u'GO', _('Gold'))
        new_type.allow(u'PO', _('Porcelain'))
        new_type.allow(u'SI', _('Silicate'))
        new_type.allow(u'FS', _('Fissure Sealant'))
        new_type.allow(u'DR', _('Dressing'))
        new_type.allow(u'PR', _('Preventive Resin'))
        new_type.allow(u'OT', _('Other Material'))
        new_type.set_default("OT")
        self["fill_material"] = new_type

        #note - these MUST be matched in the proc-codes resource file
        new_type = OMType("crown_type")
        new_type.allow(u'PJ', _('Porcelain Jacket Crown'))
        new_type.allow(u'PV', _('Porcelain Veneer'))
        new_type.allow(u'V1', _('Porcelain / Precious Metal'))
        new_type.allow(u'V2', _('Porcelain / Non Precious Metal'))
        new_type.allow(u'GO', _('Gold'))
        new_type.allow(u'A1', _('Precious Metal Crown'))
        new_type.allow(u'A2', _('Non-precious Metal Crown'))
        new_type.allow(u'TEMP', _('Temporary Crown'))
        new_type.allow(u'SS', _('Stainless Steel'))
        new_type.allow(u'LAVA', _('3M Lava'))
        new_type.allow(u'OPAL', _('Opalite'))
        new_type.allow(u'FORT', _('Fortress'))
        new_type.allow(u'E-MAX', _('E-Max'))
        new_type.allow(u'EVER', _('Everest'))
        new_type.allow(u'SR', _('Resin'))
        new_type.allow(u'OT', _('Other'))
        new_type.set_default("OT")
        self["crowns"] = new_type

        new_type = OMType("notes_clinical_type")
        new_type.allow(u'observation', _('Observation'))
        new_type.allow(u'diagnosis', _('Diagnosis'))
        new_type.allow(u'recommendation', _('Recommendation'))
        new_type.allow(u'treatment', _('Treatment'))
        new_type.set_default("observation")
        self["notes_clinical"] = new_type

        new_type = OMType("notes_clerical_type")
        new_type.allow(u'observation', _('Observation'))
        new_type.allow(u'payment', _('Payment'))
        new_type.allow(u'printing', _('Printing'))
        new_type.allow(u'invoice', _('Invoice'))
        new_type.allow(u'appointment', _('Appointment'))
        new_type.set_default("observation")
        self["notes_clerical"] = new_type

        new_type = OMType("procedure_info_type")
        new_type.allow(u'any_tooth', _('Please Select a Tooth'))
        new_type.allow(u'multi_teeth', _('Please Select involved Teeth'))
        new_type.allow(u'any_deciduous_tooth', _('Please Select a Deciduous Tooth'))
        new_type.allow(u'any_adult_tooth', _('Please Select an Adult Tooth'))
        new_type.allow(u'any_quadrant', _('Please select a Quadrant'))
        new_type.allow(u'any_sextant', _('Please select any Sextant'))
        new_type.allow(u'posterior_sextant', _('Please select a Posterior Sextant'))
        new_type.allow(u'anterior_sextant', _('Please select an Anterior Sextant'))
        new_type.set_default("any_tooth")
        self["procedure_info"] = new_type

        new_type = OMType("diary_type")
        new_type.allow(u'free time', _('Free Time'))
        new_type.allow(u'out of office', _('Out of Office'))
        new_type.allow(u'emergency', _('Emergency'))
        new_type.allow(u'lunch', _('Lunch'))
        new_type.allow(u'appointment', _('Appointment'))
        self["diary"] = new_type

        new_type = OMType("clinician_type")
        new_type.allow(u'dentist', _('Dentist'))
        new_type.allow(u'hygienist', _('Hygienist'))
        new_type.allow(u'therapist', _('Therapist'))
        new_type.allow(u'technition', _('Technition'))
        new_type.allow(u'orthodontist', _('Orthodontist'))
        new_type.allow(u'endodontist', _('Endodontist'))
        new_type.allow(u'implantologist', _('Implantologist'))
        new_type.allow(u'ohi_instructor', _('Oral Hygiene Instructor'))
        new_type.allow(u'dentist|hygienist', _('Dentist or Hygienist'))
        new_type.allow(u'dentist|therapist', _('Dentist or Therapist'))
        new_type.allow(u'dentist|hygienist|therapist',
            _('Dentist or Hygienist or Therapist'))
        new_type.allow(u'hygienist|therapist', _('Hygienist or Therapist'))
        self['clinician_type'] = new_type

        new_type = OMType("practitioner_type")
        new_type.allow(u'dentist', _('Dentist'))
        new_type.allow(u'hygienist', _('Hygienist'))
        new_type.allow(u'therapist', _('Therapist'))
        self['practitioner_type'] = new_type

        new_type = OMType("fee_type")
        new_type.allow(u'treatment', _('Treatment'))
        new_type.allow(u'sundries', _('Sundries'))
        new_type.allow(u'deposit', _('Deposit'))
        new_type.allow(u'fta_charge', _('Failed Appointment Charge'))
        new_type.allow(u'other', _("Other"))
        self["fee_type"] = new_type

        new_type = OMType("tx_chart_type")
        new_type.allow(u'root', _("root"))
        new_type.allow(u'tooth', _("tooth"))
        self["tx_chart_type"] = new_type

        # for use in the treatments_teeth table
        new_type = OMType("tooth_tx_type")
        new_type.allow(u'abutment', _("abutment"))
        new_type.allow(u'pontic', _("pontic"))
        new_type.allow(u'wing', _("wing"))
        new_type.allow(u'filling', _("filling"))
        self["tooth_tx_type"] = new_type

if __name__ == "__main__":
    import gettext
    gettext.install("openmolar")

    OM_TYPES = OMTypes()
    for om_type in OM_TYPES.values():
        print om_type