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

from lib_openmolar.common import Plugin

from PyQt4.QtCore import QResource

class PluginHandler(object):
    '''
    A class to verify and install plugins
    '''
    #: locations of directories where plugins reside
    PLUGIN_DIRS = []

    #: locations of directories where naked plugins reside
    NAKED_PLUGIN_DIRS = []

    _plugins = []
    _fee_scales = []

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
            if inspect.isclass(obj) and Plugin in obj.mro()[1:]:
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
                LOGGER.info("NAKED PLUGIN FOUND '%s'"% full_path)
                if plugin_dir in self.NAKED_PLUGIN_DIRS:
                    module = file_.replace('.py','')
                    mod = __import__(module)
                    yield mod
                else:
                    LOGGER.info(
                    'NOT COMPILING %s is not a known store for naked plugins'%
                    plugin_dir)
            elif zipfile.is_zipfile(full_path):
                module = file_.replace('.zip','')
                try:
                    z = zipimport.zipimporter(full_path)
                    mod = z.load_module(module)
                    yield mod
                except (zipimport.ZipImportError, zipfile.BadZipfile) as e:
                    LOGGER.exception ("incompatible plugin '%s'"% full_path)

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

    def load_plugins(self):
        '''
        this function is called by the client application to load plugins
        '''
        LOGGER.info ("loading plugins...")
        i = 0
        for plugin_dir in self.PLUGIN_DIRS:
            LOGGER.info ("looking for plugins in directory %s"% plugin_dir)
            try:
                i += self.get_plugins(plugin_dir)

            except Exception as e:
                LOGGER.exception ("Exception loading plugin")

        LOGGER.info("%d plugin(s) loaded"% i)

    def install_plugin(self, plugin):
        '''
        installs a plugin (of type BasePlugin)
        '''
        if plugin.TYPE == plugin.FEE_SCALE:
            self.install_fee_scale(plugin)

        try:
            LOGGER.debug("setting up plugin %s"% plugin)
            plugin.setup_plugin()
        except Exception, e:
            LOGGER.exception(
            "Exception during plugin.setup_plugin '%s'"% plugin.name)

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
        LOGGER.info ("installing fee_scale %s"% fee_scale)
        self._fee_scales.append(fee_scale)

    @property
    def fee_scales(self):
        '''
        a list of all fee_scales installed (fee_scale = a type of BasePlugin)
        '''
        return sorted(self._fee_scales)

if __name__ == "__main__":
    import lib_openmolar.admin
    logging.basicConfig(level = logging.DEBUG)
    ph = PluginHandler()
    ph.PLUGIN_DIRS = [
            "/home/neil/openmolar/hg_openmolar/plugins",
            "/home/neil/openmolar/hg_openmolar/plugins/src"]
    ph.NAKED_PLUGIN_DIRS = [
            "/home/neil/openmolar/hg_openmolar/plugins/src",
            ]
    ph.load_plugins()