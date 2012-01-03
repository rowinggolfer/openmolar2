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



from lib_openmolar.client.qt4gui.colours import colours

class ToothEditor(QtGui.QWidget):
    def __init__(self,parent=None):
        super(ToothEditor, self).__init__(parent)

        self.tooth_widget = ToothWidget(self)
        self.material_buts = MaterialButBox(self)

        self.connect_signals()

        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.tooth_widget)
        layout.addWidget(self.material_buts)

    def clear(self):
        self.tooth_widget.clear()

    def sizeHint(self):
        return QtCore.QSize(200,150)

    def sizeHint(self):
        return QtCore.QSize(150,150)

    def setTooth(self, tooth):
        self.current_tooth = tooth
        self.tooth_widget.setTooth(tooth)

    def connect_signals(self):
        self.connect(self.material_buts, QtCore.SIGNAL("colour changed"),
            self.tooth_widget.setFillColour)
        self.connect(self.material_buts, QtCore.SIGNAL("editing finished"),
            self.finished)

    def finished(self):
        self.emit(QtCore.SIGNAL("editing finished"))
        self.clear()

class MaterialButBox(QtGui.QWidget):
    def __init__(self,parent=None):
        super(MaterialButBox, self).__init__(parent)

        layout = QtGui.QVBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(2)

        for material, colour in SETTINGS.fill_materials:
            but = QtGui.QPushButton(material)
            but.setStyleSheet("background-color: %s"% colour.name())
            but.setMaximumWidth(40)
            but.setFocusPolicy(QtCore.Qt.NoFocus)
            but.clicked.connect(self.but_clicked)
            but.mouseDoubleClickEvent = self.mouseDoubleClickEvent

            layout.addWidget(but)

    def but_clicked(self):
        but = self.sender()
        self.emit(QtCore.SIGNAL("colour changed"),
            but.palette().background().color(), but.text())

    def mouseDoubleClickEvent(self, event):
        self.emit(QtCore.SIGNAL("editing finished"))

class ToothWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ToothWidget, self).__init__(parent)

        self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.current_tooth = None
        self.setMouseTracking(True)
        self.shapes()
        self.clear()

    def sizeHint(self):
        return QtCore.QSize(150, 150)

    def minimumSizeHint(self):
        return QtCore.QSize(80, 80)

    def setTooth(self, tooth):
        self.clear()
        try:
            resize_needed = self.current_tooth.is_backtooth != tooth.is_backtooth
        except AttributeError: # current_tooth could be None
            resize_needed = True

        self.current_tooth = tooth
        self.setEnabled(tooth != None)

        if resize_needed:
            self.shapes()
        self.update()

    @property
    def isBacktooth(self):
        if not self.current_tooth:
            return True
        return self.current_tooth.is_backtooth

    @property
    def isRight(self):
        if not self.current_tooth:
            return True
        return self.current_tooth.is_rightside

    @property
    def isUpper(self):
        if not self.current_tooth:
            return True
        return self.current_tooth.is_upper

    def clear(self):
        self.filledSurfaces = ""
        if self.isBacktooth:
            self.fillcolour = colours.AMALGAM
        else:
            self.fillcolour = colours.COMPOSITE
        self.update()

    def setFillColour(self, colour, text):
        self.fillcolour = colour
        self.update()
        self.emit(QtCore.SIGNAL("material"), text)

    def sortSurfaces(self,arg):
        '''
        sort the filling surfaces to fit with conventional notation
        eg... MOD not DOM etc..
        '''

        retarg = ""
        if "M" in arg:
            retarg += "M"
        if "D" in arg and not "M" in retarg:
            retarg += "D"
        if "O" in arg:
            retarg += "O"
        if "D" in arg and not "D" in retarg:
            retarg += "D"
        if "B" in arg:
            retarg += "B"
        if "P" in arg:
            retarg += "P"
        if "L" in arg:
            retarg += "L"
        if "I" in arg:
            retarg += "I"

        return retarg

    def setFilledSurfaces(self, arg):
        if arg in self.filledSurfaces:
            self.filledSurfaces = self.filledSurfaces.replace(arg, "")
        else:
            self.filledSurfaces += arg
        self.filledSurfaces = self.sortSurfaces(self.filledSurfaces)
        self.update()

    def leaveEvent(self, event):
        self.mouseOverSurface = None
        self.update()

    def mouseMoveEvent(self, event):
        y=event.y()
        x=event.x()
        point = QtCore.QPoint(x,y)

        if self.mesial.containsPoint(point, QtCore.Qt.OddEvenFill):
            self.mouseOverSurface = self.mesial
            self.update()

        elif self.occlusal.containsPoint(point, QtCore.Qt.OddEvenFill):
            self.mouseOverSurface = self.occlusal
            self.update()

        elif self.distal.containsPoint(point, QtCore.Qt.OddEvenFill):
            self.mouseOverSurface = self.distal
            self.update()

        elif self.buccal.containsPoint(point, QtCore.Qt.OddEvenFill):
            self.mouseOverSurface = self.buccal
            self.update()

        elif self.palatal.containsPoint(point, QtCore.Qt.OddEvenFill):
            self.mouseOverSurface = self.palatal
            self.update()

    def mousePressEvent(self, event):
        y = event.y()
        x = event.x()
        point = QtCore.QPoint(x,y)

        if self.mesial.containsPoint(point, QtCore.Qt.OddEvenFill):
            if self.isRight:
                self.setFilledSurfaces("D")
            else:
                self.setFilledSurfaces("M")

        elif self.occlusal.containsPoint(point, QtCore.Qt.OddEvenFill):
            if self.isBacktooth:
                self.setFilledSurfaces("O")
            else:
                self.setFilledSurfaces("I")

        elif self.distal.containsPoint(point, QtCore.Qt.OddEvenFill):
            if not self.isRight:
                self.setFilledSurfaces("D")
            else:
                self.setFilledSurfaces("M")

        elif self.buccal.containsPoint(point, QtCore.Qt.OddEvenFill):
            if self.isUpper:
                self.setFilledSurfaces("B")
            else:
                self.setFilledSurfaces("L")

        elif self.palatal.containsPoint(point, QtCore.Qt.OddEvenFill):
            if self.isUpper:
                self.setFilledSurfaces("P")
            else:
                self.setFilledSurfaces("B")

        else:
            return #missed!!

        self.emit(QtCore.SIGNAL("toothSurface"), self.filledSurfaces)


    def resizeEvent(self,event):
        self.shapes()

    def shapes(self):
        self.toothRect=QtCore.QRectF(0,0,self.width(),self.height())
        irw = self.toothRect.width()*0.25
        if self.isBacktooth:
            irh = self.toothRect.height()*0.25
        else:
            irh = self.toothRect.height()*0.40
        self.innerRect = self.toothRect.adjusted(irw,irh,-irw,-irh)

        self.mesial = QtGui.QPolygon([
            0,
            0,
            self.innerRect.topLeft().x(),self.innerRect.topLeft().y(),
            self.innerRect.bottomLeft().x(),self.innerRect.bottomLeft().y(),
            self.toothRect.bottomLeft().x(),self.toothRect.bottomLeft().y()
            ])

        self.occlusal = QtGui.QPolygon([
            self.innerRect.topLeft().x(),self.innerRect.topLeft().y(),
            self.innerRect.topRight().x(),self.innerRect.topRight().y(),
            self.innerRect.bottomRight().x(),self.innerRect.bottomRight().y(),
            self.innerRect.bottomLeft().x(),self.innerRect.bottomLeft().y()
            ])

        self.distal = QtGui.QPolygon([
            self.innerRect.topRight().x(),self.innerRect.topRight().y(),
            self.toothRect.topRight().x(),self.toothRect.topRight().y(),
            self.toothRect.bottomRight().x(),self.toothRect.bottomRight().y(),
            self.innerRect.bottomRight().x(),self.innerRect.bottomRight().y()
            ])

        self.buccal = QtGui.QPolygon([
            0,
            0,
            self.toothRect.topRight().x(),self.toothRect.topRight().y(),
            self.innerRect.topRight().x(),self.innerRect.topRight().y(),
            self.innerRect.topLeft().x(),self.innerRect.topLeft().y()
            ])

        self.palatal=QtGui.QPolygon([
            self.toothRect.bottomLeft().x(),self.toothRect.bottomLeft().y(),
            self.innerRect.bottomLeft().x(),self.innerRect.bottomLeft().y(),
            self.innerRect.bottomRight().x(),self.innerRect.bottomRight().y(),
            self.toothRect.bottomRight().x(),self.toothRect.bottomRight().y()
            ])

        self.mouseOverSurface = None #initiate a value

    def paintEvent(self, event=None):
        if self.isBacktooth:
            if self.isUpper:
                surfs = "DBPMO" if self.isRight else "MBPDO"
            else:
                surfs = "DLBMO" if self.isRight else "MLBDO"
        else:
            if self.isUpper:
                surfs = "DBPMI" if self.isRight else "MBPDI"
            else:
                surfs = "DLBMI" if self.isRight else "MLBDI"

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QtGui.QColor("gray"))
        painter.setBrush(colours.IVORY)
        painter.drawRect(self.toothRect)
        painter.drawRect(self.innerRect)

        painter.drawLine(self.toothRect.topLeft(),self.innerRect.topLeft())
        painter.drawLine(self.toothRect.topRight(),self.innerRect.topRight())
        painter.drawLine(self.toothRect.bottomLeft(),self.innerRect.bottomLeft())
        painter.drawLine(self.toothRect.bottomRight(),self.innerRect.bottomRight())

        painter.setBrush(self.fillcolour)

        if "M" in self.filledSurfaces:
            if self.isRight:
                painter.drawPolygon(self.distal)
            else:
                painter.drawPolygon(self.mesial)

        if "O" in self.filledSurfaces or "I" in self.filledSurfaces:
            painter.drawPolygon(self.occlusal)

        if "D" in self.filledSurfaces:
            if not self.isRight:
                painter.drawPolygon(self.distal)
            else:
                painter.drawPolygon(self.mesial)

        if "B" in self.filledSurfaces:
            if self.isUpper:
                painter.drawPolygon(self.buccal)
            else:
                painter.drawPolygon(self.palatal)

        if "L" in self.filledSurfaces:
                painter.drawPolygon(self.buccal)

        if "P" in self.filledSurfaces:
                painter.drawPolygon(self.palatal)

        painter.setBrush(colours.TRANSPARENT)

        if self.mouseOverSurface!=None:
            painter.setPen(QtGui.QColor("red"))
            painter.drawPolygon(self.mouseOverSurface)

        painter.setPen(self.palette().buttonText().color())
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)

        rect = self.toothRect.adjusted(0, 0, -self.innerRect.right(), 0)
        painter.drawText(QtCore.QRectF(rect), surfs[0], option)

        rect = self.toothRect.adjusted(0, 0, 0, -self.innerRect.bottom())
        painter.drawText(QtCore.QRectF(rect), surfs[1], option)

        rect = self.toothRect.adjusted(0, self.innerRect.bottom(), 0, 0)
        painter.drawText(QtCore.QRectF(rect), surfs[2], option)

        rect = self.toothRect.adjusted(self.innerRect.right(), 0, 0, 0)
        painter.drawText(QtCore.QRectF(rect), surfs[3], option)

        painter.drawText(QtCore.QRectF(self.innerRect), surfs[4], option)

if __name__ == "__main__":

    
    
    app = QtGui.QApplication([])
    dl = QtGui.QDialog()
    object = ToothEditor(dl)


    layout = QtGui.QVBoxLayout(dl)
    layout.addWidget(object)
    dl.exec_()
