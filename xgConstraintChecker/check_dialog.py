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

import os
from configparser import ConfigParser

from qgis.PyQt import uic
from PyQt.QtCore import Qt
from PyQt.QtGui import QMessageBox
from PyQt.QtWidgets import QDialog, QFileDialog

from xgcc_db import xgcc_db
from check_dialog_ui import Ui_check_dialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
ui_check_dialog, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'check_dialog_base.ui'))


class CheckDialog(QDialog, ii_check_dialog):
    def __init__(self, iface, layerPath, parent=None):
        """Constructor."""
        super().__init__(parent)
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.iface = iface
        self.layerPath = layerPath

        try:
            self.readConfiguration()
            if self.configRead:
                xgCfg = self.config[0]
                self.chk_show_results.setChecked(xgCfg['show_results'])
                self.loadChecks()
        except Exception as e:
            print(type(e), e)

    def readConfiguration(self):
        # Read the config
        config = ConfigParser()
        configFilePath = os.path.join(os.path.dirname(__file__), 'config.cfg')
        config.read(configFilePath)

        self.configRead = False
        self.config = []
        for section in config.sections():
            if section == 'xgApps':
                c={}
                c['xgApps_local'] = config.get(section, 'local_folder')
                c['xgApps_network'] = config.get(section, 'network_folder')
                showResults = config.get(section, 'show_results')
                if showResults == "yes" or showResults == "":
                    c['show_results'] = True
                else:
                    c['show_results'] = False
                self.config.append(c)
                self.configRead = True
            # end if
        # next

    def getSelectedCheck(self):
        return self.checkList[self.lst_checks.currentRow()]

    def getShowResults(self):
        return self.chk_show_results.checkState()

    def getProduceWordReport(self):
        return self.chk_word_report.checkState()

    def getWordReportPath(self):
        return self.txt_word_report.toPlainText()

    def getCreatedBy(self):
        return self.txt_created_by.toPlainText()

    def loadChecks(self):
        cfg = self.config[0]
        xgcc_db_path = os.path.join(os.path.join(cfg['xgApps_network'],'Constraints','xgcc.sqlite'))
        xgcc = xgcc_db(xgcc_db_path)
        if xgcc.dbExists():
            self.checkList = xgcc.getCheckList(self.layerPath)
            for item in self.checkList:
                self.lst_checks.addItem(item.CheckName())
            #next
        else:
            QMessageBox.critical(self.iface.mainWindow(), 'xgConstraintChecker Error', '%s could not be found. Please check the configuration and try again' % xgcc_db)

    def openFileDialog(self):
        filename1 = QFileDialog.getSaveFileName(filter="Word Document (*.docx);;Word 97-2003 Document (*.doc)")
        self.txt_word_report.setPlainText(filename1)

    def runSelected(self):
        self.accept()

    def accept(self):
        try:
            check = self.checkList[self.lst_checks.currentRow()]
            if check.CheckID() != -1:
                if self.chk_word_report.checkState() == Qt.Checked:
                    if len(self.txt_word_report.toPlainText()) != 0:
                        QDialog.accept(self)
                    else:
                        QMessageBox.critical(self.iface.mainWindow(), "xgConstraintChecker Error", \
                            "A report path must be entered if Produce Word Report is ticked. Please try again.")
                else:
                    QDialog.accept(self)
            else:
                QMessageBox.critical(self.iface.mainWindow(), "xgConstraintChecker Error", "No check selected. Please try again")
        except:
            QMessageBox.critical(self.iface.mainWindow(), "xgConstraintChecker Error", "No check selected. Please try again")

    def reject(self):
        QDialog.reject(self)
