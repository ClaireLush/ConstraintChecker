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

from PyQt4 import QtCore, QtGui
from config_dialog_ui import Ui_config_dialog


class config_dialog(QtGui.QDialog, Ui_config_dialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.setupUi(self)

        try:
            self.readConfiguration()
        except:
            pass

    def readConfiguration(self):
        # Read the config
        config = ConfigParser.ConfigParser()
        configFilePath = os.path.join(os.path.dirname(__file__), 'config.cfg')
        config.read(configFilePath)

        for section in config.sections():
            if section == 'xgApps':
                self.txt_xgApps_local.setPlainText(config.get(section, 'local_folder'))
                self.txt_xgApps_network.setPlainText(config.get(section, 'network_folder'))
            if section == 'dbConfig':
                index = self.cbo_db_type.findText(config.get(section, 'dbType'), QtCore.Qt.MatchFixedString)
                if index >= 0:
                    self.cbo_db_type.setCurrentIndex(index)
                self.txt_host.setPlainText(config.get(section, 'host'))
                self.txt_port.setPlainText(config.get(section, 'port'))
                self.txt_db.setPlainText(config.get(section, 'database'))
                trusted = config.get(section, 'trusted')
                if trusted == "yes":
                    self.chk_trusted.checked = True
                    self.txt_user.enabled = False
                    self.txt_pwd.enabled = False
                else:
                    self.chk_trusted.checked = False
                    self.txt_user.setPlainText(config.get(section, 'user'))
                    self.txt_pwd.setPlainText(config.get(section, 'password'))
                createTable = config.get(section, 'new_table')
                if createTable == "yes":
                    self.rb_new.checked = True
                    self.txt_table.enabled = False
                    self.txt_geom.enabled = False
                else:
                    self.rb_existing.checked = True
                    self.txt_table.setPlainText(config.get(section, 'table'))
                    self.txt_geom.setPlainText(config.get(section, 'geom_col'))
                dbConfigRead = True
            # end if
        # next
        
        if not dbConfigRead:
            self.cbo_db_type.setCurrentIndex(2)
            self.rb_new.checked = True
            self.txt_table.enabled = False
            self.txt_geom.enabled = False

    def saveConfiguration(self):
        # Read the config
        config = ConfigParser.RawConfigParser()
        configFilePath = os.path.join(os.path.dirname(__file__), 'config.cfg')

        section = 'xgApps'
        config.set(section, 'local_folder', self.txt_xgApps_local.plainText)
        config.set(section, 'network_folder', self.txt_xgApps_network.plainText)
        section = 'dbConfig'
        config.set(section, 'db_type', self.cbo_db_type.selectedText)
        config.set(section, 'host', self.txt_host.plainText)
        config.set(section, 'port', self.txt_port.plainText)
        config.set(section, 'database', self.txt_db.plainText)
        if self.chk_trusted.checked:
            config.set(section, 'trusted', 'yes')
        else:
            config.set(section, 'trusted', 'no')
            config.set(section, 'user', self.txt_user.plainText)
            config.set(section, 'password', self.txt_pwd.plainText)
        if self.rb_new.checked:
            config.set(section, 'new_table','yes')
        else:
            config.set(section, 'new_table','no')
            config.set(section, 'table', self.txt_table.plainText)
            config.set(section, 'geom_col', self.txt_geom.plainText)

        try:
            with open(configFilePath, 'wb') as configfile:
                config.write(configfile)
        except:
            raise Exception('Failed to write the configuration to %s' % configFilePath)

    def enableDBFields(self, dbType):
        # clear the fields
        self.txt_host.clear()
        self.txt_port.clear()
        self.txt_db.clear()
        self.txt_user.clear()
        self.txt_pwd.clear()

        if dbType == 'PostGIS':
            self.txt_host.enabled = True
            self.txt_port.enabled = True
            self.txt_port.plainText = '5432'
            self.grp_login.enabled = True
            self.chk_trusted.checked = False
            self.chk_trusted.enabled = False
        elif dbType == 'Spatialite':
            self.txt_host.enabled = False
            self.txt_port.enabled = False
            self.grpLogin.enabled = False
        elif dbType =='SQL Server':
            self.txt_host.enabled = True
            self.txt_port.enabled = False
            self.grp_login.enabled = True
            self.chk_trusted.checked = True
            self.chk_trusted.enabled = False

    def enableLoginFields(self, checkState):
        if checkState == QtCore.Qt.Checked:
            # clear the fields
            self.txt_user.clear()
            self.txt_pwd.clear()
            self.txt_user.enabled = False
            self.txt_pwd.enabled = False
        else:
            self.txt_user.enabled = True
            self.txt_pwd.enabled = True

    def accept(self):
        #Save the settings to config file
        self.saveConfiguration(self)
        self.setResult(QtGui.QDialog.Accepted)
        self.close()
        return

    def reject(self):
        self.setResult(QtGui.QDialog.Rejected)
        self.close()
        return
