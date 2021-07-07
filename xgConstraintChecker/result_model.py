# Import the PyQt and QGIS libraries
from qgis.PyQt.QtCore import QAbstractTableModel, QModelIndex, Qt

class ResultModel(QAbstractTableModel):
    def __init__(self, colCount, headerNames, parent=None, *args):
        QAbstractTableModel.__init__(self)
        self.colCount = colCount
        # data is a list of rows
        # each row contains the columns
        self.data = []
        self.headerNames = headerNames

    def appendColumns(self, noCols, columnNames):
        self.insertColumns(self.colCount, noCols)
        self.colCount += noCols
        for colName in columnNames:
            self.headerNames.append(colName)

    def appendRow(self, row):
        if len(row) > self.colCount:
            raise Exception('Row had length of %d which is more than the expected length of %d' % (len(row), self.colCount))
        if len(row) < self.colCount:
            paddingCount = self.colCount - len(row)
            for i in range(paddingCount):
                row.append('')
        self.data.append(row)

    def detachColumn(self, columnName):
        i = 0
        for headerName in self.headerNames:
            if headerName == columnName:
                self.removeColumn(i)
                return
            i += 1

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
            return None

        if orientation == Qt.Vertical:
            return section + 1
        else:
            return self.headerNames[section]
