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

from PyQt4 import QtCore, QtGui, QtSql

from lib_openmolar.common.qt4.dialogs import BaseDialog

from lib_openmolar.client.db_orm.client_perio_bpe import NewPerioBPERecord

class BPE_ComboBox(QtGui.QComboBox):
    def __init__(self, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        self.addItems(["0","1","2","3","4","*","-"])
        self.setCurrentIndex(-1)

class NewBpeDialog(BaseDialog):
    def __init__(self, parent):
        '''
        2 arguments
            1. the database into which the new bpe will go.
            2. parent widget(optional)
        '''
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("New BPE"))
        self.patient_id = parent.pt.patient_id

        frame = QtGui.QFrame()
        layout = QtGui.QGridLayout(frame)

        self.cbs = []
        for i in range(6):
            cb = BPE_ComboBox()
            self.cbs.append(cb)
            row, col = i//3, i%3
            #alter addition order to set desired keyboard focus
            if row == 1:
                if col ==2:
                    col = 0
                elif col == 0:
                    col = 2
            layout.addWidget(cb, row, col)
            cb.currentIndexChanged.connect(self.check_applyable)

        label = QtGui.QLabel(_("Note"))
        self.comment_line = QtGui.QLineEdit()
        self.comment_line.setMaxLength(80)

        self.insertWidget(frame)
        self.insertWidget(label)
        self.insertWidget(self.comment_line)
        self.cbs[0].setFocus(True)

    def sizeHint(self):
        return QtCore.QSize(300,200)

    def check_applyable(self, i):
        def test():
            for cb in self.cbs:
                if cb.currentIndex() == -1:
                    return False
            return True
        self.enableApply(test())

    @property
    def values(self):
        value = ""
        for cb in self.cbs:
            value += cb.currentText()
        return value

    def exec_(self):
        if BaseDialog.exec_(self):
            new_record = NewPerioBPERecord()
            new_record.setValue("values", self.values)
            new_record.setValue("patient_id", self.patient_id)
            new_record.setValue("checked_by", "TODO - set cli")
            new_record.setValue("comment", self.comment_line.text())
            new_record.commit()
            return True
        return False


class ListBpeDialog(BaseDialog):
    def __init__(self, parent):
        '''
        2 arguments
            1. the database into which the new bpe will go.
            2. parent widget(optional)
        '''
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("BPE history"))
        text_browser = QtGui.QTextBrowser()

        bpes = parent.pt["perio_bpe"].records

        html = u"<body>"
        for date, clinician, values, comment in bpes:

            html += '''<h3>%s</h3> %s
        <table width='100%%' border='1'>
        <tr><td>%s</td><td>%s</td><td>%s</td></tr>
        <tr><td>%s</td><td>%s</td><td>%s</td></tr>
        </table>%s
        <hr />'''% ((date.toString(QtCore.Qt.DefaultLocaleShortDate),
        clinician)+ tuple(values)+ (comment,))

        text_browser.setText(html+"</body>")
        self.insertWidget(text_browser)
        self.remove_spacer()


if __name__ == "__main__":

    class DuckPatient(object):
        patient_id = 1

    class DuckParent(QtGui.QWidget):
        pt = DuckPatient()

    app = QtGui.QApplication([])
    from lib_openmolar.client.connect import DemoClientConnection

    cc = DemoClientConnection()
    cc.connect()

    parent = DuckParent()
    dl = NewBpeDialog(parent)
    dl.exec_()