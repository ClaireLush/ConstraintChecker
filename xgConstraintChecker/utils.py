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
from qgis.core import QgsDataSourceURI

def formatCondition(condition):
    if condition == None:
        return ''
    else:
        where = []
        i = 1
        temp = condition.split(' ')
        inStrVar = False
        tmpStrVar = ''
        tmpStrDelim = ''
        for val in temp:
            if i == 1:
                # Field id
                where.append('"{0}"'.format(val))
                i+=1
            elif i == 2:
                # Comparision Operator
                where.append(val)
                i+=1
            elif i == 3:
                # Value - handle spaces in string condition
                if inStrVar == False:
                    if val[1] == '"' and val[-1] != '"':
                        inStrVar = True
                        tmpStrVar = val
                        tmpStrDelim = '"'
                        break
                    elif val[1] == "'" and val[-1] != "'":
                        inStrVar = True
                        tmpStrVar = val
                        tmpStrDelim = "'"
                        break
                    elif val[:2] == "\'" and val[-2:] != "\'":
                        inStrVar = True
                        tmpStrVar = val
                        tmpStrDelim = "\'"
                        break
                else:
                    if len(tmpStrDelim) == 1:
                        if val[-1] == tmpStrDelim:
                            inStrVar = False
                            val = ' '.join(tmpStrVar,val)
                        else:
                            tmpStrVar = ' '.join(tmpStrVar,val)
                            break
                    else:
                        if val[-2:] == "\'":
                            inStrVar = False
                            val = ' '.join(tmpStrVar,val)
                        else:
                            tmpStrVar = ' '.join(tmpStrVar,val)
                            break
                
                if '"' in val:
                    val.replace('"','\'')
                    
                if "'" in val and not '\'' in val:
                    val.replace("'",'\'')
                
                where.append(val)
                i+=1
            elif i == 4:
                # Logical Operator
                where.append(val)
                i = 1
    
        return ' '.join(where)

    
def getInsertSql(insertType, newTable, tableName, noCols, geomCol = None, 
                 inclDesc = False, inclDate = False, inclDist = False, inclGridRef = False):
    insertSQL = 'Insert Into "{0}" ('.format(tableName)
    
    if not newTable:
        insertSQL += 'ref_number,'
        
    if insertType == 'Record':
        insertSQL += '{0},'.format(geomCol)
        
    if insertType != 'Headings':
        insertSQL += 'site,'
        if inclGridRef:
            insertSQL += 'siteGR,'
    
    insertSQL += 'layer_name,'
    
    for i in range(1, noCols + 1):
        insertSQL += 'colum{0},'.format(str(i))
    
    if insertType != 'Summary':                    
        if inclDesc == True:
            insertSQL += 'desccol'
        else:
            insertSQL = insertSQL.rstrip(',')
                        
        if inclDate == True:
            insertSQL += ',datecol'
    else:
        insertSQL = insertSQL.rstrip(',')
        
    if insertType == 'Record':
        if inclDist:
            insertSQL += ',distance'
        
    insertSQL += ') '
        
    return insertSQL        


