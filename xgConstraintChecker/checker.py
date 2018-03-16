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
from qgis.core import *

# Import custom class for reading XGCC config
from xgcc_db import xgcc_db

import pyodbc
import psycopg2
import ConfigParser
import os

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
        readConfiguration(self)
            
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
                        self.config.append(c)
                        self.configRead = True
        elif fileName == 'XG_SYS.ini':
            xgAppsCfg = self.config[0]
            configFilePath = os.path.join(xgAppsCfg['xgApps_network'], 'XG_SYS.ini')
            config.read(configFilePath)
            
            if self.configRead:
                for section in config.sections():
                    if section == 'Constraints':
                        self.advDisp = config.get(section,'AdvDisp')
                        self.exportCSV = config.get(section,'ExportCSV')
                        self.includeMap = config.get(section, 'IncludeMap')
            
    def display(self):
        # Only display the results if some constraints were detected
        if self.resModel.rowCount() == 0:
            QMessageBox.information(self.iface.mainWindow(), 'No constraints found', 'The query did not locate any constraints.')
            return
        crd = ConstraintResultsDialog(self.resModel)
        crd.exec_()

    
    def getDbConn(self, dbType):
        if dbType == 'PostGIS':
            dbConn = psycopg2.connect( database = database,
                                       user = user,
                                       password = password,
                                       host = host,
                                       port = port)
            dbConn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        return dbConn
    
    
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
            return 'tmp%s' % self.refNumber
            
    def getMapPath(self):
        return self.mapPath
    
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
                self.checkLayerDetails = xgcc.getCheckLayerDetails
                self.advDispDetails = xgcc.getAdvDispLayerDetails
                    
        if layerPath == self.checkDetails['ass_layer']:
            self.siteRef = fields[self.checkDetails['key_field']]
        else:
            self.siteRef = '(Unknown)'
        
        # Create results table if required
        self.dbType = self.config[1]['db_type']
        if self.config[1]['new_table'] == 'yes':
            self.tableName = 'tmp%s' % self.refNumber
        
            if self.dbType == 'Spatialite':
                sql = 'CREATE TABLE "%s" ("MI_PRINX" INTEGER PRIMARY KEY, "Geometry" BLOB, "Site" TEXT, "Layer_name" TEXT, "colum1" TEXT, "colum2" TEXT, "colum3" TEXT, "colum4" TEXT, "colum5" TEXT, "colum6" TEXT, "colum7" TEXT, "colum8" TEXT, "colum9" TEXT, "colum10" TEXT, "descCol" TEXT, "Distance" REAL, "DateCol" TEXT, "MI_STYLE" TEXT)
            elif self.dbType == 'PostGIS':
                
            elif self.dbType == 'SQL Server':
            
            else:
                return
        
        else:
            
        
        # Extract QKT from geometry
        wkt = queryGeom.exportToWkt()
        
        cur = self.getDbCursor()
        
        for configItem in self.config:
            if not configItem['include']:
                continue
            queryString = """SELECT """
            for col in configItem['columns']:
                queryString += '"%s"' % col.strip() + ', '
            # Remove last two chars
            queryString = queryString[:-2]
            queryString += """ FROM "%s"."%s" WHERE ST_Intersects(%s, ST_Buffer(ST_GeomFromText('%s', %d), %f))""" % (configItem['schema'], configItem['table'], configItem['geom_column'], wkt, epsg_code, configItem['buffer_distance'])
            cur.execute(queryString)
            
            # FIXME
            # msg = 'Query on %s returned %d results' % (configItem['name'], cur.rowcount)
            if cur.rowcount > 0:
                
                # Add a title row to the results
                dataRow = ['', '']
                
                # msg += ':\n\n'
                for colName in configItem['columns']:
                    dataRow.append(colName)
                    # msg += colName + '\t'
                self.resModel.appendRow(dataRow)
                for row in cur.fetchall():
                    dataRow = [self.refNumber, configItem['name']]
                    for val in row:
                        dataRow.append(str(val))
                        # msg += val + '\t'
                    self.resModel.appendRow(dataRow)
            # QMessageBox.information(self.iface.mainWindow(), 'DEBUG', msg)
