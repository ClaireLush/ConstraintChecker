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
        
        self.cb
        
    def readConfiguration(self):
        # Read the config
        config = ConfigParser.ConfigParser()
        configFilePath = os.path.join(os.path.dirname(__file__), 'config.cfg')
        config.read(configFilePath)
        
        self.config = []
        for section in config.sections():
            if section == 'Constraints':
                c={}
                c['exePrompt'] = config.get(section, 'exePrompt')
                c['dbType'] = config.get(section, 'dbType')
                c['host'] = config.get(section, 'host')
                c['port'] = config.get(section, 'port')
                c['database'] = config.get(section, 'database')
                self.config.append(c)
                self.configRead = True
            # end if
        # next
    
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
            grpLogin.enabled = True
        elif dbType == 'Spatialite':
            txt_host.enabled = False
            txt_port.enabled = False
            grpLogin.enabled = False
        elif dbType =='SQL Server'
            txt_host.enabled = True
            txt_port.enabled = False
            grpLogin.enabled = True
    
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
    
    def reject()
