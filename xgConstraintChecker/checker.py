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

# Import the PyQt and QGIS libraries
from PyQt4.QtGui import QMessageBox 
from qgis.core import *
from qgis.gui import QgsMessageBar

# Import custom class for reading XGCC config
from xgcc_db import xgcc_db
# Import custom class for generating grid ref string
from grid_ref import GridRef
import utils

import psycopg2
import pyodbc
from pyspatialite import dbapi2
import ConfigParser
import os.path
import sys

class checker:
    
    def __init__(self, iface, checkID, checkName, refNumber):
        
        self.iface = iface
        self.checkID = checkID
        self.checkName = checkName
        self.refNumber = refNumber
        
        # Read the config
        self.readConfiguration()
        
    
    def readConfiguration(self, fileName ='config.cfg'):
        # Read the config
        config = ConfigParser.ConfigParser()
        
        if fileName == 'config.cfg':
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
                if section == 'dbConfig':
                    c={}
                    c['db_type'] = config.get(section, 'db_type')
                    c['host'] = config.get(section, 'host')
                    c['port'] = config.get(section, 'port')
                    c['database'] = config.get(section, 'database')
                    trusted = config.get(section, 'trusted')
                    if trusted == "yes":
                        c['trusted'] = True
                    else:
                        c['trusted'] = False
                        c['user'] = config.get(section, 'user')
                        c['password'] = config.get(section, 'password')
                    createTable = config.get(section, 'new_table')
                    if createTable == "yes":
                        c['new_table'] = True
                    else:
                        c['new_table'] = False
                        c['table'] = config.get(section, 'table')
                        c['geom'] = config.get(section, 'geom_col')
                    self.config.append(c)
                    self.configRead = True
        elif fileName == 'XG_SYS.ini':
            if self.configRead:
                xgAppsCfg = self.config[0]
                configFilePath = os.path.join(xgAppsCfg['xgApps_network'], 'XG_SYS.ini')
                config.read(configFilePath)
                        
                for section in config.sections():
                    if section == 'Constraints':
                        try:
                            self.advDisp = config.get(section,'AdvDisp')
                        except:
                            self.advDisp = 'F'
                        try:
                            self.exportCSV = config.get(section,'ExportCSV')
                        except:
                            self.exportCSV = 'F'
                        try:
                            self.includeMap = config.get(section, 'IncludeMap')
                        except:
                            self.includeMap = 'F'
                        try:
                            self.reportCSV = config.get(section,'ReportCSV')
                        except:
                            self.reportCSV = os.path.join(xgAppsCfg['xgApps_local'], 'Report.csv')
                        try:
                            self.txtRptFile = config.get(section, 'TextRptFile')
                        except:
                            self.txtRptFile = os.path.join(xgAppsCfg['xgApps_local'], 'check.txt')
                        try:
                            self.txtFileColWidth = int(config.get(section, 'TextFileColumnWidth'))
                        except:
                            self.txtFileColWidth = 30
                            
                            
    def getDbConnection(self, dbType):
        dbConfig = self.config[1]
        try:
            if dbType == 'PostGIS':
                dbConn = psycopg2.connect( database = dbConfig['database'],
                                           user = dbConfig['user'],
                                           password = dbConfig['password'],
                                           host = dbConfig['host'],
                                           port = int(dbConfig['port']))
                dbConn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            elif dbType == 'Spatialite':
                dbConn = dbapi2.connect(dbConfig['database'])
            elif dbType == 'SQL Server':
                drv = None
                drivers = pyodbc.drivers()
                if 'ODBC Driver 13 for SQL Server' in drivers:
                    drv = '{ODBC Driver 13 for SQL Server}'
                elif 'ODBC Driver 11 for SQL Server' in drivers:
                    drv = '{ODBC Driver 11 for SQL Server}'
                elif 'SQL Server Native Client 11.0' in drivers:
                    drv = '{SQL Server Native Client 11.0}'
                elif 'SQL Server Native Client 10.0' in drivers:
                    drv = '{SQL Server Native Client 11.0}'
                elif 'SQL Server' in drivers:
                    drv = '{SQL Server}'
                else:
                    QMessageBox.critical(self.iface.mainWindow(), 'No SQL Server drivers', 'No SQL Server ODBC drivers could be found.')
                    return None
                    
                if dbConfig['trusted'] == True:
                    conStr = 'DRIVER={0};SERVER={1};DATABASE={2};Trusted_Connection=yes'.format(drv, dbConfig['host'], dbConfig['database'])
                else:
                    conStr = 'DRIVER={0};SERVER={1};DATABASE={2};UID={3};PWD={4}'.format(drv, dbConfig['host'], dbConfig['database'], dbConfig['user'], dbConfig['password'])
                dbConn = pyodbc.connect(conStr)
                
            return dbConn
        except:
            QMessageBox.critical(self.iface.mainWindow(), 'Invalid Database Configuration', 'The configured results database could not be opened. Please check and try again.')
            return None
                
                
    def getSiteRef(self):
        return self.siteRef
        
        
    def getSiteGridRef(self):
        return self.gridRef
        
        
    def setResultCon(self, uri):
        dbCfg = self.config[1]
        if self.dbType == 'PostGIS':
            if dbCfg['trusted'] == True:
                uri.setConnection(dbCfg['host'],str(dbCfg['port']),dbCfg['database'],'','')
            else:
                uri.setConnection(dbCfg['host'],str(dbCfg['port']),dbCfg['database'],dbCfg['user'],dbCfg['password'])
        elif self.dbType == 'SQL Server':
            if dbCfg['trusted'] == True:
                uri.setConnection(dbCfg['host'],'',dbCfg['database'],'','')
            else:
                uri.setConnection(dbCfg['host'],'',dbCfg['database'],dbCfg['user'],dbCfg['password'])
        elif self.dbType == 'Spatialite':
            uri.setDatabase(dbCfg['database'])

        return uri
            
    def getMapPath(self):
        return self.mapPath

    
    def getResultTable(self):
        if self.schema != '':
            return '{0}.{1}'.format(self.schema, self.tableName)
        else:
            return self.tableName
            
            
    def getVectorLayer(self, dbType, uri, layerName, geomType=None, geomCol=None):
        if geomType != None:
            uri.setWkbType(geomType)
        
            if geomType == QgsWKBTypes.Point:
                strGeomType = 'POINT'
            elif geomType == QgsWKBTypes.LineString:
                strGeomType = 'LINESTRING'
            elif geomType == QgsWKBTypes.Polygon:
                strGeomType = 'POLYGON'
            
        if dbType == 'Spatialite':
            if geomType != None:
                if uri.sql() == '':
                    uri.setSql("GeometryType({0}) Like '%{1}'".format(geomCol, strGeomType))
                else:
                    uri.setSql("{0} AND GeometryType({1}) Like '%{2}'".format(uri.sql(), geomCol, strGeomType))
            lyr = QgsVectorLayer(uri.uri(), layerName, "spatialite")
        elif dbType == 'PostGIS':
            if geomType != None:
                if uri.sql() == '':
                    uri.setSql("GeometryType({0}) Like '%{1}'".format(geomCol, strGeomType))
                else:
                    uri.setSql("{0} AND GeometryType({1}) Like '%{2}'".format(uri.sql(), geomCol, strGeomType))
            lyr = QgsVectorLayer(uri.uri(), layerName, "Postgres")
        elif dbType == 'SQL Server':
            if geomType != None:
                if uri.sql() == '':
                    uri.setSql("{0}.STGeometryType() Like '%{1}'".format(geomCol, strGeomType))
                else:
                    uri.setSql("{0} AND {1}.STGeometryType() Like '%{2}'".format(uri.sql(), geomCol, strGeomType))
            lyr = QgsVectorLayer(uri.uri(), layerName, "mssql")
        
        return lyr


    def cleanupFailedSearch(self, conn, layers):
        try:
            if layers != None:
                QgsMapLayerRegistry.instance().removeMapLayers(layers)
        except:
            pass

           
    def transformGeom(self, geom, src_srs, dst_epsg, user_defined = False):
        if not user_defined:
            crsSrc = QgsCoordinateReferenceSystem(src_srs,QgsCoordinateReferenceSystem.EpsgCrsId)
        else:
            crsSrc = QgsCoordinateReferenceSystem(src_srs, QgsCoordinateReferenceSystem.InternalCrsId)
        crsDst = QgsCoordinateReferenceSystem(dst_epsg, QgsCoordinateReferenceSystem.EpsgCrsId)

        xform = QgsCoordinateTransform(crsSrc, crsDst)
        
        geom.transform(xform)
        
        return geom

    
    # Currently only works with a single selection, should work with multiple?
    def runCheck(self, queryGeom, epsg_code, layerParams, fields):
        if self.configRead == False:
            return
            
        # Read XG_SYS.ini
        self.readConfiguration('XG_SYS.ini')
            
        # Reset path to map image
        self.mapPath = None
        
        # Close results table(s) if open
        rsltLayers = QgsMapLayerRegistry.instance().mapLayersByName('XGCC_Results')
        for rsltLayer in rsltLayers:
            QgsMapLayerRegistry.instance().removeMapLayer(rsltLayer.id())
        
        rsltLayers = QgsMapLayerRegistry.instance().mapLayersByName('XGCC_Results_Pt')
        for rsltLayer in rsltLayers:
            QgsMapLayerRegistry.instance().removeMapLayer(rsltLayer.id())
        
        rsltLayers = QgsMapLayerRegistry.instance().mapLayersByName('XGCC_Results_Line')
        for rsltLayer in rsltLayers:
            QgsMapLayerRegistry.instance().removeMapLayer(rsltLayer.id())
        
        rsltLayers = QgsMapLayerRegistry.instance().mapLayersByName('XGCC_Results_Poly')
        for rsltLayer in rsltLayers:
            QgsMapLayerRegistry.instance().removeMapLayer(rsltLayer.id())
            
        # Load xgcc db
        cfg = self.config[0]
        xgcc_db_path = os.path.join(os.path.join(cfg['xgApps_network'],'Constraints','xgcc.sqlite'))
        with xgcc_db(xgcc_db_path) as xgcc:
            if xgcc.dbExists:
                # Get check details and check layer details
                self.checkDetails = xgcc.getCheckDetails(self.checkID)
                self.checkLayerDetails = xgcc.getCheckLayerDetails(self.checkID)
                self.advDispDetails = xgcc.getAdvDispLayerDetails(self.checkID)
                self.datasetDetails = xgcc.getDatasetDetails()
                
        if self.checkLayerDetails == []:
            QMessageBox.critical(self.iface.mainWindow(), 'Invalid configuration', 'This constraint check has no valid searches.')
            return
        if self.advDispDetails == []:
            self.advDisp = 'F'
            
        # Ask whether user wishes to continue if selection not in ass_layer
        if layerParams['Path'].replace('/','\\') == self.checkDetails['ass_layer']:
            self.siteRef = fields[self.checkDetails['key_field']]
            if self.siteRef == '':
                if self.checkDetails['ass_layer_type'] == 'MapInfo TAB' or self.checkDetails['ass_layer_type'] == 'ESRI Shapefile':
                    filename = os.path.splitext(layerParams['Path'])[0]
                    self.siteRef = '{0} object'.format(filename)
                else:
                    temp = self.checkDetails['ass_layer'].split('#')
                    self.siteRef = '{0} object'.format(temp[1])
        else:
            if layerParams['Path'] == '':
                self.siteRef = '(Unknown)'
            else:
                self.siteRef = '{0} object'.format(layerParams['Name'])
            reply = QMessageBox.question(self.iface.mainWindow(), 'Unknown layer', 
                                         'You are about to do a {0} constraints check on an object from the {1} layer.\nAre you sure you wish to do this?'.format(self.checkName, layerParams['Name']), 
                                         QMessageBox.Yes, QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return
        
        self.rpt = []
        self.rpt.append('\n')
        self.rpt.append('{0} constraints check on {1}\n'.format(self.checkName, self.siteRef))
        
        includeGridRef = False
        if self.checkDetails['GridRef'] == 1:
            includeGridRef = True
            centroid = queryGeom.centroid().asPoint()
            gr = GridRef(centroid[0],centroid[1])
            if epsg_code == 27700:
                self.gridRef = gr.getOSGridRef(5)
            else:
                self.gridRef = gr.getGridRef()
        else:
            self.gridRef = None
        
        # Get database cursor        
        dbCfg = self.config[1]
        self.dbType = dbCfg['db_type']
        conn = self.getDbConnection(self.dbType)  
        if conn == None:
            return
        
        # Create results table if required
        if dbCfg['new_table'] == True:
            self.newTable = True
            self.tableName = 'tmp{0}'.format(self.refNumber)
            self.geomCol = 'geom'
               
            if self.dbType == 'Spatialite':
                self.schema = ''
                sql = 'CREATE TABLE "{0}" ("MI_PRINX" INTEGER PRIMARY KEY AUTOINCREMENT, "geom" BLOB, "Site" TEXT, "SiteGR" TEXT, "Layer_name" TEXT, '.format(self.tableName) + \
                      '"colum1" TEXT, "colum2" TEXT, "colum3" TEXT, "colum4" TEXT, "colum5" TEXT, "colum6" TEXT, "colum7" TEXT, ' + \
                      '"colum8" TEXT, "colum9" TEXT, "colum10" TEXT, "descCol" TEXT, "Distance" REAL, "DateCol" TEXT, "MI_STYLE" TEXT)'
            elif self.dbType == 'PostGIS':
                self.schema = 'public'
                sql = "CREATE TABLE public.{0} (mi_prinx serial PRIMARY KEY, geom geometry(Geometry,27700), site varchar(30), sitegr varchar(30), layer_name varchar(50), ".format(self.tableName.lower()) + \
                      "colum1 varchar(50), colum2 varchar(50), colum3 varchar(50), colum4 varchar(50), colum5 varchar(50), colum6 varchar(50), colum7 varchar(50), " + \
                      "colum8 varchar(50), colum9 varchar(50), colum10 varchar(50), desccol varchar(254), distance decimal(10,2), datecol varchar(40))"
            elif self.dbType == 'SQL Server':
                self.schema = 'dbo'
                sql = 'CREATE TABLE dbo.{0} (MI_PRINX int IDENTITY PRIMARY KEY, geom geometry, Site varchar(30), SiteGR varchar(30), Layer_Name varchar(50), '.format(self.tableName) + \
                      'colum1 varchar(50), colum2 varchar(50), colum3 varchar(50), colum4 varchar(50), colum5 varchar(50), colum6 varchar(50), colum7 varchar(50), ' + \
                      'colum8 varchar(50), colum9 varchar(50), colum10 varchar(50), descCol varchar(254), Distance decimal(10,2), DateCol varchar(40))'
            else:
                self.cleanupFailedSearch(conn, None)
                return
        
            try:  
                with conn, conn.cursor() as cur:
                    cur.execute(sql)
            except Exception as e:
                self.cleanupFailedSearch(conn, None)
                QMessageBox.critical(self.iface.mainWindow(), 'No results table', 'The results table could not be created: {0}'.format(e))
                return
        else:
            self.newTable = False
            if '.' in dbCfg['table']:
                self.schema = dbCfg['table'].split('.')[0]
                self.tableName = dbCfg['table'].split('.')[1]
            else:
                self.schema = ''
                self.tableName = dbCfg['table']
            self.geomCol = dbCfg['geom']
        
        
        # Prepare processing framework
        pluginDir = os.path.split(os.path.dirname(__file__))[0]
        sys.path.append(pluginDir)
        from processing.core.Processing import Processing
        Processing.initialize()
        from processing.tools import *
        
        for layer in self.checkLayerDetails:
            table = ''
            tableType = ''
            for dataset in self.datasetDetails:
                if dataset['name'] == layer['name']:
                    table = dataset['table']
                    tableType = dataset['tableType']
                    break
                                            
            if table == '':
                self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    "The dataset {0} was not found".format(layer['name']), \
                                                    level=QgsMessageBar.INFO) #, duration=10
                #go to next layer
                break
                
            includeDist = False
            includeDate = False
            dateField = ''
            
            if self.advDisp == 'T':
                for advDisp in self.advDispDetails:
                    if advDisp['UID'] == layer['UID']:
                        includeDist = advDisp['InclDist']
                        if includeDist == True:
                            dateField = advDisp['DateField']
                        if dateField != '':
                            includeDate = True
                    break
            
            
            # Open search layer and filter by WHERE clause if present
            try:
                layerName = "XGCC_{0}".format(layer['name'])
                whereClause = utils.formatCondition(layer['condition'])
                
                searchLayer = None
                if tableType == 'MapInfo TAB' or tableType == 'ESRI Shapefile' or tableType == None:
                    searchLayer = QgsVectorLayer(table, layerName, "ogr")
                    # Get WHERE clause format with "" around fields (not for MI) and \'value\' around strings
                    searchLayer.setSubsetString(whereClause)
                elif tableType == 'PostGIS':
                    uri = QgsDataSourceURI()
                    
                    # Get params from Table
                    tempCon = table.split('#')
                    tempConParams = tempCon[0].split(';')
                    for param in tempConParams:
                        tempParam = param.split('=')
                        if tempParam[0] == 'Host':
                            host = tempParam[1]
                        elif tempParam[0] == 'Port':
                            port = tempParam[1]
                        elif tempParam[0] == 'Database':
                            database = tempParam[1]
                        elif tempParam[0] == 'Username':
                            user = tempParam[1]
                        elif tempParam[0] == 'Password':
                            password = tempParam[1]
                    uri.setConnection(host,port,database,user,password)
                    
                    # Set database schema, table name, geometry column and optionally subset (WHERE clause)
                    tempTable = tempCon[1].split('.')
                    uri.setDataSource (tempTable[0], tempTable[1], tempCon[2], whereClause)
                    
                    searchLayer = QgsVectorLayer(uri.uri(),layerName,"postgres")    
                elif tableType == 'SQL Server':
                    # Get params from Table
                    tempCon = table.split('#')
                    uri = QgsDataSourceURI('MSSQL:{0}'.format(tempCon[0]))
                        
                    # Set database schema, table name, geometry column and optionally subset (WHERE clause)
                    tempTable = tempCon[1].split('.')
                    uri.setDataSource (tempTable[0], tempTable[1], tempCon[2], whereClause)
                    searchLayer = QgsVectorLayer(uri.uri(),layerName,"mssql")    
                else:
                    self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'The {0} layer is not a valid layer type. Continuing with next layer.'.format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10) 
                    continue
                    
                # Check configured table is valid
                if not searchLayer.dataProvider().isValid():
                    self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'The {0} layer is not valid. Continuing with next layer.'.format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10) 
                    continue
                
                # Check layer has features else ignore condition
                if searchLayer.featureCount == 0:
                    if layer['condition'] != '':
                        searchLayer.setSubset(None)
                        if searchLayer.featureCount > 0:
                            self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'The {0} layer condition is not valid, condition is being ignored.'.format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10)
                        else:
                            self.cleanupFailedSearch(None, [searchLayer])
                            self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'The {0} layer has no features. Continuing with next layer.'.format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10)
                            continue
                    else:
                        self.cleanupFailedSearch(None, [searchLayer])
                        self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'The {0} layer has no features. Continuing with next layer.'.format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10)
                        continue
            except Exception as e:
                self.cleanupFailedSearch(None, [searchLayer])
                self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'The {0} layer is not valid. Continuing with next layer.'.format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10) 
                continue
                        
            self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    "Finding: {0}".format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10)
            
            # Reset ignMin if geometry is not a polygon
            if queryGeom.type() != QgsWKBTypes.PolygonGeometry:
                layer['ignoreMin'] = True
            
            try:
                # Buffers in CRS distance units - translate geom if not in 27700, UTM or 3857
                if epsg_code != 27700:
                    queryGeom = self.transformGeom(queryGeom, epsg_code, 27700)
                    
                if layer['radius'] == 0:
                    bufferGeom = queryGeom
                elif layer['ignoreMin'] == -1:
                    bufferGeom = queryGeom.buffer(layer['radius'], 12)
                else:
                    # Create doughnut if possible
                    if layer['minRadius'] == 0:
                        innerGeom = queryGeom
                    else:
                        innerGeom = queryGeom.buffer(layer['minRadius'], 12)
                    outerGeom = queryGeom.buffer(layer['radius'], 12)    
                    
                    try:
                        bufferGeom = outerGeom.difference(innerGeom)
                    except Exception as e:
                        bufferGeom = queryGeom.buffer(layer['radius'], 12)

                
                # Insert bufferGeom into temporary layer
                bufferLayer = QgsVectorLayer("Polygon?crs=epsg:{0}".format(epsg_code),"tmpXGCC","memory")
                bufferFeat = QgsFeature()
                bufferFeat.setGeometry(bufferGeom)
                result = bufferLayer.dataProvider().addFeatures([bufferFeat])
                if result == False:
                    self.cleanupFailedSearch(Conn, [searchLayer, bufferLayer])
                    QMessageBox.critical(self.iface.mainWindow(), 'Layer creation failed', 'The site could not be saved to the temp layer.')
                    return
                bufferLayer.updateExtents()
                QgsMapLayerRegistry.instance().addMapLayer(bufferLayer)
                
                lyrCount = searchLayer.dataProvider().subLayerCount()
                if lyrCount == 0:
                    lyrCount = 1
                    searchLayers = [searchLayer]
                else:
                    searchLayers = []
                    for subLyr in searchLayer.dataProvider().subLayers():
                        params = subLyr.split(':')
                        subLayer = QgsVectorLayer('{0}|layerid={1}|geometrytype={2}'.format(table, params[0], params[3]), \
                                                  '{0}_{1}'.format(layerName, params[3]), "ogr")
                        subLayer.setSubsetString(searchLayer.subsetString())
                        searchLayers.append(subLayer)
                
                addHeadings = True
                featuresFound = False
                for i in range(lyrCount):
                    searchLayer = searchLayers[i]
                    
                    # Add layer to map
                    QgsMapLayerRegistry.instance().addMapLayer(searchLayer)
                    
                    # Select where filtered layer intersects bufferGeom
                    if searchLayer.wkbType() == QgsWKBTypes.Point:
                        general.runalg("qgis:selectbylocation", searchLayer, bufferLayer, u'within', 0)
                    else:
                        general.runalg("qgis:selectbylocation", searchLayer, bufferLayer, u'intersects', 0)
                    
                    noFeatures = searchLayer.selectedFeatureCount()
                    if noFeatures == 0:
                        self.cleanupFailedSearch(None, [searchLayer])
                        
                        if i == (lyrCount - 1) and featuresFound == False:
                            self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                                'No features found in {0} layer. Continuing with next layer.'.format(layer['name']), \
                                                                level=QgsMessageBar.INFO, duration=10) 
                            continue
                    else:
                        featuresFound = True
                    
                        if addHeadings == True:
                            self.rpt.append('\n')
                            if layer['desc'] != None:
                                self.rpt.append(layer['desc'] + '\n')
                            else:
                                self.rpt.append(layer['name'] + '\n')
                                
                            # Build lists of fields / headings
                            colNames = []
                            colLabels = []
                            noCols = 0
                            fileStr = ''
                            
                            # Check colName1 to colName10
                            for i in range(1,11):
                                tmpColName = 'colName{0}'.format(str(i))
                                tmpColLabel = 'colLabel{0}'.format(str(i))
                                if layer[tmpColName] != None:
                                    noCols+=1
                                    colNames.append(layer[tmpColName])
                                    if layer[tmpColLabel] != None:
                                        colLabels.append(layer[tmpColLabel])
                                    else:
                                        colLabels.append(layer[tmpColName])
                                        
                                    fileStr += colLabels[noCols - 1].ljust(self.txtFileColWidth)
                                    
                            if layer['descrCol'] != None:
                                includeDesc = True
                                if layer['descrLabel'] != None:
                                    descField = layer['descrLabel']
                                    fileStr += layer['descrLabel'].ljust(254)
                                else:
                                    descField = layer['descrCol']
                                    fileStr += layer['descrCol'].ljust(254)
                            else:
                                includeDesc = False
                                descField = ''
                                
                            if includeDist == True:
                                fileStr += 'Distance'.ljust(15)
                                
                            if includeDate == True:
                                fileStr += dateField.ljust(40)
                                
                            if len(colNames) > 0:
                                self.rpt.append(fileStr + '\n')
                                
                                if self.newTable:
                                    insertSQL = utils.getInsertSql('Headings', True, self.getResultTable(), len(colNames), inclDesc=includeDesc, inclDate=includeDate)
                                    valuesSQL = utils.getValuesSql('Headings', True, len(colNames), colLabels, inclDesc=includeDesc, 
                                                                   descVal=descField, inclDate=includeDate, dateVal=dateField)
                                else:
                                    insertSQL = utils.getInsertSql('Headings',False, self.getResultTable(), len(colNames), inclDesc=includeDesc, inclDate=includeDate)
                                    valuesSQL = utils.getValuesSql('Headings', True, len(colNames), colLabels, refNumber=self.refNumber, 
                                                                   inclDesc=includeDesc, descVal=descField, inclDate=includeDate, dateVal=dateField)
                                try: 
                                    with conn, conn.cursor() as cur:
                                        cur.execute(insertSQL + valuesSQL)
                                except Exception as e:
                                    self.cleanupFailedSearch(conn, [searchLayer, bufferLayer])
                                    QMessageBox.critical(self.iface.mainWindow(), 'Results table', 'Result headings could not be inserted into the {0} table: {1}'.format(self.tableName, e))
                                    return
                            addHeadings = False
                    
                        selFeats = searchLayer.selectedFeatures()
                        if self.checkDetails['Summary'] != 0:
                            # Calculate summary
                            sumTypes = initSummaryTypeArray()
                            tempVal = []
                            
                            for i in range(len(colNames)):
                                matchType = -1
                                for j in range(24): #cNoSummaryTypes
                                    if colNames[i] == sumTypes[j]:
                                        matchType = j
                                        break
                                
                                if matchType != -1:
                                    # Sum the field
                                    try:
                                        tempVal[i] = 0
                                        for n in range(noFeatures):
                                            tempVal[i] += selFeats[n][colNames[i]] 
                                    except:
                                        tempVal[i] = ''
                                else:  
                                     # TODO: if statements for each type to replace next line
                                     self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                        'Specific summary types not implemented. {1} Continuing with next field.'.format(layer['name'], e), \
                                                        level=QgsMessageBar.INFO, duration=5)
                                     tempVal[i] = ''
                            
                            self.rpt.append(utils.getPaddedValues('Summary', len(colNames), tempVal, self.txtFileColWidth) + '\n')
                            
                            if self.newTable:
                                insertSQL = utils.getInsertSql('Summary', True, self.getResultTable(), len(colNames), inclGridRef=includeGridRef)
                                valuesSQL = utils.getValuesSql('Summary', True, len(colNames), tempVal, layerName=layer['name'], siteRef = self.siteRef,
                                                               inclGridRef=includeGridRef, gridRef=self.gridRef)
                            else:
                                insertSQL = utils.getInsertSql('Summary', False, self.getResultTable(), len(colNames), inclGridRef=includeGridRef)
                                valuesSQL = utils.getValuesSql('Summary', True, len(colNames), tempVal, layerName=layer['name'], refNumber=self.refNumber, 
                                                               siteRef = self.siteRef, inclGridRef=includeGridRef, gridRef=self.gridRef)
                            try:    
                                with conn, conn.cursor() as cur:
                                    cur.execute(insertSQL + valuesSQL)
                            except Exception as e:
                                self.cleanupFailedSearch(conn, [searchLayer, bufferLayer])
                                QMessageBox.critical(self.iface.mainWindow(), 'Results table', 'Result heading could not be inserted into the {0} table: {1}'.format(self.tableName, e))
                                return
                        else:  
                            authid = searchLayer.crs().authid()
                            srsid = searchLayer.crs().srsid()
                            
                            if authid[:4] == 'EPSG':
                                search_srs = int(authid.split(':')[1])
                                user_srs = False
                            elif authid[:4] == 'USER':
                                search_srs = srsid
                                user_srs = True
                            else:
                                self.cleanupFailedSearch(conn, [searchLayer, bufferLayer])
                                QMessageBox.critical(self.iface.mainWindow(), 'Failed to determine coordinate system', 'Please ensure the layer to which the query feature belongs has a coordinate system set.')
                                return
                                
                            for feat in selFeats:
                                tempVal = []
                            
                                for i in range(len(colNames)):
                                    tempVal.insert(i,feat[colNames[i]])
                                    
                                if includeDesc:
                                    tempDescVal = feat[descField]
                                else:
                                    tempDescVal = ''
                                    
                                if includeDate:
                                    tempDateVal = feat[dateField]
                                else:
                                    tempDateVal = ''
                                    
                                tempGeom = feat.geometry()
                                if search_srs != 27700:
                                    if user_srs == False:
                                        tempGeom = self.transformGeom(tempGeom, search_srs, 27700)
                                    else:
                                        tempGeom = self.transformGeom(tempGeom, search_srs, 27700, user_defined = user_srs)
                                tempWKT = tempGeom.exportToWkt()
                                                            
                                if includeDist:
                                    tempDistVal = bufferGeom.distance(tempGeom)
                                else:
                                    tempDistVal = ''
                                    
                                self.rpt.append(utils.getPaddedValues('Record', len(colNames), tempVal, self.txtFileColWidth) + '\n')
                                
                                if self.newTable:
                                    insertSQL = utils.getInsertSql('Record', True, self.getResultTable(), len(colNames), inclGridRef=includeGridRef,
                                                                   inclDesc=includeDesc, inclDate=includeDate, inclDist=includeDist, geomCol=self.geomCol)
                                    valuesSQL = utils.getValuesSql('Record', True, len(colNames), tempVal, layerName=layer['name'], siteRef = self.siteRef, 
                                                                   inclGridRef=includeGridRef, gridRef=self.gridRef, inclDesc=includeDesc, descVal=tempDescVal, 
                                                                   inclDate=includeDate, dateVal=tempDateVal, inclDist=includeDist, distVal=tempDistVal, 
                                                                   dbType=self.dbType, geomWKT=tempWKT)
                                else:
                                    insertSQL = utils.getInsertSql('Record', False, self.getResultTable(), len(colNames), inclGridRef=includeGridRef,
                                                                   inclDesc=includeDesc, inclDate=includeDate, inclDist=includeDist, geomCol=self.geomCol)
                                    valuesSQL = utils.getValuesSql('Record', True, len(colNames), tempVal, layerName=layer['name'], refNumber=self.refNumber, 
                                                                   siteRef = self.siteRef, inclGridRef=includeGridRef, gridRef=self.gridRef, 
                                                                   inclDesc=includeDesc, descVal=descField, inclDate=includeDate, dateVal=dateField, 
                                                                   inclDist=includeDist, distVal=tempDistVal, dbType=self.dbType, geomWKT=tempWKT)
                                
                                try:    
                                    with conn, conn.cursor() as cur:
                                        cur.execute(insertSQL + valuesSQL)
                                except Exception as e:
                                    self.cleanupFailedSearch(conn, [searchLayer, bufferLayer])
                                    QMessageBox.critical(self.iface.mainWindow(), 'Results table', 'Result values could not be inserted into the {0} table: {1}'.format(self.tableName, e))
                                    return
                        # Close temporary search layer
                        QgsMapLayerRegistry.instance().removeMapLayer(searchLayer)
                        
                # Close temporary layers
                QgsMapLayerRegistry.instance().removeMapLayer(bufferLayer)
                
                
                # Message - Layer Finished
                self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    '{0} layer search finished.'.format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10) 
                                             
            except Exception as e:
                self.cleanupFailedSearch(None, [searchLayer, bufferLayer])
                self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'Error during {0} layer search. {1} Continuing with next layer.'.format(layer['name'], e), \
                                                    level=QgsMessageBar.INFO, duration=10) 
                continue
    
        try:
            conn.close()
        except:
            pass
                
        # Message - Finished
        self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                            '{0} search finished.'.format(self.checkName), \
                                            level=QgsMessageBar.INFO, duration=10) 
                                            
        # Save self.rpt to text file
        f = open(self.txtRptFile,'w+')
        f.writelines(self.rpt)
        f.close()
        
        # Open results
        uri = QgsDataSourceURI()
        uri = self.setResultCon(uri)
        if self.newTable == False:
            whereClause = '"ref_number" = {0}'.format(self.refNumber)
        else:
            whereClause = None
            
        uri.setDataSource(self.schema, self.tableName, self.geomCol, whereClause)
        resultsLayer = self.getVectorLayer(self.dbType, uri, "XGCC_Results")
        
        if resultsLayer.featureCount == 0:
            QMessageBox.information(self.iface.mainWindow(), 'No constraints found', 'The query did not locate any constraints.')
            return
        
        # Export as CSV if required
        if self.exportCSV:
            QgsVectorFileWriter.writeAsVectorFormat(resultsLayer, self.reportCSV, "System", None, "CSV")

        # Add map layers - 1 per geom type
        pointLayer = self.getVectorLayer(self.dbType, uri, "XGCC_Results_Pt", geomType = QgsWKBTypes.Point, geomCol = self.geomCol)
        if pointLayer.featureCount > 0:
            QgsMapLayerRegistry.instance().addMapLayer(pointLayer)
        uri.setSql(whereClause)
        lineLayer = self.getVectorLayer(self.dbType, uri, "XGCC_Results_Line", geomType = QgsWKBTypes.LineString, geomCol = self.geomCol)
        if lineLayer.featureCount > 0:
            QgsMapLayerRegistry.instance().addMapLayer(lineLayer)
        uri.setSql(whereClause)
        polyLayer = self.getVectorLayer(self.dbType, uri, "XGCC_Results_Poly", geomType = QgsWKBTypes.Polygon, geomCol = self.geomCol)
        if polyLayer.featureCount > 0:
            QgsMapLayerRegistry.instance().addMapLayer(polyLayer)
        
        
            
        
            
        