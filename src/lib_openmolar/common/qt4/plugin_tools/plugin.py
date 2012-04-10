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

from PyQt4 import QtGui

class _PluginError(Exception):
    '''
    A custom exception
    '''
    def __init__(self, value="Unknown"):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Plugin(object):
    '''
This class should be inherited by any class to be added to openmolar2.
Several key methods should be overwritten.
    '''

    #:
    SIMPLE = 0

    #:
    FEE_SCALE = 1

    #:
    IMPORTER = 2

    #:
    TYPES = (0, 1, 2)

    #:
    name = "Unspecified"

    #:
    authors = "unknown"

    #:
    version = "None"

    #:
    is_signed = False

    #:
    is_active = False

    #: can this be installed without app restart?
    is_hot_pluggable = True

    #:
    unique_id = None

    #:
    TARGET = "client"

    PluginError = _PluginError

    def __init__(self, plugin_type=SIMPLE):
        '''
        Plugin.__init__(self, plugin_type=Plugin.UNKNOWN)
            registers the plugin with the application
        '''
        if not plugin_type in self.TYPES:
            raise self.PluginError("Unknown plugin_type")

        self._TYPE = plugin_type

    def setup_plugin(self):
        '''
        by default, this does nothing, if overwritten, this is your chance
        to add to the gui.
        note - the gui can be accessed by SETTINGS.main_ui
        see also tear_down
        '''
        pass

    def tear_down(self):
        '''
        deactive the plugin
        this should reverse the setup_plugin function
        '''
        pass

    @property
    def icon(self):
        '''
        An icon is presented to the preferences dialog.
        A default icon is provided, so overwriting is optional.
        '''
        return QtGui.QIcon(":icons/plugins.png")

    def about_dialog(self, parent=None):
        '''
        Plugin.about_dialog(self, parent=None)

        Displays a QMessageBox with parent "parent"
        providing some basic information when the user requests it.
        can be overwritten by the plugin if required
        '''
        message = _("Name") + u"\t : %s<br />"% self.name
        message += _("Authors") + u"\t : %s<br />"% self.authors
        message += _("Version") + u"\t : %s<hr />"% self.version
        message += _("Description") + u"\t : %s<hr />"% self.description

        message += "%s<hr />"% self.long_description
        message += _("Website") + u"\t : %s"% self.website
        QtGui.QMessageBox.information(parent,
            _("About") + " " + self.name, message)

    def config_dialog(self, parent=None):
        '''
        Plugin.config_dialog(self, parent=None)

        This method can be called by the user by pressing on a button in
        the preferences dialog.
        by default, Displays a QMessageBox with parent "parent" saying no config is possible.

        NB - I have not coded a way to make these settings persistant yet.
        '''
        message = u"%s %s"% (
            self.name, _("plugin has no configuration options"))
        QtGui.QMessageBox.information(parent,
            _("Configure") + " " + self.name, message)

    @property
    def description(self):
        '''
        (String) Plugin.description(self)

        this property should be overwritten by well behaved plugins
        which inherit from this class
        '''
        return "property description must be overwritten by subclasses"

    @property
    def long_description(self):
        '''
        (String) Plugin.long_description(self)

        this property should be overwritten by well behaved plugins
        which inherit from this class
        '''
        return "property long_description should be overwritten by subclasses"

    @property
    def website(self):
        '''
        (String) Plugin.website(self)

        a homepage for this plugin
        '''
        return "property website should be overwritten by subclasses"

    @property
    def TYPE(self):
        '''
        returns the value which determines the nature of this plugin
        '''
        return self._TYPE

    def get_estimate(self, patient):
        '''
        get_estimate called...
        this should be overwritten by fee scale plugins
        '''
        return self.get_estimate.__doc__

    def __cmp__(self, other):
        '''
        Plugin.__cmp__(self, other)

        makes a comparions based on attribute 'name'
        useful to get plugins listed in alphabetical order

        returns cmp(self.name, other.name)
        '''
        return cmp(self.name, other.name)

    def __repr__(self):
        message = ("PLUGIN: name '%s'\n"% self.name +
        "        description '%s'\n"% self.description +
        "        signed  %s\n"% self.is_signed +
        "        authors '%s'\n"% self.authors +
        "        version '%s'\n"% self.version)
        return message

    def set_unique_id(self, id):
        self.unique_id = id

if __name__ == "__main__":
    import gettext
    gettext.install("")

    plug = Plugin()
    print plug
    app = QtGui.QApplication([])
    plug.about_dialog()
    plug.config_dialog()
