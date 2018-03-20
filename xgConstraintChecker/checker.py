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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import QSqlDatabase
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
import sys, traceback

class ResultModel(QAbstractTableModel):
    
    def __init__(self, colCount, headerNames, parent=None, *args):
        QAbstractTableModel.__init__(self)
        self.colCount = colCount
        # data is a list of rows
        # each row contains the columns
        self.data = []
        self.headerNames = headerNames
        
    def appendRow(self, row):
        if len(row) > self.colCount:
            raise Exception('Row had length of %d which is more than the expected length of %d' % (len(row), self.colCount))
        if len(row) < self.colCount:
            paddingCount = self.colCount - len(row)
            for i in range(paddingCount):
                row.append('')
        self.data.append(row)
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.data)
    
    def columnCount(self, parent=QModelIndex()):
        return self.colCount
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            i = index.row()
            j = index.column()
            
            return self.data[i][j]
        else:
            return None
            
    def fetchRow(self, rowNumber):
        return self.data[rowNumber]
    
    def headerData(self, section, orientation, role = Qt.DisplayRole):
        
        if role != Qt.DisplayRole:
            # We are being asked for something else, do the default implementation
            return QAbstractItemModel.headerData(self, section, orientation, role)
            
        if orientation == Qt.Vertical:
            return section + 1
        else:
            return self.headerNames[section]
    

