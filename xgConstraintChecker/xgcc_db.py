import ConfigParser
import os
import sqlite3

from PyQt4 import QtCore

class CheckListWidgetItem(QListWidgetItem):
    def __init__(self, parent = None, checkID, checkName):
        self.checkID = checkID
        self.checkName = checkName
    
    def CheckID(self):
        return self.checkID
        
    def setCheckID(self, int):
        self.checkID = int

    def CheckName(self):
        return self.checkName
        
    def setCheckName(self, text):
        self.checkName = text
    
class xgcc_db:
    def __init__(self, xgccPath):
        self.xgccPath = xgccPath
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.xgccPath = None
    
    def dbExists(self):
        return os.path.exists(file_path)
        
    def  getCheckList(self, layerPath):
        con = sqlite3.connect(self.xgccPath)
        c = con.cursor()
        
        checkList = []
        
        checkList.append(CheckListWidgetItem(-1,'<<Checks Related To Selected Layer>>'))
        for row in c.execute('SELECT ID, [check], ass_layer FROM XG_Con WHERE ass_layer = ?', layerPath):
            checkList.append(CheckListWidgetItem(row['ID'],row['check']))
                
        checkList.append(CheckListWidgetItem(-1,'<<Checks NOT Related To Selected Layer>>'))
        for row in c.execute('SELECT ID, [check], ass_layer FROM XG_Con WHERE ass_layer <> ?', layerPath):
            checkList.append(CheckListWidgetItem(row['ID'],row['check']))
                
        con.close()
        return checkList
    
    def getCheckDetails(self, checkID):
        con = sqlite3.connect(self.xgccPath)
        c = con.cursor()
        
        c.execute('SELECT * FROM XG_Con WHERE ID = ?', checkID)
        check = c.fetchone()
        
        con.close()
        return check

    def getAdvDispLayerDetails(self, checkID):
        con = sqlite3.connect(self.xgccPath)
        c = con.cursor()
        
        c.execute('SELECT * FROM XG_ConAdvDisp WHERE ID = ?', checkID)
        if c.rowcount > 0:
            advDispLayers = c.fetchall()
        else:
            advDispLayers = None
        
        con.close()
        return advDispLayers
    
    def getCheckLayerDetails(self, checkID):
        con = sqlite3.connect(self.xgccPath)
        c = con.cursor()
        
        c.execute('SELECT * FROM XG_ConLS WHERE ID = ? ORDER BY layerSort', checkID)
        if c.rowcount > 0:
            checkLayers = c.fetchall()
        else:
            checkLayers = None
        
        con.close()
        return checkLayers
        
    
    def getDatasetDetails(self):
        con = sqlite3.connect(self.xgccPath)
        c = con.cursor()
        
        c.execute('SELECT * FROM XG_MDS')
        if c.rowcount > 0:
            datasets = c.fetchall()
        else:
            datasets = None
        
        con.close()
        return dataset
       
