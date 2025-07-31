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
    if len(sys.argv) > 1:
        project_name = sys.argv[1]
    else:
        project_name = "GFM"
    window = GfmWindow(project_name, app)
    window.show()
    sys.exit(app.exec())
