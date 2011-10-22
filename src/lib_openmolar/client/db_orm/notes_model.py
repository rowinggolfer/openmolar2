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
This module provides the NotesModel Class, a view aware editable model of
data stored in various notes tables
'''

from PyQt4 import QtCore, QtSql

from lib_openmolar.client.db_orm import *

class NotesModel(object):
    '''
a view aware editable model of data stored in various notes tables
    '''
    views = set([])
    '''The model keeps a note of what is watching it.'''

    def __init__(self, patient_id):
        self.clinical = NotesClinicalDB(patient_id)
        self.clerical = NotesClericalDB(patient_id)

        self.patient_id = patient_id

    def add_view(self, view):
        '''
        make the model aware of the view so that it can be alerted when model
        changes.
        such views require a method "model_updated"
        '''
        self.views.add(view)

    @property
    def is_dirty(self):
        '''
        A Boolean.
        If True, then the record differs from the database state
        '''
        return self.clinical.is_dirty or self.clerical.is_dirty

    def what_has_changed(self):
        '''
        returns a stringlist of what has changed.

        TODO could be much improved
        '''
        changes = []
        if self.clerical.is_dirty:
            changes.append(_("Clerical Notes"))
        if self.clinical.is_dirty:
            changes.append(_("Clinical Notes"))
        return changes

    def commit_changes(self):
        '''
        commits any user edits to the database
        '''
        self.clerical.commit_changes()
        self.clinical.commit_changes()

    def update_views(self):
        for view in self.views:
            view.model_updated()

    @property
    def clinical_html(self):
        '''
        returns an html representation of the *clinical* notes
        '''
        def wrap(foo):
            foo = foo.replace("<", "&lt;").replace(">", "&gt;").replace(
                "\n", "<br />")

            editable = not record.value("committed").toBool()
            if editable:
                foo = '<a href = "edit_note_%d">%s</a>%s'% (
                    record.value("ix").toInt()[0] , SETTINGS.PENCIL, foo)

            return (foo, editable)

        def record_date():
            date_ = record.value('open_time').toDate().toString(
                    QtCore.Qt.DefaultLocaleShortDate)
            return date_

        html =  u'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="utf-8" />
        <title>Clinical Notes</title>
        <link rel="stylesheet" type="text/css" href="%s">
        </head>
        <body>
        <div class='center'><table>
        <tr><th>%s</th><th>%s</th><th>%s</th></tr>
        '''% (SETTINGS.NOTES_CSS, _("Date"), _("Author"), _("notes"))

        for record in self.clinical.records:
            author = record.value("author").toInt()[0]
            co_author = record.value("co_author").toInt()[0]

            author_repr = SETTINGS.users.get_avatar_html(author,
                options='class="author"')
            co_author_repr = SETTINGS.users.get_avatar_html(co_author,
                options='class="co_author"')

            note, editable = wrap(record.value("line").toString())

            edit_class = 'editable_clinical' if editable else ""
            html += u'''
            <tr class="%s">
                <td class="date">%s</td>
                <td class="author">%s %s</td>
                <td class="note">%s</td>
            </tr>'''% (
                edit_class, record_date(),
                author_repr, co_author_repr,
                note)

        if not self.clinical.has_new_note:
            html += '''
            </table>
            <div class="new_note_link">
            <a href = "new_clinical_note">%s %s</a>
            </div>
            </div>'''% (_("New Clinical Note"), SETTINGS.PENCIL)

        else:
            html += '</table></div>'

        return html + "</body></html>"

    def clinical_by_id(self, id):
        '''
         :param: id (int)
        returns the :doc:`NotesClinicalDB` with this id
       '''
        return self.clinical.record_by_id(id)

    @property
    def new_clinical(self):
        '''
        returns a new clinical note of type :doc:`InsertableRecord`
        '''
        return self.clinical.new_note

    def commit_clinical(self, note):
        '''
        the note has been edited
        '''
        if self.clinical.commit_note(note):
            self.update_views()

    def commit_clerical(self, note):
        '''
        the note has been edited
        '''
        if self.clerical.commit_note(note):
            self.update_views()

    @property
    def clerical_html(self):
        '''
        returns an html representation of the *reception* notes
        '''
        def wrap(foo):
            foo = foo.replace("<", "&lt;").replace(">", "&gt;").replace(
                "\n", "<br />")

            editable = not record.value("committed").toBool()
            if editable:
                foo = '<a href = "edit_note_%d">%s</a>%s'% (
                    record.value("ix").toInt()[0] , SETTINGS.PENCIL, foo)

            return (foo, editable)

        def record_date():
            date_ = record.value('open_time').toDate().toString(
                    QtCore.Qt.DefaultLocaleShortDate)
            return date_

        html = u'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="utf-8" />
        <title>Reception Notes</title>
        <link rel="stylesheet" type="text/css" href="%s">
        </head>
        <body>
        <div class='center'><table>
        <tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>
        '''% (
            SETTINGS.NOTES_CSS,
            _("Date"), _("Author"), _("Action"), _("Notes")
            )

        for record in self.clerical.records:
            author = record.value("author").toInt()[0]
            author_repr = SETTINGS.users.get_avatar_html(author,
                    options='class="author"')
            action = record.value("type").toString()
            note, editable = wrap(record.value("line").toString())

            edit_class = 'editable_clerical' if editable else ""
            html += u'''
            <tr class="%s">
                <td class="date">%s</td>
                <td class="author">%s</td>
                <td class="action">%s</td>
                <td class="note">%s</td>
            </tr>'''% (
                edit_class, record_date(),
                author_repr, action, note)

        return html + '</table></div></body></html>'

    def clerical_by_id(self, id):
        '''
        :param: id (int)
        returns the :doc:`NotesClericalDB` with this id
        '''
        return self.clerical.record_by_id(id)

    @property
    def all_records(self):
        '''
        yields all records from all note types
        '''
        for record in self.clerical.records:
            yield record
        for record in self.clinical.records:
            yield record

    @property
    def sorted_records(self):
        '''
        yields all_records in order.
        '''
        datetimes = []
        for record in self.all_records:
            datetimes.append(record.value("open_time").toDateTime())
        for datetime_ in sorted(datetimes):
            for record in self.all_records:
                if record.value("open_time") == datetime_:
                    yield record

    @property
    def combined_html(self):
        '''
        All notes together
        '''

        def wrap(foo):
            foo = foo.replace("<", "&lt;").replace(">", "&gt;").replace(
                "\n", "<br />")

            editable = not record.value("committed").toBool()
            record_type = "clinical" if record.is_clinical else "clerical"
            if editable:
                foo = '<a href = "edit_%s_note_%d">%s</a>%s'% (
                    record_type,
                    record.value("ix").toInt()[0] , SETTINGS.PENCIL, foo)

            return (foo, editable)

        def record_date():
            date_ = record.value('open_time').toDateTime().toString(
                    QtCore.Qt.DefaultLocaleShortDate)
            return date_

        html = u'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="utf-8" />
        <title>Combined Notes</title>
        <link rel="stylesheet" type="text/css" href="%s">
        </head>
        <body>
        <h1>%s</h1>
        <div class='center'><table>
        <tr><th>%s</th><th>%s</th><th>%s</th></tr>
        '''% (
            SETTINGS.NOTES_CSS,
            _("Combined Notes"),
            _("Date"), _("Author"), _("Notes"))

        for record in self.sorted_records:
            author = record.value("author").toInt()[0]
            co_author = record.value("co_author").toInt()[0]

            author_repr = SETTINGS.users.get_avatar_html(author,
                options='class="author"')
            co_author_repr = SETTINGS.users.get_avatar_html(co_author,
                options='class="co_author"')

            note, editable = wrap(record.value("line").toString())

            edit_class = 'editable_' if editable else ""
            edit_class += "clinical" if record.is_clinical else "clerical"
            html += u'''
            <tr class="%s">
                <td class="date">%s</td>
                <td class="author">%s %s</td>
                <td class="note">%s</td>
            </tr>'''% (
                edit_class, record_date(),
                author_repr, co_author_repr,
                note)


        return html + "</table></div></body></html>"


if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    model = NotesModel(1)
    print model.clerical_html
    print "\n"*5
    print model.clinical_html
    print "\n"*5
    print model.combined_html