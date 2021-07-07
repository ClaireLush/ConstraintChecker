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
from qgis.core import QgsDataSourceUri, QgsWkbTypes

summary_types = []

def countAll(layer):
    count = 0
    for feat in layer.getFeatures():
        count += 1
    return count

def countByGeomType(layer, selected, geomType):
    count = 0
    layerGeomType = layer.geometryType()
    if geomType is not None and layerGeomType != geomType:
        return 0

    if selected:
        if geomType is None:
            count += 1
        else:
            for feat in layer.getSelectedFeatures():
                if feat.geometry().type() == geomType:
                    count += 1
    else:
        if geomType is None:
            count += 1
        else:
            for feat in layer.getFeatures():
                if feat.geometry().type() == geomType:
                    count += 1
    return count

def countNodesByGeomType(layer, selected, geomType=None):
    layerGeomType = layer.geometryType()
    count = 0
    if geomType is not None and layerGeomType != geomType:
        return 0

    if selected:
        for feat in layer.getSelectedFeatures():
            nodes = list(feat.geometry().vertices())
            if geomType is None:
                count += len(nodes)
            else:
                if feat.geometry().type() == geomType:
                    if geomType == QgsWkbTypes.PolygonGeometry:
                        count += len(nodes)-1
                    else:
                        count += len(nodes)
    else:
        for feat in layer.getFeatures():
            nodes = list(feat.geometry().vertices())
            if geomType is None:
                count += len(nodes)
            else:
                if feat.geometry().type() == geomType:
                    if geomType == QgsWkbTypes.PolygonGeometry:
                        count += len(nodes)-1
                    else:
                        count += len(nodes)
    return count

def formatCondition(condition):
    if condition is None:
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
                # Comparison Operator
                where.append(val)
                i+=1
            elif i == 3:
                # Value - handle spaces in string condition
                if not inStrVar:
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
                            val = ' '.join([tmpStrVar, val])
                        else:
                            tmpStrVar = ' '.join([tmpStrVar, val])
                            break
                    else:
                        if val[-2:] == "\'":
                            inStrVar = False
                            val = ' '.join([tmpStrVar, val])
                        else:
                            tmpStrVar = ' '.join([tmpStrVar, val])
                            break

                if '"' in val:
                    val.replace('"','\'')

                if "'" in val and '\'' not in val:
                    val.replace("'",'\'')

                where.append(val)
                i+=1
            elif i == 4:
                # Logical Operator
                where.append(val)
                i = 1

        return ' '.join(where)


def getDelimitedValues(valueType, delimiter, noCols, values, layerName = None, siteRef = None, \
                       inclGridRef = False, gridRef = None, inclDesc = False, descVal = None, \
                       inclDist = False, distVal = None, inclDate = False, dateVal = None):
    fileStr = ''

    if valueType != 'Headings':
        fileStr += ('"{0}"{1}'.format(siteRef,delimiter))
        if inclGridRef:
            fileStr += ('"{0}"{1}'.format(gridRef,delimiter))
        else:
            fileStr += delimiter
        fileStr += '"{0}"{1}'.format(layerName,delimiter)
    else:
        fileStr += ('{0}{0}{0}'.format(delimiter))

    for i in range(noCols):
        if values[i] is None:
            fileStr += delimiter
        else:
            fileStr += ('"{0}"{1}'.format(values[i],delimiter))

    for i in range(10-noCols):
        fileStr += delimiter

    if valueType == 'Summary':
        fileStr += ('{0}{0}{0}'.format(delimiter))
    else:
        if inclDesc:
            fileStr += ('"{0}"{1}'.format(descVal,delimiter))
        else:
            fileStr += delimiter

        if valueType != 'Headings':
            if inclDist:
                fileStr += ('"{0}"{1}'.format(distVal,delimiter))
            else:
                fileStr += delimiter
        else:
            fileStr += delimiter

        if inclDate:
            fileStr += ('"{0}"{1}'.format(dateVal,delimiter))
        else:
            fileStr += delimiter

    return fileStr[:-1]


