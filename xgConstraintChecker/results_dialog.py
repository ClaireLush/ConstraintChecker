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
import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
ui_results_dialog, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'results_dialog_base.ui'))

class ResultsDialog(QDialog, ui_results_dialog):
    def __init__(self, model, parent=None):
        """Constructor."""
        super().__init__(parent)

        # Set up the user interface from Designer.
        self.setupUi(self)
        self.resultModel = model
        self.constraintTableView.setModel(self.resultModel)
        self.constraintTableView.resizeColumnsToContents()
