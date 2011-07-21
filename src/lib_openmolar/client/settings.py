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

from lib_openmolar.common import settings

from lib_openmolar.client import classes
from lib_openmolar.client.scripts import dent_key
from lib_openmolar.client.qt4gui.colours import colours

from lib_openmolar.client.db_orm import TreatmentModel
from lib_openmolar.client.db_orm.client_practitioner import Practitioners
from lib_openmolar.client.db_orm.client_staff_members import StaffMembers
from lib_openmolar.client.db_orm.client_users import Users

import inspect, os, sys, traceback, zipfile, zipimport

class SettingsError(Exception):
    '''
    A custom exception
    '''
    def __init__(self, value="Unknown"):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Settings(settings.CommonSettings):
    def __init__(self):
        settings.CommonSettings.__init__(self)

        #: a reference to a :doc:`TeethPresentDecoder`
        self.tooth_decoder = dent_key.TeethPresentDecoder()

        #: who is using the system
        self.user = "UNKNOWN"

        #: who is logged in as user1
        self.user1 = None

        #: and assistant
        self.user2 = None

        #: a pointer to the :doc:`ClientConnection` in use
        self.database = None

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

    def get_pluggable_classes(self, module):
        '''
        Args:
            module (module object)

        generates a list of all classes which are subclassed
        from lib_openmolar.client.Plugin in the module "module"
        '''

        for name in dir(module):
            obj = getattr(module, name)
            ## check is this object is a class.. and that it inherits
            ## from Plugin.. (but is not the Plugin base class itself!)
            ## hence issubclass wouldn't work
            if inspect.isclass(obj) and classes.Plugin in obj.mro()[1:]:
                klass = obj()
                yield klass

    def get_modules(self, plugin_dir):
        '''
        finds all modules in plugin_dir
        '''
        sys.path.insert(0, str(plugin_dir))
        for file_ in os.listdir(str(plugin_dir)):
            full_path = os.path.join(str(plugin_dir), file_)

            if file_.endswith(".py"):
                self.log("NAKED PLUGIN FOUND", full_path)
                if self.PERSISTANT_SETTINGS.get("compile_plugins", False):
                    module = file_.replace('.py','')
                    mod = __import__(module)
                    yield mod
                else:
                    self.log ('NOT COMPILING',
                        "(as you have naked plugins disabled)")
            elif zipfile.is_zipfile(full_path):
                module = file_.replace('.zip','')
                try:
                    z = zipimport.zipimporter(full_path)
                    mod = z.load_module(module)
                    yield mod
                except (zipimport.ZipImportError, zipfile.BadZipfile) as e:
                    self.log ("incompatible plugin", filepath)

    def get_plugins(self, plugin_dir):
        '''
        peruses a directory and finds all plugins
        '''
        i = 0
        for mod in self.get_modules(plugin_dir):
            plugins = self.get_pluggable_classes(mod)
            for plugin in plugins:
                self.install_plugin(plugin)
                i += 1
        return i

    def verbose_exception(self):
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()

        readable_ex =   traceback.format_exception(
            exceptionType, exceptionValue, exceptionTraceback)

        message = u"%s\n\n"% _(
            "exception loading plugin- please file a bug")

        for line in readable_ex:
            message += "%s\n" % line

        self.log (message)

    def load_plugins(self):
        '''
        this function is called by the client application to load plugins
        '''
        self.log ("loading plugins...")
        i = 0
        for plugin_dir in self.PLUGIN_DIRS:
            self.log ("looking in", plugin_dir, "for plugins")

            try:
                i += self.get_plugins(plugin_dir)

            except Exception as e:
                self.log ("Exception loading plugin")
                self.verbose_exception()

        self.log (str(i), "plugin(s) loaded")

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
        SETTINGS.log("setting user1 as %s"% user)
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
        self.log("setting current patient - %s"% patient)

    @property
    def current_patient(self):
        '''
        a pointer to the currently loaded patient
        '''
        return self._current_patient

    def install_plugin(self, plugin):
        '''
        installs a plugin (of type BasePlugin)
        '''
        if plugin.TYPE == plugin.FEE_SCALE:
            self.install_fee_scale(plugin)

        try:
            plugin.setup_plugin()
        except Exception, e:
            print "Exception during plugin.setup_plugin", plugin.name
            self.verbose_exception()

        self._plugins.append(plugin)

    @property
    def plugins(self):
        '''
        a list of all plugins (of type BasePlugin)
        '''
        return self._plugins

    def install_fee_scale(self, fee_scale):
        '''
        installs a fee_scale (of type BasePlugin)
        '''
        self.log ("installing fee_scale", fee_scale)
        self._fee_scales.append(fee_scale)

    @property
    def fee_scales(self):
        '''
        a list of all fee_scales installed (fee_scale = a type of BasePlugin)
        '''
        return sorted(self._fee_scales)

def install():
    '''
    make an instance of this object acessible in the global namespace
    >>>
    '''
    import __builtin__
    __builtin__.__dict__["SETTINGS"] = Settings()

if __name__ == "__main__":

    install()
    print SETTINGS.PROCEDURE_CODES
    print SETTINGS.OM_TYPES
    print SETTINGS.tooth_decoder.decode(23456)

    print SETTINGS.allowed_crown_types