def getInsertSql(insertType, newTable, tableName, noCols, geomCol = None, \
                 inclDesc = False, inclDate = False, inclDist = False, inclGridRef = False):
    insertSQL = 'Insert Into {0} ('.format(tableName)

    if not newTable:
        insertSQL += 'ref_number,'

    if insertType == 'Record':
        insertSQL += '{0},'.format(geomCol)

    if insertType != 'Headings':
        insertSQL += 'site,'
        if inclGridRef:
            insertSQL += 'sitegr,'
        insertSQL += 'layer_name,'

    for i in range(1, noCols + 1):
        insertSQL += 'colum{0},'.format(str(i))

    if insertType != 'Summary':
        if inclDesc:
            insertSQL += 'desccol'
        else:
            insertSQL = insertSQL.rstrip(',')

        if inclDate:
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
    if layerProvider is None:
        layerParams['Name'] = 'Freehand Polygon'
        layerParams['Path'] = ''
    else:
        layerParams['Name'] = layerName
        if layerProvider == 'Postgres':
            layerParams['Provider'] = 'Postgres'
            uri = QgsDataSourceUri(uriStr)
            if uri.username().encode('utf-8') == '':
                layerParams['Connection'] = 'Host={0};Port={1} Integrated Security=True;Database={2}'.format(
                                            uri.host().encode('utf-8'), uri.port().encode('utf-8'), uri.database().encode('utf-8'))
            else:
                layerParams['Connection'] = 'Host={0};Port={1};Integrated Security=False;Username={2};Password={3};Database={4}'.format(
                                            uri.host().encode('utf-8'), uri.port().encode('utf-8'), uri.username().encode('utf-8'),
                                            uri.password().encode('utf-8'), uri.database().encode('utf-8'))

            layerParams['Schema'] = uri.schema().encode('utf-8')
            layerParams['Table'] = uri.table().encode('utf-8')
            layerParams['GeomCol'] = uri.geometryColumn().encode('utf-8')
            layerParams['Path'] = '{0}#{1}.{2}#{3}'.format(layerParams['Connection'], layerParams['Schema'], \
                                                           layerParams['Table'], layerParams['GeomCol'])
        elif layerProvider == 'mssql':
            uri = QgsDataSourceUri(uriStr)
            if uri.username().encode('utf-8') == '':
                layerParams['Connection'] = 'Data Source={0};Initial Catalog={1};Integrated Security=True;'.format(
                                            uri.host().encode('utf-8'), uri.database().encode('utf-8'))
            else:
                layerParams['Connection'] = 'Data Source={0};Initial Catalog={1};Integrated Security=False;User ID={2};Password={3}'.format(
                                            uri.host().encode('utf-8'), uri.database().encode('utf-8'), uri.username().encode('utf-8'),
                                            uri.password().encode('utf-8'))
                layerParams['Schema'] = uri.schema().encode('utf-8')
                layerParams['Table'] = uri.table().encode('utf-8')
                layerParams['GeomCol'] = uri.geometryColumn().encode('utf-8')
                layerParams['Path'] = '{0}#{1}.{2}#{3}'.format(layerParams['Connection'], layerParams['Schema'],
                                                               layerParams['Table'], layerParams['GeomCol'])
        elif layerProvider == 'ogr':
            layerParams['Path'] = uriStr.split('|')[0]
        else:
            layerParams['Path'] = ''

    return layerParams

def getPaddedValues(valueType, noCols, values, colWidth, inclDesc = False, descVal = None,
                       inclDist = False, distVal = None, inclDate = False, dateVal = None):
    fileStr = ''

    for i in range(noCols):
        if values[i] is None:
            fileStr += ' '.ljust(colWidth)
        else:
            fileStr += str(values[i]).ljust(colWidth)

    if valueType != 'Summary':
        if inclDesc:
            fileStr += str(descVal).ljust(254)
        if inclDist:
            fileStr += str(distVal).ljust(15)
        if inclDate:
            fileStr += str(dateVal).ljust(40)

    return fileStr.rstrip()