class checker:
    
    def __init__(self, iface, checkID, checkName, refNumber):
        
        self.iface = iface
        self.checkID = checkID
        self.checkName = checkName
        self.refNumber = refNumber
        
        # Read the config
        self.readConfiguration()
            
        # Determine the largest number of columns requested
        maxColsRequested = 0
        headerNames = ['Site', 'Layer_name']
        for conf in self.config:
            if len(conf['columns']) > maxColsRequested:
                maxColsRequested = len(conf['columns'])
        for i in range(maxColsRequested):
            headerNames.append('Column%d' % (i+1))
        self.resModel = ResultModel(maxColsRequested + 2, headerNames)
        
    
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
                    c['db_type'] = config.get(section, 'dbType')
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
                        self.rb_new.checked = True
                    else:
                        self.rb_existing.checked = True
                        self.txt_table.setPlainText(config.get(section, 'table'))
                        self.txt_geom.setPlainText(config.get(section, 'geom_col'))
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
                            self.txtRptFile = config.get(section, 'TextRptFile')
                        except:
                            self.txtRptFile = os.path.join(xgAppsCfg['xgApps_local'], 'check.txt')
                        try:
                            self.txtFileColWidth = config.get(section, 'TextFileColumnWidth')
                        except:
                            self.txtFileColWidth = 30
                            
                            
    def display(self):
        # Only display the results if some constraints were detected
        if self.resModel.rowCount() == 0:
            QMessageBox.information(self.iface.mainWindow(), 'No constraints found', 'The query did not locate any constraints.')
            return
        crd = ConstraintResultsDialog(self.resModel)
        crd.exec_()

    
    def getDbCursor(self, dbType):
        dbConfig = self.config[1]
        if dbType == 'PostGIS':
            dbConn = psycopg2.connect( database = dbConfig['database'],
                                       user = dbConfig['user'],
                                       password = dbConfig['password'],
                                       host = dbConfig['host'],
                                       port = int(dbConfig['port']))
            dbConn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        elif dbType == 'Spatialite':
            dbConn = dbapi2.connect(dbConfig['database'])
            
        return dbConn.cursor()
        
    
    def getSqlDatabase(self):
        dbConfig = self.config[1]
        
        db = QSqlDatabase.addDatabase("QSQLServer")
        if db.isDriverAvailable('{ODBC Driver 13 for SQL Server}'):
            drv = '{ODBC Driver 13 for SQL Server}'
        elif db.isDriverAvailable('{ODBC Driver 11 for SQL Server}'):
            drv = '{ODBC Driver 11 for SQL Server}'
        elif db.isDriverAvailable('{SQL Server Native Client 11.0}'):
            drv = '{SQL Server Native Client 11.0}'
        elif db.isDriverAvailable('{SQL Server Native Client 10.0}'):
            drv = '{SQL Server Native Client 10.0}'
        else:
            QMessageBox.error(self.iface.mainWindow(), 'No SQL Server drivers', 'Could not find any SQL Server ODBC drivers.')
            return None
        
        if dbConfig['trusted'] == 'yes':
            conStr = 'DRIVER={0};SERVER={1};DATABASE={2};Trusted_Connection=yes'.format(drv, dbConfig['host'], dbConfig['database'])
        else:
            conStr = 'DRIVER={0};SERVER={1};DATABASE={2};Trusted_Connection=no;user_id={3};password={4}'.format(drv, dbConfig['host'], dbConfig['database'], dbConfig['user'], dbConfig['password'])
        db.setDatabaseName(dbConfig['database'])
        return db
        
                
    def getSiteRef(self):
        return self.siteRef
        
    def getResultCon(self):
        dbCfg = self.config[1]
        return 'Host=%(host)s;Port=%(port)s;Integrated Security=%(trusted)s;Username=%(user)s;Password=%(password)s;Database=%(database)s' % dbCfg
    
    def getResultTable(self):
        dbCfg = self.config[1]
        if dbCfg['new_table'] == 'no':
            return dbCfg['table']
        else:
            return 'tmp{0}'.format(self.refNumber)
            
    def getMapPath(self):
        return self.mapPath
    
    # Currently only works with a single selection, should work with multiple?
    def check(self, queryGeom, epsg_code, layerPath, fields):
        if self.configRead == False:
            return
        # Read XG_SYS.ini
        self.readConfiguration('XG_SYS.ini')
            
        # Reset path to map image
        self.mapPath = None
        
        # Ask whether user wishes to continue if selection not in ass_layer
    
        # Load xgcc db
        cfg = self.config[0]
        xgcc_db_path = os.path.join(os.path.join(cfg[xgApps_network],'Constraints','xgcc.sqlite'))
        with xgcc_db(xgcc_db_path) as xgcc:
            if xgcc.dbExists:
                # Get check details and check layer details
                self.checkDetails = xgcc.getCheckDetails()
                self.checkLayerDetails = xgcc.getCheckLayerDetails()
                self.advDispDetails = xgcc.getAdvDispLayerDetails()
                self.datasetDetails = xgcc.getDatasetDetails()
                
        if self.checkLayerDetails == None:
            QMessageBox.error(self.iface.mainWindow(), 'Invalid configuration', 'This constraint check has no valid searches.')
            return
        if self.advDispDetails == None:
            self.advDisp = 'F'
        
        self.rpt = []
        
        # layerPath format may be u'D:\\OneDrive\\Financial\\Drive\\Back_Westminster.TAB|layerid=0' or
        # u'dbname=\'Records\' host=localhost port=5432 sslmode=disable key=\'id\' srid=4326 type=Point table="public"."MJL_collections_v2" (geom) sql="collectioncode" LIKE \'MJL2%\''
        # so need to reformat to compare to ass_layer...
        if layerPath == self.checkDetails['ass_layer']:
            self.siteRef = fields[self.checkDetails['key_field']]
            if self.siteRef == '':
                if self.checkDetails['ass_layer_type'] == 'MapInfo TAB' or self.checkDetails['ass_layer_type'] == 'ESRI Shapefile':
                    filename = os.path.splitext(layerPath)[0]
                    self.siteRef = '{0} object'.format(filename)
                else:
                    temp = self.checkDetails['ass_layer'].split('#')
                    self.siteRef = '{0} object'.format(temp[1])
        else:
            self.siteRef = '(Unknown)'
            
        self.rpt.append['']
        self.rpt.append['{0} constraints check on {1}'.format(self.checkName, self.siteRef)]
        
        inclGridRef = False
        if self.checkDetails['GridRef'] == 'T':
            inclGridRef = True
            centroid = queryGeom.centroid().asPoint()
            gr = GridRef(centroid[0],centroid[1])
            if epsg_code == 27700:
                self.gridRef = gr.getOSGridRef(5)
            else:
                self.gridRef = gr.getGridRef()
        
        if dbType == 'SQL Server':
            sqlDb = self.getSqlDatabase()
        else:
            cur = self.getDbCursor()
            
        # Create results table if required
        dbCfg = self.config[1]
        self.dbType = dbCfg['db_type']
        if dbCfg['new_table'] == 'yes':
            self.newTable = True
            self.tableName = 'tmp{0}'.format(self.refNumber)
            self.geomCol = 'geom'
               
            if self.dbType == 'Spatialite':
                sql = 'CREATE TABLE "{0}" ("MI_PRINX" INTEGER PRIMARY KEY, "geom" BLOB, "Site" TEXT, "Layer_name" TEXT, ' + \
                      '"colum1" TEXT, "colum2" TEXT, "colum3" TEXT, "colum4" TEXT, "colum5" TEXT, "colum6" TEXT, "colum7" TEXT, ' + \
                      '"colum8" TEXT, "colum9" TEXT, "colum10" TEXT, "descCol" TEXT, "Distance" REAL, "DateCol" TEXT, "MI_STYLE" TEXT)'.format(self.tableName)
            elif self.dbType == 'PostGIS':
                sql = "CREATE TABLE {0} (mi_prinx int, geom geometry(Geometry,27700), site varchar(30), layer_name varchar(50), " + \
                      "colum1 varchar(50), colum2 varchar(50), colum3 varchar(50), colum4 varchar(50), colum5 varchar(50), colum6 varchar(50), colum7 varchar(50), " + \
                      "colum8 varchar(50), colum9 varchar(50), colum10 varchar(50), desccol varchar(254), distance decimal(10,2), datecol varchar(40)) " + \
                      "CONSTRAINT pk_{0} PRIMARY KEY (mi_prinx)".format(self.tableName.lower())
            elif self.dbType == 'SQL Server':
                sql = 'CREATE TABLE {0} (MI_PRINX int NOT NULL, geom geometry, Site varchar(30), Layer_Name varchar(50), ' + \
                      'colum1 varchar(50), colum2 varchar(50), colum3 varchar(50), colum4 varchar(50), colum5 varchar(50), colum6 varchar(50), colum7 varchar(50), ' + \
                      'colum8 varchar(50), colum9 varchar(50), colum10 varchar(50), descCol varchar(254), Distance decimal(10,2), DateCol varchar(40))' + \
                      'CONSTRAINT PK_{0} PRIMARY KEY (MI_PRINX)'.format(self.tableName)
            else:
                return
        
            try:    
                if self.dbType == 'SQL Server':
                    sqlDb.open()
                    sqlDb.exec_(sql)
                    sqlDb.close()
                else:
                    cur.execute(sql)
            except Exception as e:
                QMessageBox.error(self.iface.mainWindow(), 'No results table', 'The results table could not be created: {0}'.format(e))
                return
        else:
            self.newTable = False
            self.tableName = self.config[1]['table']
            self.geomCol = dbCfg['geom']
        
        # Variables to determine when conditional fields are displayed
        showDesc = False
        showDate = False
        showDistance = False
        
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
                            showDistance = True
                        dateField = advDisp['DateField']
                        if dateField != '':
                            includeDate = True
                            showDate = True
                    break
            
            
            # Open search layer and filter by WHERE clause if present
            try:
                layerName = "XGCC_{0}".format(layer['name'])
                whereClause = formatCondition(layer['condition'])
                if tableType == 'MapInfo TAB' or tableType == 'ESRI Shapefile' or tableType == '':
                    searchLayer = QgsVectorLayer(table, layerName, "ogr")
                    # Get WHERE clause format with "" around fields (not for MI) and \'value\' around strings
                    searchLayer.setSubsetString(whereClause)
                elif tableType == 'PostGIS':
                    # Get params from Table
                    tempCon = table.split('#')
                    uri = QgsDataSourceURI(tempCon[0])
                   
                    tempTable = tempCon[1].split['.']
                    # Set database schema, table name, geometry column and optionally subset (WHERE clause)
                    uri.setDataSource (tempTable[0], tempTable[1], tempCon[2], whereClause)
                    searchLayer = QgsVectorLayer(uri,layerName,"postgres")    
                elif tableType == 'SQL Server':
                    # Get params from Table
                    tempCon = table.split('#')
                    uri = QgsDataSourceURI('MSSQL:{0}'.format(tempCon[0]))
                        
                    tempTable = tempCon[1].split['.']
                    # Set database schema, table name, geometry column and optionally subset (WHERE clause)
                    uri.setDataSource (tempTable[0], tempTable[1], tempCon[2], whereClause)
                    searchLayer = QgsVectorLayer(uri,layerName,"mssql")    
                else:
                    return
                    
                # Check configured table is valid
                if searchLayer.dataProvider().isValid():
                    QgsMapLayerRegistry.instance().addMapLayer(searchLayer)
                else:
                    self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'The {0} layer is not valid. Continuing with next layer.'.format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10) 
                    break
                
                # Check layer has features else ignore condition
                if searchLayer.featureCount == 0:
                    if layer['condition'] != '':
                        searchLayer.setSubset(None)
                        if searchLayer.featureCount > 0:
                            self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'The {0} layer condition is not valid, condition is being ignored.'.format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10)
                        else:
                            self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'The {0} layer has no features. Continuing with next layer.'.format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10)
                            break
                    else:
                        self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'The {0} layer has no features. Continuing with next layer.'.format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10)
                        break
            except:
                self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'The {0} layer is not valid. Continuing with next layer.'.format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10) 
                break
                        
            self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    "Finding: {0}".format(layer['name']), \
                                                    level=QgsMessageBar.INFO, duration=10)
            
            # Reset ignMin if geometry is not a polygon
            if queryGeom.type() != QgsWkbTypes.GeometryType.PolygonGeometry:
                layer['ignoreMin'] = True
            
            try:
                # Buffers in CRS distance units - translate geom if not in 27700, UTM or 3857
                if layer['radius'] == 0:
                    bufferGeom = queryGeom
                elif layer['ignoreMin'] == True:
                    bufferGeom = queryGeom.buffer(layer['radius'], 12)
                else:
                    # Create doughnut if possible
                    innerGeom = queryGeom.buffer(layer['minRadius'], 12)
                    outerGeom = queryGeom.buffer(layer['radius'], 12)    
                    
                    try:
                        bufferGeom = outerGeom.difference(innerGeom)
                    except:
                        ring = QVector(innerGeom.vertexCount)
                        for vertex in innerGeom.vertices():
                            c = vertex.centroid()
                            ring.append(QgsPointXY(c[0],c[1]))
                    
                        opResult = bufferGeom.addRing(ring)

                # Insert bufferGeom into temporary layer
                bufferLayer = QgsVectorLayer("Polygon?crs=epsg:{0}".format(epsg_code),"tmpXGCC","memory")
                bufferFeat = QgsFeature()
                bufferFeat.setGeometry(bufferGeom)
                result = bufferLayer.addFeatures([bufferFeat])
                if result == False:
                     QMessageBox.error(self.iface.mainWindow(), 'Layer creation failed', 'The site could not be saved to the temp layer.')
                     return
                QgsMapLayerRegistry.instance().addMapLayer(bufferLayer)
                
                # Select where filtered layer intersects bufferGeom
                general.runalg("qgis:selectbylocation", searchLayer, bufferLayer, 0, 0)
                
                noFeatures = searchLayer.selectedFeatureCount()
                if noFeatures == 0:
                    self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'No features found in {0} layer. {1} Continuing with next layer.'.format(layer['name'], e), \
                                                    level=QgsMessageBar.INFO, duration=10) 
                    break
                
                # Get search layer geomCol
                searchUri = QgsDataSourceURI(searchLayer.dataProvider().dataSourceUri())
                searchGeomCol = searchUri.geomColumn
                
                self.rpt.append('')
                if layer['desc'] != '':
                    self.rpt.append(layer['desc'])
                else:
                    self.rpt.append(layer['name'])
                    
                # Build lists of fields / headings
                colNames = []
                colLabels = []
                noCols = 0
                fileStr = ''
                
                # Check colName1 to colName10
                for i in range[1,11]:
                    if layer['colName{0}'.format(str(i))] != '':
                        noCols+=1
                        colNames.append(layer['colName{0}'.format(str(i))])
                        if layer['colLabel{0}'.format(str(i))] != '':
                            colLabels.append(layer['colLabel{0}'.format(str(i))])
                        else:
                            colLabels.append(layer['colName{0}'.format(str(i))])
                            
                        fileStr += colLabels[noCols].ljust(self.txtFileColWidth)
                        
                if layer['descrCol'] != '':
                    inclDesc = True
                    showDesc = True
                    if layer['descrLabel'] != '':
                        descField = layer['descrLabel']
                        fileStr += layer['descrLabel'].ljust(254)
                    else:
                        descField = layer['descrCol']
                        fileStr += layer['descrCol'].ljust(254)
                else:
                    inclDesc = False
                    
                if inclDist == True:
                    fileStr += 'Distance'.ljust(15)
                    
                if inclDate == True:
                    fileStr += dateField.ljust(40)
                    
                if colNames.count() > 0:
                    self.rpt.append(fileStr)
                    
                    if self.newTable:
                        insertSQL = utils.getInsertSql('Headings', True, self.tableName, colNames.count(), includeDesc=inclDesc, includeDate=inclDate)
                        valuesSQL = utils.getValuesSql('Headings', True, colNames.count(), colLabels, includeDesc=inclDesc, 
                                                       descVal=descField, includeDate=inclDate, dateVal=dateField)
                    else:
                        utils.getInsertSql('Headings',False,self.tableName, colNames.count(), includeDesc=inclDesc, includeDate=inclDate)
                        valuesSQL = utils.getValuesSql('Headings', True, colNames.count(), colLabels, refNumber=self.refNumber, 
                                                       includeDesc=inclDesc, descVal=descField, includeDate=inclDate, dateVal=dateField)
                    try:    
                        if self.dbType == 'SQL Server':
                            sqlDb.open()
                            sqlDb.exec_(insertSQL + valuesSQL)
                            sqlDb.close()
                        else:
                            cur.execute(insertSQL + valuesSQL)
                    except Exception as e:
                        QMessageBox.error(self.iface.mainWindow(), 'Results table', 'Result heading could not be inserted into the {0} table: {1}'.format(self.tableName, e))
                        return
                
                    selFeats = searchLayer.selectedFeatures()
                    if self.checkLayerDetails['Summary']:
                        # Calculate summary
                        sumTypes = initSummaryTypeArray()
                        tempVal = []
                        
                        for i in range(colNames.count):
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
                                    tempVal[i] = None
                            else:  
                                 # TODO: if statements for each type to replace next line
                                 tempVal[i] = None
                        
                        self.rpt.append(utils.getPaddedValues('Summary', colNames.count, tempVal, self.txtFileColWidth))
                        
                        if self.newTable:
                            insertSQL = utils.getInsertSql('Summary', True, self.tableName, colNames.count(), includeGridRef=inclGridRef)
                            valuesSQL = utils.getValuesSql('Summary', True, colNames.count(), tempVal, includeGridRef=inclGridRef, gridRef=site.gridRef)
                        else:
                            utils.getInsertSql('Summary',False,self.tableName, colNames.count(), colNames.count(), includeGridRef=inclGridRef)
                            valuesSQL = utils.getValuesSql('Summary', True, colNames.count(), tempVal, refNumber=self.refNumber, 
                                                           includeGridRef=inclGridRef, gridRef=site.gridRef)
                        try:    
                            if self.dbType == 'SQL Server':
                                sqlDb.open()
                                sqlDb.exec_(insertSQL + valuesSQL)
                                sqlDb.close()
                            else:
                                cur.execute(insertSQL + valuesSQL)
                        except Exception as e:
                            QMessageBox.error(self.iface.mainWindow(), 'Results table', 'Result heading could not be inserted into the {0} table: {1}'.format(self.tableName, e))
                            return
                    else:  
                        for feat in selFeats:
                            tempVal = []
                        
                            for i in range(colNames.count()):
                                tempVal[i] = feat[colNames[i]]
                                
                            if inclDesc:
                                tempDescVal = feat[descField]
                                
                            if inclDate:
                                tempDateVal = feat[dateField]
                                
                            if inclDist:
                                # TODO Calculate distance
                                tempDistVal = -1
                                
                            self.rpt.append(utils.getPaddedValues('Record', colNames.count, tempVal, self.txtFileColWidth))
                            
                            if self.newTable:
                                insertSQL = utils.getInsertSql('Record', True, self.tableName, colNames.count(), includeGridRef=inclGridRef,
                                                               includeDesc=inclDesc, includeDate=inclDate, includeDist=inclDist)
                                valuesSQL = utils.getValuesSql('Record', True, colNames.count(), colLabels, includeGridRef=inclGridRef, gridRef=site.gridRef,
                                                               includeDesc=inclDesc, descVal=tempDescVal, includeDate=inclDate, dateVal=tempDateVal,
                                                               includeDist=inclDist, distVal=tempDistVal)
                            else:
                                utils.getInsertSql('Record',False,self.tableName, colNames.count(), colNames.count(), includeGridRef=inclGridRef,
                                                   includeDesc=inclDesc, includeDate=inclDate, includeDist=inclDist)
                                valuesSQL = utils.getValuesSql('Record', True, colNames.count(), tempVal, refNumber=self.refNumber, 
                                                               includeGridRef=inclGridRef, gridRef=site.gridRef, includeDesc=inclDesc, descVal=descField, 
                                                               includeDate=inclDate, dateVal=dateField, includeDist=inclDist, distVal=tempDistVal)
                            
                            try:    
                                if self.dbType == 'SQL Server':
                                    sqlDb.open()
                                    sqlDb.exec_(insertSQL + valuesSQL)
                                    sqlDb.close()
                                else:
                                    cur.execute(insertSQL + valuesSQL)
                            except Exception as e:
                                QMessageBox.error(self.iface.mainWindow(), 'Results table', 'Result heading could not be inserted into the {0} table: {1}'.format(self.tableName, e))
                                return
                
                # Message - Finished
                # Save self.rpt to text file
                # Export as CSV if required
                # Browse data - show results model
                
    except Exception as e:
        self.iface.messageBar().pushMessage("ESDM Constraint Checker", \
                                                    'Error during {0} layer search. {1} Continuing with next layer.'.format(layer['name'], e), \
                                                    level=QgsMessageBar.INFO, duration=10) 
        break