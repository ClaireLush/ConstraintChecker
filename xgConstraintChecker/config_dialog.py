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
import resources

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'config_dialog_base.ui'))


class config_dialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(config_dialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        try:
            readConfiguration(self)
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
                self.txt_xgApps_local.setPlainText(config.get(section, 'network_folder'))
            if section == 'dbConfig':
                index = cbo_db_type.findText(config.get(section, 'dbType'), QtCore.Qt.MatchFixedString)
                if index >= 0:
                    cbo_db_type.setCurrentIndex(index)
                self.txt_host.setPlainText(config.get(section, 'host'))
                self.txt_port.setPlainText(config.get(section, 'port'))
                self.txt_db.setPlainText(config.get(section, 'database'))
                trusted = config.get(section, 'trusted')
                if trusted == "yes":
                    self.chk_trusted.checked = True
                else:
                    self.chk_trusted.checked = False
                    self.txt_user.setPlainText(config.get(section, 'user'))
                    self.txt_pwd.setPlainText(config.get(section, 'password'))
                createTable = config.get(section, 'new_table')
                if createTable == "yes":
                    self.rb_new.checked = True
                else:
                    self.rb_existing.checked = True
                    self.txt_table.setPlainText(config.get(section, 'table'))
					self.txt_geom.setPlainText(config.get(section, 'geom_col'))
            # end if
        # next
    
    def saveConfiguration(self):
        # Read the config
        config = ConfigParser.RawConfigParser()
        configFilePath = os.path.join(os.path.dirname(__file__), 'config.cfg')
        
        section == 'xgApps'
        config.set(section, 'local_folder', self.txt_xgApps_local.plainText)
        config.set(section, 'network_folder', self.txt_xgApps_network.plainText)
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
            raise Exception('Failed to write the configuration to %s' % filePath)
    
    def enableDBFields(dbType):
        # clear the fields
        txt_host.clear()
        txt_port.clear()
        txt_db.clear()
        txt_user.clear()
        txt_pwd.clear()
        
        if dbType == 'PostGIS':
            txt_host.enabled = True
            txt_port.enabled = True
            txt_port.plainText = '5432'
            grp_login.enabled = True
            chk_trusted.checked = False
            chk_trusted.enabled = False
        elif dbType == 'Spatialite':
            txt_host.enabled = False
            txt_port.enabled = False
            grpLogin.enabled = False
        elif dbType =='SQL Server'
            txt_host.enabled = True
            txt_port.enabled = False
            grp_login.enabled = True
            chk_trusted.checked = True
            chk_trusted.enabled = False
    
    def enableLoginFields(checked):
        if checked == True:
            # clear the fields
            txt_user.clear()
            txt_pwd.clear()
            txt_user.enabled = False
            txt_pwd.enabled = False
        else:
            txt_user.enabled = True
            txt_pwd.enabled = True
        

    def accept()
        #Save the settings to config file
        saveConfiguration(self)
        self.setResult(QDialog::Accepted)
        self.close()
    
    def reject()
        self.setResult(QDialog::Rejected)
        self.close()