def getSummaryValues(layer, colNames):
    tempVal = []
    for colName in colNames:
        if colName in summary_types:
            if colName == 'CountAny':
                tempVal.append(layer.selectedFeatureCount())
            elif colName == 'CountPoint':
                tempVal.append(countByGeomType(layer, True, QgsWkbTypes.PointGeometry()))
            elif colName == 'CountLine':
                tempVal.append(countByGeomType(layer, True, QgsWkbTypes.LineGeometry()))
            elif colName == 'CountPolygon':
                tempVal.append(countByGeomType(layer, True, QgsWkbTypes.PolygonGeometry()))
            elif colName == 'CountAllAny':
                tempVal.append(countByGeomType(layer, False, None))
            elif colName == 'CountAllPoint':
                tempVal.append(countByGeomType(layer, False, QgsWkbTypes.PointGeometry()))
            elif colName == 'CountAllLine':
                tempVal.append(countByGeomType(layer, False, QgsWkbTypes.LineGeometry()))
            elif colName == 'CountAllPolygon':
                tempVal.append(countByGeomType(layer, False, QgsWkbTypes.PolygonGeometry()))
            elif colName == 'NodesAll':
                tempVal.append(countNodesByGeomType(layer, True, None))
            elif colName == 'CountAllLine':
                tempVal.append(countNodesByGeomType(layer, True, QgsWkbTypes.LineGeometry()))
            elif colName == 'CountAllPolygon':
                tempVal.append(countNodesByGeomType(layer, True, QgsWkbTypes.PolygonGeometry()))
            elif colName == 'PercentInAny':
                percent = (layer.selectedFeatureCount() / countByGeomType(layer, False, None)) * 100
                tempVal.append(round(percent, 2))
            elif colName == 'PercentInPoint':
                percent = (countByGeomType(layer, True, QgsWkbTypes.PointGeometry()) / countByGeomType(layer, False, QgsWkbTypes.PointGeometry())) * 100
                tempVal.append(round(percent, 2))
            elif colName == 'PercentInLine':
                percent = (countByGeomType(layer, True, QgsWkbTypes.LineGeometry()) / countByGeomType(layer, False, QgsWkbTypes.LineGeometry())) * 100
                tempVal.append(round(percent, 2))
            elif colName == 'PercentInPolygon':
                percent = (countByGeomType(layer, True, QgsWkbTypes.PolygonGeometry()) / countByGeomType(layer, False, QgsWkbTypes.PolygonGeometry())) * 100
                tempVal.append(round(percent, 2))
            elif colName == 'PercentNodeInAny':
                percent = (countNodesByGeomType(layer, True, None) / countNodesByGeomType(layer, False, None)) * 100
                tempVal.append(round(percent, 2))
            elif colName == 'PercentNodeInLine':
                percent = (countNodesByGeomType(layer, True, QgsWkbTypes.LineGeometry()) / countNodesByGeomType(layer, False, QgsWkbTypes.LineGeometry())) * 100
                tempVal.append(round(percent, 2))
            elif colName == 'PercentNodeInPolygon':
                percent = (countNodesByGeomType(layer, True, QgsWkbTypes.PolygonGeometry()) / countNodesByGeomType(layer, False, QgsWkbTypes.PolygonGeometry())) * 100
                tempVal.append(round(percent, 2))
            elif colName == 'LineLength':
                length = 0
                for feat in layer.getSelectedFeatures():
                    if feat.geometry().type() == QgsWkbTypes.LineGeometry:
                        length += feat.geometry().length()
                tempVal.append(length)
            elif colName == 'AreaPolygon':
                area = 0
                for feat in layer.getSelectedFeatures():
                    if feat.geometry().type() == QgsWkbTypes.PolygonGeometry:
                        area += feat.geometry().area()
                tempVal.append(area)
            elif colName == 'PercentLengthLine':
                lengthIn = lengthTotal = 0
                for feat in layer.getSelectedFeatures():
                    if feat.geometry().type() == QgsWkbTypes.LineGeometry:
                        lengthIn += feat.geometry().length()
                for feat in layer.getSelectedFeatures():
                    if feat.geometry().type() == QgsWkbTypes.LineGeometry:
                        lengthTotal += feat.geometry().length()
                percent = (lengthIn / lengthTotal) * 100
                tempVal.append(round(percent,2))
            elif colName == 'PercentAreaPolygon':
                areaIn = areaTotal = 0
                for feat in layer.getSelectedFeatures():
                    if feat.geometry().type() == QgsWkbTypes.PolygonGeometry:
                        areaIn += feat.geometry().area()
                for feat in layer.getFeatures():
                    if feat.geometry().type() == QgsWkbTypes.PolygonGeometry:
                        areaTotal += feat.geometry().area()
                percent = (areaIn / areaTotal) * 100
                tempVal.append(round(percent,2))
            else:
                tempVal.append('')
        else:
            # Sum the field
            try:
                val = 0
                for feat in layer.getSelectedFeatures():
                    val += feat[colName]
                tempVal.append(val)
            except:
                tempVal.append('')

    print(tempVal)
    return tempVal

