"main entry point for the GFM application"

import sys

from PySide6.QtWidgets import QApplication, QWidget, QListView, QTextEdit, QHBoxLayout, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT

from ScanData import ScanData
from PlotData import PlotData
from ScanListModel import ScanListModel
from GfmWindow import GfmWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GfmWindow()
    window.show()
    sys.exit(app.exec())
