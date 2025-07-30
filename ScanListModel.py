from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from ScanData import ScanData

class ScanListModel(QAbstractListModel):
    def __init__(self, scanData : ScanData):
        super().__init__()
        self.scanData = scanData

    def rowCount(self, parent=QModelIndex()):
        return self.scanData.numScans

    def data(self, index, role):
        if role == Qt.DisplayRole and index.isValid():
            return self.scanData.getScanFullDesc(index.row())
        return None

    def getScanDataByIndex(self, index):
        return self.scanData.getScanDataByIndex(index)