def getValues(valueType, noCols, values, layerName = None, siteRef = None,
              inclGridRef = False, gridRef = None, inclDesc = False, descVal = None,
              inclDate = False, dateVal = None, inclDist = False, distVal = None):
    if valueType != 'Headings':
        dataRow = []
        dataRow.append(siteRef)
        if inclGridRef:
            dataRow.append(gridRef)
        else:
            dataRow.append('')
        dataRow.append(layerName)
    else:
        dataRow = ['', '', '']

    for i in range(noCols):
        dataRow.append(values[i])

    if valueType != 'Summary':
        if inclDesc:
            dataRow.append(descVal)
        else:
            dataRow.append('')

        if valueType != 'Headings':
            if inclDist:
                dataRow.append(distVal)
            else:
                dataRow.append('')
        else:
            dataRow.append('')

        if inclDate:
            dataRow.append(dateVal)
        else:
            dataRow.append('')

    return dataRow

def getValuesSql(valueType, newTable, noCols, values, layerName = None, refNumber = None, dbType = None,
                 geomWKT = None, siteRef = None, inclGridRef = False, gridRef = None,
                 inclDesc = False, descVal = None, inclDate = False, dateVal = None,
                 inclDist = False, distVal = None):
    valuesSQL = 'Values ('

    if not newTable:
        valuesSQL += '{0},'.format(str(refNumber))

    if valueType == 'Record':
        if dbType == 'PostGIS':
            valuesSQL += 'ST_GeomFromText(\'{0}\', 27700),'.format(geomWKT)
        elif dbType == 'SQL Server':
            valuesSQL += 'geometry::STGeomFromText(\'{0}\', 27700),'.format(geomWKT)
        elif dbType == 'Spatialite':
            valuesSQL += 'GeomFromText(\'{0}\', 27700),'.format(geomWKT)

    if valueType != 'Headings':
        valuesSQL += '\'{0}\','.format(siteRef)
        if inclGridRef:
            valuesSQL += '\'{0}\','.format(gridRef)
        valuesSQL += '\'{0}\','.format(layerName)

    for i in range(noCols):
        valuesSQL += '\'{0}\','.format(values[i])

    if valueType != 'Summary':
        if inclDesc:
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

    return valuesSQL

def initSummaryTypeArray():
    summary_types.clear()
    summary_types.append('CountAny')
    summary_types.append('CountPoint')
    summary_types.append('CountLine')
    summary_types.append('CountPolygon')
    summary_types.append('CountAllAny')
    summary_types.append('CountAllPoint')
    summary_types.append('CountAllLine')
    summary_types.append('CountAllPolygon')
    summary_types.append('NodesAll')
    summary_types.append('NodesLine')
    summary_types.append('NodesPolygon')
    summary_types.append('PercentInAny')
    summary_types.append('PercentInPoint')
    summary_types.append('PercentInLine')
    summary_types.append('PercentInPolygon')
    summary_types.append('PercentNodeInAny')
    summary_types.append('PercentNodeInLine')
    summary_types.append('PercentNodeInPolygon')
    summary_types.append('LengthLine')
    summary_types.append('AreaPolygon')
    summary_types.append('PercentLengthLine')
    summary_types.append('PercentAreaPolygon')
