# -*- coding: utf-8 -*-
"""
/***************************************************************************
 xgConstraintCheckerDialog
                                 A QGIS plugin
 Constraint Checker is a time saving application that interrogates spatial data for information within a user defined area, point or line.
                             -------------------
        begin                : 2018-03-07
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Exegesis Spatial Data Management Ltd
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

import ConfigParser
import os
import resources_rc

from PyQt4 import QtGui, uic
from xgcc_db import xgcc_db

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'check_dialog_base.ui'))


class check_dialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, layerPath, parent=None):
        """Constructor."""
        super(check_dialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.layerPath = layerPath
        
        try:
            self.readConfiguration()
            if self.configRead:
                self.loadChecks()
        except:
            pass
        
    def readConfiguration(self):
        # Read the config
        config = ConfigParser.ConfigParser()
        configFilePath = os.path.join(os.path.dirname(__file__), 'config.cfg')
        config.read(configFilePath)
        
        self.config = []
        for section in config.sections():
            if section == 'xgApps':
                c={}
                c['xgApps_local'] = config.get(section, 'local_folder')
                c['xgApps_network'] = config.get(section, 'network_folder')
                self.config.append(c)
                self.configRead = True
            # end if
        # next
    
    def getSelectedCheck(self):
        return self.lst_checks.currentItem
        
    def getProduceWordReport(self):
        return self.chk_word_report.checked
        
    def getWordReportPath(self):
        return self.txt_word_report.plainText
        
    def getCreatedBy(self):
        return self.txt_created_by
        
    def loadChecks(self):
        cfg = self.config[0]
        xgcc_db_path = os.path.join(os.path.join(cfg['xgApps_network'],'Constraints','xgcc.sqlite'))
        xgcc = xgcc_db(xgcc_db_path)
        if xgcc.dbExists:
            checks = xgcc.getCheckList(self.layerPath)
            for item in checks:
                self.lst_checks.addItem(item)
            #next
        else:
            QtGui.QMessageBox.critical(self.iface.mainWindow(), 'xgConstraintChecker Error', '%s could not be found. Please check the configuration and try again' % xgcc_db)

    def openFileDialog(self):
        filename1 = QtGui.QFileDialog.getOpenFileName()
        self.txt_word_report.setPlainText(filename1)
    
    def runSelected(self, selectedCheck):
        self.accept()
        
    def accept(self):
        if self.lst_checks.selectedItems.count > 0:
            check = self.lst_checks.currentItem
            if check.checkID != -1:
                if self.chk_word_report.checked & self.txt_word_report.text.length != 0:
                    self.setResult(QtGui.QDialog.Accepted)
                    return
                else:
                    QtGui.QMessageBox.critical(self.iface.mainWindow(), "xgConstraintChecker Error", "A report path must be entered if Produce Word Report is ticked. Please try again.")
            else:
                QtGui.QMessageBox.critical(self.iface.mainWindow(), "xgConstraintChecker Error", "No check selected. Please try again")
        else:
            QtGui.QMessageBox.critical(self.iface.mainWindow(), "xgConstraintChecker Error", "No check selected. Please try again")
    
    def reject(self):
        self.setResult(QtGui.QDialog.Rejected)
        return
