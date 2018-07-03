# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Constraint Checker
                                 A QGIS plugin
 Generate reports of constraints (e.g. planning constraints) applicable to an area of interest.
                              -------------------
        begin                : 2014-03-19
        copyright            : (C) 2014 by Lutra Consulting for Dartmoor National Park Authority
        email                : it@dnpa.gov.uk
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from results_dialog_ui import Ui_Dialog

class ResultsDialog(QDialog, Ui_Dialog):
    
    def __init__(self, model):
        QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.resultModel = model
        self.constraintTableView.setModel(self.resultModel)
        self.constraintTableView.resizeColumnsToContents()       