def getLayerParams(layerProvider, layerName, uriStr):
    layerParams={}
    layerParams['Provider'] = layerProvider
    
    # Freehand polygon
    if layerProvider == '':
        layerParams['Name'] = 'Freehand Polygon'
        layerParams['Path'] = ''
    else:
        layerParams['Name'] = layerName
        if layerProvider == 'Postgres':
            layerParams['Provider'] = 'Postgres'
            uri = QgsDataSourceURI(uriStr)
            if uri.username().encode('utf-8') == '':
                layerParams['Connection'] = 'Host={0};Port={1};Integrated Security=True;Username=;Password=;Database={2}'.format(
                                            uri.host().encode('utf-8'), uri.port().encode('utf-8'), uri.database().encode('utf-8'))
            else:
                layerParams['Connection'] = 'Host={0};Port={1};Integrated Security=False;Username={2};Password={3};Database={4}'.format(
                                            uri.host().encode('utf-8'), uri.port().encode('utf-8'), uri.username().encode('utf-8'), 
                                            uri.password().encode('utf-8'), uri.database().encode('utf-8'))
                                            
            layerParams['Schema'] = uri.schema().encode('utf-8')
            layerParams['Table'] = uri.table().encode('utf-8')
            layerParams['GeomCol'] = uri.geometryColumn().encode('utf-8')
            layerParams['Path'] = '{0}#{1}.{2}#{3}'.format(layerParams['Connection'], layerParams['Schema'], 
                                                           layerParams['Table'], layerParams['GeomCol'])
        elif layerProvider == 'mssql':
            uri = QgsDataSourceURI(uriStr)
            if uri.username().encode('utf-8') == '':
                layerParams['Connection'] = 'Data Source={0};Initial Catalog={1};Integrated Security=True;User ID=;Password='.format(
                                            uri.host().encode('utf-8'), uri.database().encode('utf-8'))
            else:
                layerParams['Connection'] = 'Data Source={0};Initial Catalog={1};Integrated Security=False;User ID={2};Password={3};Database={4}'.format(
                                            uri.host().encode('utf-8'), uri.database().encode('utf-8'), uri.username().encode('utf-8'), 
                                            uri.password().encode('utf-8'))
                layerParams['Schema'] = uri.schema().encode('utf-8')
                layerParams['Table'] = uri.table().encode('utf-8')
                layerParams['GeomCol'] = uri.geometryColumn().encode('utf-8')
                layerParams['Path'] = '{0}#{1}.{2}#{3}'.format(layerParams['Connection'], layerParams['Schema'], 
                                                               layerParams['Table'], layerParams['GeomCol'])
        elif layerProvider == 'ogr':
            uri = uriStr.encode('utf-8')
            layerParams['Path'] = uri.split('|')[0]
        else:
            layerParams['Path'] = ''
            
    return layerParams
    
def getPaddedValues(valueType, noCols, values, colWidth, inclDesc = False, descVal = None, 
                       inclDist = False, distVal = None, inclDate = False, dateVal = None):
    fileStr = ''
    
    for i in range(1, noCols + 1):
        fileStr += values[i].ljust(colWidth)
            
    if valueType != 'Summary':
        if inclDesc == True:
            fileStr += descVal.ljust(254)
        if inclDist == True:
            fileStr += distVal.ljust(15)
        if inclDate == True:
            fileStr += dateVal.ljust(40)
    
    return fileStr.rtrim()

    
def initSummaryTypeArray():
        # TODO: populate arrau
        return []

        
def getValuesSql(valueType, newTable, noCols, values, refNumber = None, dbType = None,
                 geomWKT = None, siteRef = None, inclGridRef = False, gridRef = None, 
                 inclDesc = False, descVal = None, inclDate = False, dateVal = None,
                 inclDist = False, distVal = None):
    valuesSQL = 'Values ('
    
    if not newTable:
        valuesSQL += '{0},'.format(str(refNumber))
    
    if valueType == 'Record':
        if dbType == 'PostGIS':
            valuesSQL += 'ST_GeomFromText(\'{0}\', 27700),'.format(geomWKT)
        elif dbType == 'SQLServer':
            valuesSQL += 'STGeomFromText(\'{0}\', 27700),'.format(geomWKT)
        elif dbType == 'Spatialite':
            valuesSQL += 'GeomFromText(\'{0}\', 27700),'.format(geomWKT)
        
    if valueType != 'Headings':
        valuesSQL += '\'{0}\','.format(siteRef)
        if inclGridRef:
            valuesSQL += '\'{0}\','.format(gridRef)
            
    for i in range(noCols):
        valuesSQL += '\'{0}\','.format(values[i])
            
    if valueType != 'Summary':
        if inclDesc == True:
            valuesSQL += '\'{0}\''.format(descVal)
        else:
            valuesSQL = valuesSQL.rstrip(',')
            
        if inclDate:
            valuesSQL += ',\'{0}\''.format(dateVal)
    else:
        valuesSQL = valuesSQL.rstrip(',') 
        
    if valueType == 'Record':
        if inclDist:
            valuesSQL += ',{0}'.format(distVal)
                           
    valuesSQL += ') '