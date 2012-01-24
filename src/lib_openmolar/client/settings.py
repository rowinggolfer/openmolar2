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

import logging
import os

from lib_openmolar.common import settings

from lib_openmolar.client.classes import PluginHandler
from lib_openmolar.client.scripts import dent_key
from lib_openmolar.client.qt4.colours import colours

from lib_openmolar.client.db_orm import TreatmentModel
from lib_openmolar.client.db_orm.client_practitioner import Practitioners
from lib_openmolar.client.db_orm.client_staff_members import StaffMembers
from lib_openmolar.client.db_orm.client_users import Users

from PyQt4.QtCore import QResource

class SettingsError(Exception):
    '''
    A custom exception
    '''
    def __init__(self, value="Unknown"):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Settings(settings.CommonSettings, PluginHandler):
    #: an html image tag showing a pencil
    PENCIL = '<img class="pencil" alt ="edit" src="qrc:/icons/pencil.png" />'

    LOCALFOLDER = os.path.join(os.environ.get("HOME", ""), ".openmolar2")

    _CSS = {}

    def __init__(self):
        settings.CommonSettings.__init__(self)

        if not os.path.exists(self.LOCALFOLDER):
            os.mkdir(self.LOCALFOLDER)

        #: a reference to a :doc:`TeethPresentDecoder`
        self.tooth_decoder = dent_key.TeethPresentDecoder()

        #: who is using the system
        self.user = "UNKNOWN"

        #: who is logged in as user1
        self.user1 = None

        #: and assistant
        self.user2 = None

        #: a pointer to the :doc:`ClientConnection` in use
        self.psql_conn = None

        #: an enumeration of chart styles
        self.chart_styles = (
            (_("Mixed"), 1),
            (_("Deciduous"), 2),
            (_("Adult Simple"), 3),
            (_("Adult Complex"), 4),
            (_("Adult Complex PLUS"), 4.5),
            (_("Roots Only"), 5),
            (_("Perio Chart"), 6),
            )

        #: initially this is "Adult Complex"
        self.default_chart_style = 4

        #: only adult rows, as per style 4
        self.visible_chart_rows = (1,2)

        #: colours for fillings
        self.fill_materials = (
            ("?", colours.UNKNOWN),
            ("AM", colours.AMALGAM),
            ("CO", colours.COMPOSITE),
            ("GL", colours.GLASS),
            ("PO", colours.PORCELAIN),
            ("GO", colours.GOLD)
            )

        #: a reference to the :doc:`ClientMainWindow` for plugin use
        self.mainui = None

        #: locations of directories where plugins reside
        self.PLUGIN_DIRS = []

        self._plugins = []
        self._fee_scales = []
        self._current_patient = None
        self._current_practitioner = None
        self._practitioners = None
        self._treatment_model = None
        self._staff = None
        self._users = None
        self._last_known_address = None

        self.init_css()

    def init_css(self):
        '''
        look for the presence of custom css files
        '''

        for css in ("notes", "details"):
            custom_loc = os.path.join(self.LOCALFOLDER, "custom_%s.css"% css)

            if os.path.exists(custom_loc):
                print "WARNING: using a custom css file - %s"% custom_loc
                self._CSS[css] = custom_loc
            else:
                self._CSS[css] = os.path.join(self.LOCALFOLDER, "%s.css"% css)

            #ensure that we have a css file.. otherwise the notes will be awful!
            if not os.path.exists(self._CSS[css]):
                print "initiating a new css file - %s"% self._CSS[css]
                resource = QResource(":css/notes.css")
                f = open(self._CSS[css], "w")
                f.write(resource.data())
                f.close()

    @property
    def VERSION(self):
        try:
            from lib_openmolar.client import version
            VERSION = "Client version %s~hg%s"% (
                version.VERSION, version.revision_number)
            from lib_openmolar.common import version
            VERSION += "\nCommon version %s~hg%s"% (
                version.VERSION, version.revision_number)
        except ImportError:
            VERSION = "Unknown"
            LOGGER.exception("unable to parse for client versioning")
        LOGGER.info("VERSION %s"% VERSION)
        return VERSION

    @property
    def NOTES_CSS(self):
        '''
        location of the notes css file for the current OS user.

        .. note::
            this will usually be
            ~/.openmolar2/notes.css (which is generated if not present)
            or ~/.openmolar2/custom_notes.css (user edited file)
        '''
        return "file://%s"% self._CSS.get("notes", "")

    @property
    def DETAILS_CSS(self):
        '''
        location of the notes css file for the current OS user.

        .. note::
            this will usually be
            ~/.openmolar2/details.css (which is generated if not present)
            or ~/.openmolar2/custom_details.css (user edited file)
        '''
        return "file://%s"% self._CSS.get("details", "")

    @property
    def users(self):
        if self._users is None:
            self._users = Users()
        return self._users

    @property
    def practitioners(self):
        if self._practitioners is None:
            self._practitioners = Practitioners()
        return self._practitioners

    @property
    def staff_members(self):
        if self._staff is None:
            self._staff = StaffMembers()
        return self._staff

    @property
    def treatment_model(self):
        if self._treatment_model is None:
            self._treatment_model = TreatmentModel()
        return self._treatment_model

    @property
    def allowed_fill_materials(self):
        for mat, color in self.fill_materials:
            yield mat

    @property
    def allowed_crown_types(self):
        '''
        can't be a generator.. because indexing is used for the default value
        ie. allowed_crown_types[-1]
        '''
        return self.OM_TYPES["crowns"].allowed_values

    @property
    def allowed_root_types(self):
        '''
        can't be a generator.. because indexing is used for the default value
        ie. allowed_root_types[-1]
        '''
        return self.OM_TYPES["root_description"].allowed_values

    @property
    def last_used_address(self):
       return self._last_known_address

    def set_last_used_address(self, address):
        self._last_known_address = address

    def month_name(self, d):
        '''
        expects a qdatetime object, returns the month
        '''
        try:
            return self.MONTH_NAMES[d.month()-1]
        except IndexError:
            return "?month?"

    def set_user1(self, user):
        LOGGER.info("setting user1 as %s"% user)
        self.user1 = user
        try:
            practitioner = self.practitioners.practitioner_from_user(user)
            self.set_current_practitioner(practitioner)
        except SettingsError:
            print "unable to set %s as practitioner"% user

    def set_user2(self, user):
        self.user2 = user

    @property
    def current_practitioner(self):
        return self._current_practitioner

    def set_current_practitioner(self, practitioner):
        '''
        set the current practitioner
        this means other modules can always access this important object
        '''
        if not practitioner in self.practitioners:
            self._current_practitioner = None
            raise SettingsError, \
                "An attempt was made to set a non-valid practitioner"
        self._current_practitioner = practitioner


    def set_current_patient(self, patient):
        '''
        set the currently loaded patient
        this means other modules can always access this important object
        '''
        self._current_patient = patient
        LOGGER.debug("setting current patient - %s"% patient)

    @property
    def current_patient(self):
        '''
        a pointer to the currently loaded patient
        '''
        return self._current_patient

    @property
    def connections(self):
        '''
        TODO - populate this list!!
        '''
        return []

def install():
    '''
    make an instance of this object acessible in the global namespace
    >>>
    '''
    import __builtin__
    __builtin__.__dict__["SETTINGS"] = Settings()

if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG)

    install()
    print SETTINGS.PROCEDURE_CODES
    print SETTINGS.OM_TYPES
    print SETTINGS.tooth_decoder.decode(23456)

    print SETTINGS.allowed_crown_types
    SETTINGS.VERSION
