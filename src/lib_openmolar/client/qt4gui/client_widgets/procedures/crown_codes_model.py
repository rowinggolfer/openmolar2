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

from PyQt4 import QtGui, QtCore



class CrownCodesModel(QtCore.QAbstractListModel):
    '''
    a model to display crown procedure codes
    '''
    def __init__(self, parent=None):
        super(CrownCodesModel, self).__init__(parent)

        self.proc_codes = [_("Crowns")]
        for code in SETTINGS.PROCEDURE_CODES.crown_codes:
            self.proc_codes.append(code)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole:
            item = self.proc_codes[index.row()]
            if index.row() == 0:
                return item
            else:
                return u"   %s"% item.description
        if role == QtCore.Qt.UserRole:
            return self.proc_codes[index.row()]

        return QtCore.QVariant()

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
        role == QtCore.Qt.DisplayRole):
            return "Crowns"

        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
       return len(self.proc_codes)


if __name__ == "__main__":
    def sig_catcher(arg):
        index = model.index(arg)
        print model.data(index, QtCore.Qt.UserRole)
    
    

    app = QtGui.QApplication([])


    model = CrownCodesModel()

    obj = QtGui.QComboBox()
    obj.setModel(model)
    obj.show()

    obj.currentIndexChanged.connect(sig_catcher)

    app.exec_()
