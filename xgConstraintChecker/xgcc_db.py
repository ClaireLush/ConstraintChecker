import os
import sqlite3

class CheckListItem:
    def __init__(self, checkID, checkName):
        self.checkID = checkID
        self.checkName = checkName

    def CheckID(self):
        return self.checkID

    def setCheckID(self, check_id):
        self.checkID = check_id

    def CheckName(self):
        return self.checkName

    def setCheckName(self, text):
        self.checkName = text

class XgCCDb:
    def __init__(self, xgccPath):
        self.xgccPath = xgccPath

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.xgccPath = None

    def dbExists(self):
        return os.path.exists(self.xgccPath)

    def  getCheckList(self, layerPath):
        con = sqlite3.connect(self.xgccPath)
        con.row_factory = sqlite3.Row
        c = con.cursor()

        checkList = []

        checkList.append(CheckListItem(-1,'<<Checks Related To Selected Layer>>'))
        try:
            for row in c.execute('SELECT ID, [check], ass_layer FROM XG_Con WHERE ass_layer = ?', (layerPath,)):
                checkList.append(CheckListItem(row['ID'],row['check']))
        except:
            pass

        checkList.append(CheckListItem(-1,'<<Checks NOT Related To Selected Layer>>'))
        try:
            for row in c.execute('SELECT ID, [check], ass_layer FROM XG_Con WHERE ass_layer <> ?', (layerPath,)):
                checkList.append(CheckListItem(row['ID'],row['check']))
        except:
            pass

        con.close()
        return checkList

    def getCheckDetails(self, checkID):
        con = sqlite3.connect(self.xgccPath)
        con.row_factory = sqlite3.Row
        c = con.cursor()

        c.execute('SELECT * FROM XG_Con WHERE ID = ?', (checkID,))
        check = c.fetchone()

        con.close()
        return check

    def getAdvDispLayerDetails(self, checkID):
        con = sqlite3.connect(self.xgccPath)
        con.row_factory = sqlite3.Row
        c = con.cursor()

        c.execute('SELECT * FROM XG_ConAdvDisp WHERE ID = ?', (checkID,))
        advDispLayers = c.fetchall()

        con.close()
        return advDispLayers

    def getCheckLayerDetails(self, checkID):
        con = sqlite3.connect(self.xgccPath)
        con.row_factory = sqlite3.Row
        c = con.cursor()

        c.execute('SELECT * FROM XG_ConLS WHERE ID = ? ORDER BY layerSort', (checkID,))
        checkLayers = c.fetchall()

        con.close()
        return checkLayers

    def getDatasetDetails(self):
        con = sqlite3.connect(self.xgccPath)
        con.row_factory = sqlite3.Row
        c = con.cursor()

        c.execute('SELECT * FROM XG_MDS')
        datasets = c.fetchall()

        con.close()
        return datasets
