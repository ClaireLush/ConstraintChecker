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

from PyQt4.QtGui import QDialog, QMessageBox
from PyQt4.QtCore import Qt
from config_dialog_ui import Ui_config_dialog


class config_dialog(QDialog, Ui_config_dialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.iface = iface

        try:
            self.readConfiguration()
        except:
            pass

    def readConfiguration(self):
        # Read the config
        config = ConfigParser.ConfigParser()
        configFilePath = os.path.join(os.path.dirname(__file__), 'config.cfg')
        config.read(configFilePath)

        dbConfigRead = False
        for section in config.sections():
            if section == 'xgApps':
                try:
                    self.txt_xgApps_local.setPlainText(config.get(section, 'local_folder'))
                except:
                    # Ignore
                try:
                    self.txt_xgApps_network.setPlainText(config.get(section, 'network_folder'))
                except:
                    # Ignore
                try:
                    showResults = config.get(section, 'show_results')
                    if showResults == "yes":
                        self.chk_show_results.setChecked(True)
                    else:
                        self.chk_show_results.setChecked(False)
                except:
                    self.chk_show_results.setChecked(True)
            if section == 'dbConfig':
                index = self.cbo_db_type.findText(config.get(section, 'db_type'), Qt.MatchFixedString)
                if index >= 0:
                    self.cbo_db_type.setCurrentIndex(index)
                self.txt_host.setPlainText(config.get(section, 'host'))
                self.txt_port.setPlainText(config.get(section, 'port'))
                self.txt_db.setPlainText(config.get(section, 'database'))
                trusted = config.get(section, 'trusted')
                if trusted == "yes":
                    self.chk_trusted.setCheckState(Qt.Checked)
                    self.txt_user.setEnabled(False)
                    self.txt_pwd.setEnabled(False)
                else:
                    self.chk_trusted.setCheckState(Qt.Unchecked)
                    self.txt_user.setPlainText(config.get(section, 'user'))
                    self.txt_pwd.setPlainText(config.get(section, 'password'))
                createTable = config.get(section, 'new_table')
                if createTable == "yes":
                    self.rb_new.setChecked(True)
                    self.txt_table.setEnabled(False)
                    self.txt_geom.setEnabled(False)
                else:
                    self.rb_existing.setChecked(True)
                    self.txt_table.setPlainText(config.get(section, 'table'))
                    self.txt_geom.setPlainText(config.get(section, 'geom_col'))
                dbConfigRead = True
            # end if
        # next
        
        if not dbConfigRead:
            self.cbo_db_type.setCurrentIndex(2)
            self.rb_new.setChecked(True)
            self.txt_table.setEnabled(False)
            self.txt_geom.setEnabled(False)

    def saveConfiguration(self):
        # Read the config
        config = ConfigParser.RawConfigParser()
        configFilePath = os.path.join(os.path.dirname(__file__), 'config.cfg')

        section = 'xgApps'
        config.add_section(section)
        config.set(section, 'local_folder', self.txt_xgApps_local.toPlainText())
        config.set(section, 'network_folder', self.txt_xgApps_network.toPlainText())
        if self.chk_show_results.isChecked():
            config.set(section, 'show_results','yes')
        else:
            config.set(section, 'show_results','no')
        section = 'dbConfig'
        config.add_section(section)
        config.set(section, 'db_type', self.cbo_db_type.currentText())
        config.set(section, 'host', self.txt_host.toPlainText())
        config.set(section, 'port', self.txt_port.toPlainText())
        config.set(section, 'database', self.txt_db.toPlainText())
        if self.chk_trusted.isChecked():
            config.set(section, 'trusted', 'yes')
        else:
            config.set(section, 'trusted', 'no')
            config.set(section, 'user', self.txt_user.toPlainText())
            config.set(section, 'password', self.txt_pwd.toPlainText())
        if self.rb_new.isChecked():
            config.set(section, 'new_table','yes')
        else:
            config.set(section, 'new_table','no')
            config.set(section, 'table', self.txt_table.toPlainText())
            config.set(section, 'geom_col', self.txt_geom.toPlainText())

        try:
            with open(configFilePath, 'wb') as configfile:
                config.write(configfile)
        except:
            QMessageBox.critical(self.iface.mainWindow(), 'Save Failed', 'Failed to write the configuration to %s' % configFilePath)

    def enableDBFields(self, dbType):
        # clear the fields
        self.txt_host.clear()
        self.txt_port.clear()
        self.txt_db.clear()
        self.txt_user.clear()
        self.txt_pwd.clear()

        if dbType == u'PostGIS':
            self.txt_host.setEnabled(True)
            self.txt_port.setEnabled(True)
            self.txt_port.setPlainText('5432')
            self.grpLogin.setEnabled(True)
            self.chk_trusted.setCheckState(Qt.Unchecked)
            self.chk_trusted.setEnabled(False)
        elif dbType == u'Spatialite':
            self.txt_host.setEnabled(False)
            self.txt_port.setEnabled(False)
            self.grpLogin.setEnabled(False)
        elif dbType == u'SQL Server':
            self.txt_host.setEnabled(True)
            self.txt_port.setEnabled(False)
            self.grpLogin.setEnabled(True)
            self.chk_trusted.setCheckState(Qt.Checked)
            self.chk_trusted.setEnabled(True)

    def enableLoginFields(self, checkState):
        if checkState == Qt.Checked:
            # clear the fields
            self.txt_user.clear()
            self.txt_pwd.clear()
            self.txt_user.setEnabled(False)
            self.txt_pwd.setEnabled(False)
        else:
            self.txt_user.setEnabled(True)
            self.txt_pwd.setEnabled(True)

    def accept(self):
        #Save the settings to config file
        try:
            self.saveConfiguration()
        except Exception as e:
            print e
            pass
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)
