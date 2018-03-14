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
        
        self.iface = iface
        self.xgccPath = xgccPath
    
    def dbExists(self):
        return os.path.exists(file_path)
        
    def  getCheckList(self, layerPath):
        con = sqlite3.connect(self.xgccPath)
        c = con.cursor()
        
        checkList = []
        
        checkList.append(CheckListWidgetItem(-1,'<<Checks Related To Selected Layer>>'))
        for row in c.execute('SELECT ID, [check], ass_layer FROM XG_Con WHERE ass_layer = ?', layerPath)
            checkList.append(CheckListWidgetItem(row[0],row[1]))
        #next
        
        checkList.append(CheckListWidgetItem(-1,'<<Checks NOT Related To Selected Layer>>'))
        for row in c.execute('SELECT ID, [check], ass_layer FROM XG_Con WHERE ass_layer <> ?', layerPath)
            checkList.append(CheckListWidgetItem(row[0],row[1]))
        #next
        
        con.close()
        return checkList