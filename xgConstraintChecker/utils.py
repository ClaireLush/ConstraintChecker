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

def formatCondition(self, condition):
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
    
def getInsertSql(self, insertType, newTable, tableName, noCols, geomCol = None, 
                 includeDesc = False, includeDate = False, includeDist = False, 
                 includeGridRef = False):
    insertSQL = 'Insert Into "{0}" ('.format(tableName)
    
    if not newTable:
        insertSQL += 'ref_number,'
        
    if insertType == 'Record':
        insertSQL += '{0},'.format(geomCol)
        
    if insertType != 'Headings':
        insertSQL += 'site,'
        if includeGridRef:
            insertSQL += 'siteGR,'
    
    insertSQL += 'layer_name,'
    
    for i in range(1, noCols + 1):
        insertSQL += 'colum{0},'.format(str(i))
    
    if insertType != 'Summary':                    
        if includeDesc == True:
            insertSQL += 'desccol'
        else:
            insertSQL = insertSQL.rstrip(',')
                        
        if includeDate == True:
            insertSQL += ',datecol'
    else:
        insertSQL = insertSQL.rstrip(',')
        
    if insertType == 'Record':
        if includeDist:
            insertSQL += ',distance'
                        
    insertSQL += ') '
        
    return insertSQL        
    
    
def getValuesSql(self, valueType, newTable, noCols, values, refNumber = None, 
                 geomWKT = None, siteRef = None, includeGridRef = False, gridRef = None, 
                 includeDesc = False, descVal = None, includeDate = False, dateVal = None,
                 includeDist = False, distVal = None):
    valuesSQL = 'Values ('
    
    if not newTable:
        valuesSQL += '{0},'.format(str(refNumber))
    
    if valueType == 'Record':
        valuesSQL += '\'{0}\','.format(geomWKT)
        
    if valueType != 'Headings':
        valuesSQL += '\'{0}\','.format(siteRef)
        if includeGridRef:
            valuesSQL += '\'{0}\','.format(gridRef)
            
    for i in range(noCols):
        valuesSQL += '\'{0}\','.format(values[i])
            
    if valueType != 'Summary':
        if includeDesc == True:
            valuesSQL += '\'{0}\''.format(descVal)
        else:
            valuesSQL = valuesSQL.rstrip(',')
            
        if includeDate:
            valuesSQL += ',\'{0}\''.format(dateVal)
    else:
        valuesSQL = valuesSQL.rstrip(',') 
        
    if valueType == 'Record':
        if includeDist:
            valuesSQL += ',{0}'.format(distVal)
                           
                        
    valuesSQL += ') '
    
def getNoNodes(self, features):
    # TODO Implement method
    return -1
    
def getPaddedValues(self, valueType, noCols, values, colWidth, includeDesc = False, descVal = None, 
                       includeDist = False, distVal, includeDate = False, dateVal = None):
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
    
def initSummaryTypeArray(self):
        # TODO: populate arrau
        return []