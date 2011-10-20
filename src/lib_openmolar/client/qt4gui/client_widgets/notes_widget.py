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
from lib_openmolar.client.qt4gui.client_widgets import AddNotesWidget

class NotesWidget(QtGui.QWidget):
    RECEPTION = 0
    CLINICAL = 1
    COMBINED = 2

    # the current note being edited
    _current_edit_note = None
    _type = COMBINED

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.patient = None

        self.notes_browser = QtWebKit.QWebView(self)
        self.notes_browser.setHtml(messages.welcome_html(
            self.notes_browser.width()))

        self.notes_entry = AddNotesWidget()

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.notes_browser)
        layout.addWidget(self.notes_entry)

        self.is_loaded = False
        self.notes_entry.hide()

        self.notes_browser.linkClicked.connect(self._link_clicked)

        self.connect(self.notes_entry, QtCore.SIGNAL("Save Requested"),
            self.note_edited)

        #ensure that we have a css file.. otherwise the notes will be awful!
        if not os.path.exists(SETTINGS._NOTES_CSS):
            print "initiating a new notes.css file"
            resource = QtCore.QResource(":css/notes.css")
            f = open(SETTINGS._NOTES_CSS, "w")
            f.write(resource.data())
            f.close()


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
            self.notes_entry.hide()
            QtCore.QTimer.singleShot(100, self.scroll_to_end)

    def scroll_to_end(self):
        wf = self.notes_browser.page().mainFrame()
        wf.setScrollBarValue(QtCore.Qt.Vertical,
            wf.scrollBarMaximum(QtCore.Qt.Vertical))

    def _link_clicked(self, qurl):
        url = qurl.toString()
        if url.startsWith("edit_note"):
            m = re.match("edit_note_(\d+)", url)
            ix = int(m.groups()[0])
            if ix != 0:
                print "edit existing uncommitted note %d"% ix
                self._current_edit_note = SETTINGS.current_patient.notes.clinical_by_id(ix)
            else:
                self._current_edit_note = SETTINGS.current_patient.notes.new_clinical

        elif url =="new_note":
            self._current_edit_note = SETTINGS.current_patient.notes.new_clinical
        else:
            print "bad url in notes page?", url
            return
        try:
            self.notes_entry.set_text(
                self._current_edit_note.value("line").toString())
        except AttributeError:
            self.notes_entry.set_text("")

        self.notes_entry.show()
        self.scroll_to_end()

    def note_edited(self):
        '''
        the user has edited a note.. time to update the html
        '''
        self._current_edit_note.setValue("line", self.notes_entry.text)
        SETTINGS.current_patient.notes.commit_clinical(self._current_edit_note)

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

        QtCore.QTimer.singleShot(2000, self.change)

    def sizeHint(self):
        return QtCore.QSize(700,200)

    def change(self):
        self.nw.set_type(NotesWidget.CLINICAL)

if __name__ == "__main__":

    from lib_openmolar.common.widgets import RestorableApplication
    app = RestorableApplication("openmolar-client")

    from lib_openmolar.client.connect import ClientConnection
    from lib_openmolar.client.db_orm import PatientModel

    cc = ClientConnection()

    cc.connect()
    pt = PatientModel(1)
    SETTINGS.set_current_patient(pt)

    dl = _TestDialog()
    dl.exec_()
