# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Constraint Checker
                                 A QGIS plugin
 Generate reports of constraints (e.g. planning constraints) applicable to an area of interest.
                              -------------------
        begin                : 2014-03-19
        copyright            : (C) 2018 by exeGesIS SDM Ltd
        email                : xginfo@esdm.co.uk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import pyqtSignal, Qt
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsWkbTypes, QgsGeometry
from qgis.gui import QgsMapTool, QgsRubberBand

class FreehandPolygonMapTool(QgsMapTool):
    geometryReady = pyqtSignal(QgsGeometry)

    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas = canvas
        self.rb = QgsRubberBand(canvas, QgsWkbTypes.PolygonGeometry)
        self.rb.setColor(QColor(255, 0, 0, 50))

    def activate(self):
        self.rb.reset(QgsWkbTypes.PolygonGeometry)

    def deactivate(self):
        self.rb.reset(QgsWkbTypes.PolygonGeometry)

    def canvasMoveEvent(self, ev):
        worldPoint = ev.mapPoint()
        self.rb.movePoint(worldPoint)

    def canvasPressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            # Add a new point to the rubber band
            worldPoint = ev.mapPoint()
            self.rb.addPoint( worldPoint )

        elif ev.button() == Qt.RightButton:
            # Send back the geometry to the calling class
            self.geometryReady.emit(self.rb.asGeometry())

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return False
