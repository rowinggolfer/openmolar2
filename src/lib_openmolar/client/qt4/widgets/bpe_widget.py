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



from PyQt4 import QtCore, QtGui

class BPEWidget(QtGui.QGroupBox):
    '''
    this class provides a widget which displays the BPE information,
    also fires a signal when a new BPE is to be added.
    '''
    def __init__(self, parent=None):
        QtGui.QGroupBox.__init__(self, _("BPE"), parent)

        self.bpe_label = QtGui.QLabel()
        icon = QtGui.QIcon(':icons/bpe_new.png')

        self.new_button = QtGui.QPushButton(icon, "")
        self.new_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.new_button.setMaximumWidth(40)
        self.new_button.setFlat(True)

        icon = QtGui.QIcon(':icons/bpe_list.png')
        self.list_button = QtGui.QPushButton(icon, "")
        self.list_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.list_button.setMaximumWidth(40)
        self.list_button.setFlat(True)

        self.new_button.clicked.connect(self.emit_new_bpe)
        self.list_button.clicked.connect(self.emit_show_all)

        layout = QtGui.QGridLayout(self)
        layout.setMargin(0)
        layout.setSpacing(1)
        layout.addWidget(self.new_button,0,1)
        layout.addWidget(self.list_button,1,1)
        layout.addWidget(self.bpe_label,0,0,2,1)

    def sizeHint(self):
        return QtCore.QSize(200,100)

    def clear(self):
        '''
        restores the widget to it's initial state
        '''
        self.bpe_label.hide()
        self.list_button.hide()
        self.bpe_label.setToolTip("")
        self.setTitle(_("BPE"))

    def set_values(self, arg):
        if arg is None:
            self.clear()
            return
        date, clinician, values, comment = arg
        self.set_label_text(values)
        self.setTitle("%s %s"%(_("BPE"),
            date.toString(QtCore.Qt.DefaultLocaleShortDate)))

        if comment != "":
            self.bpe_label.setToolTip("%s<hr />%s"% (_("NOTE"), comment))

    def set_label_text(self, values):
        self.bpe_label.show()
        self.list_button.show()
        display_values = []
        for c in values:
            if c in ("*","4"):
                display_values.append("<font color='red'>%s</font>"% c)
            else:
                display_values.append(c)
        bpe_text = '''<div>
        <table width='100%%' border='1'>
        <tr><td>%s</td><td>%s</td><td>%s</td></tr>
        <tr><td>%s</td><td>%s</td><td>%s</td></tr>
        </table>
        </div>'''% tuple(display_values)
        self.bpe_label.setText(bpe_text)

    def emit_new_bpe(self):
        '''
        A signal is emmitted if user clicks on the new button

        >>> self.emit(QtCore.SIGNAL("New BPE"))

        '''
        self.emit(QtCore.SIGNAL("New BPE"))

    def emit_show_all(self):
        '''
        A signal is emmitted if user clicks on the show button

        >>>self.emit(QtCore.SIGNAL("Show BPE"))

        '''
        self.emit(QtCore.SIGNAL("Show BPE"))

if __name__ == "__main__":
    

    def sig_catcher(*args):
        print args, cp.sender()

    
    
    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    layout = QtGui.QVBoxLayout(dl)
    cp = BPEWidget(dl)
    cp.set_values((QtCore.QDate.currentDate(), 1, "1234*-", "furcation UL6"))
    dl.connect(cp, QtCore.SIGNAL('New BPE'), sig_catcher)
    dl.connect(cp, QtCore.SIGNAL('Show BPE'), sig_catcher)

    layout.addWidget(cp)
    dl.exec_()
