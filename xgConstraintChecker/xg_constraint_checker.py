# -*- coding: utf-8 -*-
"""
/***************************************************************************
 xgConstraintChecker
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject, SIGNAL
from PyQt4.QtGui import QAction, QDialog, QIcon, QMessageBox
from qgis.core import QgsGeometry, QgsMapLayer
from qgis.gui import QgsMessageBar

# Initialize Qt resources from file resources.py
import resources

# Import the code for the dialogs/tools
from config_dialog import config_dialog
from check_dialog import check_dialog
from checker import checker
from freehand_polygon_maptool import FreehandPolygonMapTool

import ConfigParser
import sys, traceback
import os.path
import subprocess
from datetime import datetime

class xgConstraintChecker:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir,'i18n','xgConstraintChecker_{}.qm'.format(locale))
        
        # initialize config
        self.configRead = False
        
        # initialize freeHandTool
        self.freeHandTool = FreehandPolygonMapTool(self.iface.mapCanvas())

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&ESDM Constraint Checker')
        self.toolbar = self.iface.addToolBar(u'xgConstraintChecker')
        self.toolbar.setObjectName(u'xgConstraintChecker')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('xgConstraintChecker', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.add_action(
            ':/plugins/xgConstraintChecker/checker_config.png',
            text=self.tr(u'Configure Plugin'),
            callback=self.openConfiguration,
            add_to_toolbar=False,
            status_tip=u'Opens a dialog to configure Constraint Checker plugin',
            parent=self.iface.mainWindow())
        self.add_action(
            ':/plugins/xgConstraintChecker/checker_config.png',
            text=self.tr(u'Configure Checks'),
            callback=self.openSetup,
            status_tip=u'Opens a dialog to configure checks',
            parent=self.iface.mainWindow())
        self.add_action(
            ':/plugins/xgConstraintChecker/checker_selected.png',
            text=self.tr(u'Check Selected Feature'),
            callback=self.checkSelectedGeometry,
            status_tip=u'Run a constraint check on the selected feature',
            add_to_menu=False,
            parent=self.iface.mainWindow())
        self.add_action(
            ':/plugins/xgConstraintChecker/checker_freehand.png',
            text=self.tr(u'Check Freehand Feature'),
            callback=self.checkFreehandGeometry,
            status_tip=u'Draw a freehand feature and run a constraint check',
            add_to_menu=False,
            parent=self.iface.mainWindow())

        QObject.connect(self.freeHandTool, SIGNAL("geometryReady(PyQt_PyObject)"), self.receiveFeature)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ESDM Constraint Checker'),
                action)
            self.iface.removeToolBarIcon(action)
        QObject.disconnect(self.freeHandTool, SIGNAL("geometryReady(PyQt_PyObject)"), self.receiveFeature)
        # remove the toolbar
        del self.toolbar


    def receiveFeature(self, geom):
        crs = self.iface.mapCanvas().mapRenderer().destinationCrs()
        epsg = int( crs.authid().split('EPSG:')[1] )
        self.iface.mapCanvas().unsetMapTool( self.freeHandTool )
        self.constraintCheck(geom, epsg)


    def checkSelectedGeometry(self):
        """ The user should already have a feature selected.  Ensure 
        this is the case and then send the geometry to the main 
        function. """
        
        errTitle = 'No feature selected'
        errMsg = 'Please select a single feature in a loaded vector layer.'
        
        if self.iface.mapCanvas().layerCount() < 1:
            QMessageBox.critical(self.iface.mainWindow(), errTitle, errMsg)
            return
        
        currentLayer = self.iface.mapCanvas().currentLayer()
        if currentLayer is None or currentLayer.type() != QgsMapLayer.VectorLayer:
            QMessageBox.critical(self.iface.mainWindow(), errTitle, errMsg)
            return
        
        if currentLayer.selectedFeatureCount() != 1:
            QMessageBox.critical(self.iface.mainWindow(), errTitle, errMsg)
            return
        
        # By this point the user has a single, existing feature selected
        # Now pass the geometry to the query
        
        # Due to an existing bug ? 777
        # We need to fetch the list first before taking off the feature we want
        selFeats = currentLayer.selectedFeatures()
        feature = selFeats[0]
        geom = QgsGeometry( feature.geometry() )
        authid = currentLayer.crs().authid()
        
        layerPath = currentLayer.dataProvider().dataSourceURI()
        
        try:
            epsg = int(authid.split('EPSG:')[1])
        except:
            QMessageBox.critical(self.iface.mainWindow(), 'Failed to determine coordinate system', 'Please ensure the layer to which the query feature belongs has a coordinate system set.')
            return
        self.constraintCheck(geom, epsg, layerPath, feature)
        
    
    def checkFreehandGeometry(self):
        
        self.iface.messageBar().pushMessage("Constraint Checker", \
            "Please digitise your area of interest - Right-click to add last vertex.", \
            level=QgsMessageBar.INFO, duration=10)
        self.iface.mapCanvas().setMapTool(self.freeHandTool)
        
    
    def constraintCheck(self, queryGeom, epsg, layerPath='', fields=None):
        # Prompt user to select which check to run
        chkDlg = check_dialog(layerPath)
        result = chkDlg.exec_()
        if result == QDialog.Rejected:
            #User pressed cancel
            return
        
        check = chkDlg.getSelectedCheck()
        checkID = check[0]
        checkName = check[1]
        wordReport = chkDlg.getProduceWordReport()
        if wordReport == True:
            reportPath = chkDlg.getWordReportPath()
            createdBy = chkDlg.getCreatedBy()
        chkDlg.deleteLater()
        
        # Prompt the user for a reference number
        #refDlg = ReferenceNumberDialog()
        #result = refDlg.exec_()
        #if result == QDialog.Rejected:
        #    # User pressed cancel
        #    return
        #refNumber = refDlg.getRefNumber()
        #refDlg.deleteLater()
        
        d0 = datetime(2002,01,01)
        d1 = datetime.now()
        refNumber = (d1-d0).total_seconds()
        
        try:
            c = checker(self.iface, checkID, checkName, refNumber)
            c.check(queryGeom, epsg, layerPath, fields)
            c.display()
            if wordReport == True:
                siteRef = c.getSiteRef()
                resultCon = c.getResultCon()
                resultTable = c.getResultTable()
                mapPath = c.getMapPath()
                if resultTable[:3] == 'tmp':
                    if mapPath == None:
                        self.createWordReport(siteRef, checkID, checkName, reportPath, createdBy, resultCon, resultTable)
                    else:
                        self.createWordReport(siteRef, checkID, checkName, reportPath, createdBy, resultCon, resultTable, mapFile=mapPath)
                else:
                    if mapPath == None:
                        self.createWordReport(siteRef, checkID, checkName, reportPath, createdBy, resultCon, resultTable, refNumber)
                    else:
                        self.createWordReport(siteRef, checkID, checkName, reportPath, createdBy, resultCon, resultTable, refNumber, mapFile=mapPath)
        except:
            QMessageBox.critical(self.iface.mainWindow(), 'Query Failed', 'The query failed and the detailed error was:\n\n%s' % traceback.format_exc() )
    
    
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
                
    
    def openConfiguration(self):
        # Display the configuration editor dialog
        cfgDlg = config_dialog()
        dlgCode = cfgDlg.exec_()
        if dlgCode == QDialog.Accepted:
            self.readConfiguration()
        cfgDlg.deleteLater()

    def openSetup(self):
        # Run the standard Constraint Checker Setup EXE
        if self.configRead == False:
            try:
                self.readConfiguration()
            except:
                pass
        
        xgAppsCfg = self.config[0]
        exePath = os.path.join(xgAppsCfg['xgApps_local'],'Constraints','xgCCSU.exe') 
        if exePath != '':
            if os.path.isfile(exePath):
                subprocess.Popen(exePath)
            else:
                QMessageBox.critical(self.iface.mainWindow(), 'Constraint Checker Setup Not Found', 'xgCCSU.exe cannot be found at the specified path: ' + exePath)
        else:
            QMessageBox.critical(self.iface.mainWindow(), 'Invalid Configuration', 'xgApps local folder is not configured. Please configure the plugin and try again.')
            
    def createWordReport(self, siteRef, checkID, checkName, reportPath, createdBy, resultCon, resultTable, resultKey=None, mapFile=None):
        # Run the standard Constraint Checker EXE
        if self.configRead == False:
            try:
                self.readConfiguration()
            except:
                pass

        for cfg in self.config:
            xgAppsLocal = cfg['xgApps_local']                 
            
        exePath = os.path.join(xgAppsLocal,'Constraints','xgCC.exe') 
        if exePath != '':
            if os.path.isfile(exePath):
                args = []
                args.append(exePath)
                args.append('qgis')
                args.append('siteRef=%s' % siteRef)
                args.append('chkID=%s' % checkID)
                args.append('chkName=%s' % checkName)
                args.append('rptName=%s' % reportPath)
                args.append('rptName=%s' % createdBy)
                args.append('rsltCon=%s' % resultCon)
                args.append('rsltTable=%s' % resultTable)
                if resultKey != None:
                    args.append('rsltKey=%s' % resultKey)
        
                subprocess.Popen([exePath,args])
            else:
                QMessageBox.critical(self.iface.mainWindow(), 'Constraint Checker Setup Not Found', 'xgCCSU.exe cannot be found at the specified path: ' + exePath)
        else:
            QMessageBox.critical(self.iface.mainWindow(), 'Invalid Configuration', 'xgApps local folder is not configured. Please configure the plugin and try again.')