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

import os
import re

from PyQt4 import QtCore, QtGui, QtWebKit
from lib_openmolar.client.messages import messages
from lib_openmolar.client.qt4.widgets import AddNotesWidget

class NotesWidget(QtGui.QWidget):
    RECEPTION = 0
    CLINICAL = 1
    COMBINED = 2

    # the current note being edited
    _clinical_edit_note = None
    _clerical_edit_note = None

    _type = COMBINED

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.patient = None

        self.notes_browser = QtWebKit.QWebView(self)
        self.notes_browser.setHtml(messages.welcome_html(
            self.notes_browser.width()))

        self.clinical_editor = AddNotesWidget()
        self.clerical_editor = AddNotesWidget()

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.notes_browser)
        layout.addWidget(self.clerical_editor)
        layout.addWidget(self.clinical_editor)

        self.is_loaded = False
        self.clinical_editor.hide()
        self.clerical_editor.hide()

        self.notes_browser.linkClicked.connect(self._link_clicked)

        self.connect(self.clinical_editor, QtCore.SIGNAL("Save Requested"),
            self.clinical_note_edited)
        self.connect(self.clerical_editor, QtCore.SIGNAL("Save Requested"),
            self.clerical_note_edited)

    def sizeHint(self):
        return QtCore.QSize(500,400)

    def clear(self):
        self.notes_browser.setHtml(messages.welcome_html(
            self.notes_browser.width()))
        self.is_loaded = False
        self._new_note = None

    @property
    def type(self):
        '''
        A notes widget can be of type Reception, clinical or combined
        '''
        return self._type

    def set_type(self, type):
        '''
        set the type
        '''
        assert type in (self.CLINICAL, self.RECEPTION, self.COMBINED)
        self.is_loaded = type == self.type
        self._type = type
        self.load_patient()

    def minimumSizeHint(self):
        return QtCore.QSize(300,300)

    def Advise(self, *args):
        if __name__ == "__main__":
            print args
        self.emit(QtCore.SIGNAL("Advise"), *args)

    def update_patient(self):
        if not self.patient:
            return

    def load_patient(self):
        patient = SETTINGS.current_patient
        if patient and not self.is_loaded:
            patient.notes.add_view(self)
            if self.type == self.CLINICAL:
                html = patient.notes.clinical_html
            elif self.type == self.RECEPTION:
                html = patient.notes.clerical_html
            else:
                html = patient.notes.combined_html

            self.notes_browser.setHtml(html)
            self.notes_browser.page().setLinkDelegationPolicy(
                QtWebKit.QWebPage.DelegateAllLinks)

            self.is_loaded = True
            self.clinical_editor.hide()
            self.clerical_editor.hide()
            QtCore.QTimer.singleShot(100, self.scroll_to_end)

    def scroll_to_end(self):
        wf = self.notes_browser.page().mainFrame()
        wf.setScrollBarValue(QtCore.Qt.Vertical,
            wf.scrollBarMaximum(QtCore.Qt.Vertical))

    def _link_clicked(self, qurl):
        url = qurl.toString()
        show_clinical, show_clerical = False, False
        if url.startsWith("edit_clinical_note"):
            m = re.match("edit_clinical_note_(\d+)", url)
            ix = int(m.groups()[0])
            if ix != 0:
                print "edit existing uncommitted clinical note %d"% ix
                self._clinical_edit_note = SETTINGS.current_patient.notes.clinical_by_id(ix)
            else:
                self._clinical_edit_note = SETTINGS.current_patient.notes.new_clinical
            show_clinical = True
        elif url.startsWith("edit_clerical_note"):
            m = re.match("edit_clerical_note_(\d+)", url)
            ix = int(m.groups()[0])
            if ix != 0:
                print "edit existing uncommitted clerical_note %d"% ix
                self._clerical_edit_note = SETTINGS.current_patient.notes.clerical_by_id(ix)
            else:
                self._clerical_edit_note = SETTINGS.current_patient.notes.new_clerical
            show_clerical = True

        elif url =="new_clinical_note":
            self._clinical_edit_note = SETTINGS.current_patient.notes.new_clinical
            show_clinical = True

        elif url =="new_clerical_note":
            self._clerical_edit_note = SETTINGS.current_patient.notes.new_clerical
            show_clerical = True

        else:
            print "bad url in notes page?", url
            return
        try:
            self.clinical_editor.set_text(
                self._clinical_edit_note.value("line").toString())
        except AttributeError:
            self.clinical_editor.set_text("")

        try:
            self.clerical_editor.set_text(
                self._clerical_edit_note.value("line").toString())
        except AttributeError:
            self.clerical_editor.set_text("")

        self.clinical_editor.setVisible(show_clinical)
        self.clerical_editor.setVisible(show_clerical)
        self.scroll_to_end()

    def clinical_note_edited(self):
        '''
        the user has edited a note.. time to update the html
        '''
        self._clinical_edit_note.setValue("line", self.clinical_editor.text)
        SETTINGS.current_patient.notes.commit_clinical(self._clinical_edit_note)

    def clerical_note_edited(self):
        '''
        the user has edited a note.. time to update the html
        '''
        self._clerical_edit_note.setValue("line", self.clerical_editor.text)
        SETTINGS.current_patient.notes.commit_clerical(self._clerical_edit_note)

    def model_updated(self):
        '''
        this function is called by the underlying model
        '''
        self.is_loaded = False
        self.load_patient()

class _TestDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.nw = NotesWidget(self)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.nw)
        self.nw.load_patient()

        #QtCore.QTimer.singleShot(2000, self.change)

    def sizeHint(self):
        return QtCore.QSize(700,200)

    def change(self):
        self.nw.set_type(NotesWidget.CLINICAL)

if __name__ == "__main__":

    from lib_openmolar.common.qt4.widgets import RestorableApplication
    app = RestorableApplication("openmolar-client")

    from lib_openmolar.client.connect import DemoClientConnection
    from lib_openmolar.client.db_orm import PatientModel

    cc = DemoClientConnection()

    cc.connect()
    pt = PatientModel(1)
    SETTINGS.set_current_patient(pt)

    dl = _TestDialog()
    dl.exec_()
