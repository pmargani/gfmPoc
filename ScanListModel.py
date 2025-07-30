from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

class ScanListModel(QAbstractListModel):
    def __init__(self, scans=None):
        super().__init__()
        self.scans = scans or []

    def rowCount(self, parent=QModelIndex()):
        return len(self.scans)

    def data(self, index, role):
        if role == Qt.DisplayRole and index.isValid():
            return f"Scan {self.scans[index.row()]}"
        return None
