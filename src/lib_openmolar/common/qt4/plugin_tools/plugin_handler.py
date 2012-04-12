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

import inspect
import logging
import os
import sys
import zipfile
import zipimport

from lib_openmolar.common.qt4.plugin_tools import Plugin

from PyQt4.QtCore import QResource, QString

class PluginHandler(object):
    '''
    A class to verify and install plugins
    '''
    #: locations of directories where plugins reside
    PLUGIN_DIRS = []

    #: locations of directories where naked plugins reside
    NAKED_PLUGIN_DIRS = []

    #:
    ACTIVE_PLUGINS = set([])

    _plugins = []
    _fee_scales = []

    def get_pluggable_classes(self, module, target=None):
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
            if inspect.isclass(obj) and Plugin in obj.mro()[1:]:
                try:
                    LOGGER.debug("initiating plugin object %s"% obj)
                    klass = obj()
                except Exception: # shouldn't happen!!
                    LOGGER.exception(
                    "Unable to instantiate Plugin %s from %s"% (obj, module))
                    continue
                if target is None or klass.TARGET == target:
                    yield klass
                else:
                    LOGGER.error("Plugin %s has target '%s' ignoring"% (
                    klass.name, klass.TARGET))

    def get_modules(self, plugin_dir):
        '''
        finds all modules in plugin_dir
        '''
        sys.path.insert(0, str(plugin_dir))
        for file_ in os.listdir(str(plugin_dir)):
            full_path = os.path.join(str(plugin_dir), file_)

            if file_.endswith(".py"):
                LOGGER.debug("found module '%s'"% full_path)
                if plugin_dir in self.NAKED_PLUGIN_DIRS:
                    LOGGER.info("NAKED PLUGIN FOUND '%s'"% full_path)
                    module = file_.replace('.py','')
                    mod = __import__(module)
                    yield mod
                else:
                    LOGGER.info(
            'IGNORING because %s is not a known store for naked plugins'%
                    plugin_dir)
            elif zipfile.is_zipfile(full_path):
                LOGGER.info("POSSIBLE PLUGIN FOUND '%s'"% full_path)
                module = file_.replace('.zip','')
                try:
                    z = zipimport.zipimporter(full_path)
                    mod = z.load_module(module)
                    yield mod
                except (zipimport.ZipImportError, zipfile.BadZipfile) as e:
                    LOGGER.exception ("incompatible plugin '%s'"% full_path)

    def get_plugins(self, plugin_dir, target=None):
        '''
        peruses a directory and finds all plugins
        '''
        for mod in self.get_modules(plugin_dir):
            plugins = self.get_pluggable_classes(mod, target)
            for plugin in plugins:
                plugin.set_unique_id(QString(
                "%s:%s"% (mod.__name__, os.path.abspath(str(plugin_dir)))))
                self._plugins.append(plugin)

    def load_plugins(self, target=None):
        '''
        this function is called by the client application to load plugins
        '''
        LOGGER.info ("loading plugins...")
        for plugin_dir in self.PLUGIN_DIRS:
            LOGGER.info ("="*80)
            LOGGER.info ("looking for plugins in directory %s"% plugin_dir)
            LOGGER.info ("="*80)
            try:
                self.get_plugins(plugin_dir, target)
            except Exception as e:
                LOGGER.exception ("Exception loading plugin")

        LOGGER.info("%d plugin(s) loaded"% len(self.plugins))

    def activate_plugins(self):
        '''
        iterates over the loaded plugins and activates them.
        '''
        LOGGER.info ("="*80)
        LOGGER.info("Activating plugins")
        LOGGER.info ("="*80)
        i = 0
        for plugin in self.plugins:
            if plugin.unique_id in self.ACTIVE_PLUGINS:
                self.activate_plugin(plugin)
                i += 1
            else:
                LOGGER.debug(".. NOT ACTIVATING %s"% plugin.unique_id)
        LOGGER.info("%d plugin(s) activated"% i)
    
    def de_activate_plugins(self):
        '''
        iterates over the activated plugins and de-activates them.
        '''
        LOGGER.info ("="*80)
        LOGGER.info("De-Activating plugins")
        LOGGER.info ("="*80)
        i = 0
        for plugin in self.plugins:
            if plugin.is_active:
                self.deactivate_plugin(plugin)
                i += 1
        LOGGER.info("%d plugin(s) de-activated"% i)
    
    def activate_plugin(self, plugin):
        LOGGER.info("..Activating %s '%s'"% (plugin.__module__, plugin.name))
        try:
            if plugin.TYPE == plugin.FEE_SCALE:
                self.install_fee_scale(plugin)
            LOGGER.debug("setting up plugin %s"% plugin)
            plugin.setup_plugin()
            plugin.is_active = True
        except Exception, e:
            LOGGER.exception(
            "Exception during plugin.setup_plugin '%s'"% plugin.name)

        self.ACTIVE_PLUGINS.add(plugin.unique_id)

    def deactivate_plugin(self, plugin):
        LOGGER.info("..Deactivating %s '%s'"% (plugin.__module__, plugin.name))
        if plugin.TYPE == plugin.FEE_SCALE:
            self.remove_fee_scale(plugin)
        try:
            LOGGER.debug("calling teardoown plugin %s"% plugin)
            plugin.tear_down()
        except Exception, e:
            LOGGER.exception(
            "Exception during plugin.teardown '%s'"% plugin.name)

        self.ACTIVE_PLUGINS.remove(plugin.unique_id)
        plugin.is_active = False

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
        LOGGER.info ("installing fee_scale %s"% fee_scale)
        self._fee_scales.append(fee_scale)

    def remove_fee_scale(self, fee_scale):
        '''
        removes a fee_scale (of type BasePlugin)
        '''
        LOGGER.info ("removing fee_scale %s"% fee_scale)
        self._fee_scales.remove(fee_scale)

    @property
    def fee_scales(self):
        '''
        a list of all fee_scales installed (fee_scale = a type of BasePlugin)
        '''
        return sorted(self._fee_scales)

if __name__ == "__main__":
    import lib_openmolar.client
    logging.basicConfig(level = logging.DEBUG)
    ph = PluginHandler()
    ph.PLUGIN_DIRS = [
            "/home/neil/openmolar/hg_openmolar/plugins/src/import_om1",
            #"/home/neil/openmolar/hg_openmolar/plugins/src"
            ]
    ph.NAKED_PLUGIN_DIRS = [
            "/home/neil/openmolar/hg_openmolar/plugins/src/import_om1",
            ]
    ph.ACTIVE_PLUGINS = set([QString(
    "import_om1_plugin:/home/neil/openmolar/hg_openmolar/plugins/src/import_om1"
            )])
    ph.load_plugins("admin")
    ph.activate_plugins()
    ph.de_activate_plugins()
