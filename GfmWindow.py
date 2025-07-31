"module for the GFM application window"

import sys
import itertools

from PySide6.QtWidgets import QWidget, QListView, QTextEdit, QHBoxLayout, QVBoxLayout, QSplitter, QTabWidget
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QCheckBox
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from ScanData import ScanData
from PlotData import PlotData
from ScanListModel import ScanListModel
from ContinuumTab import ContinuumTab

class GfmWindow(QWidget):
    def __init__(self, project_name : str):
        super().__init__()
        self.project_name = project_name
        self.setWindowTitle("GFM - " + self.project_name)

        # Try to size the window to about half the screen
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            width = screen_geometry.width() // 2
            height = screen_geometry.height() // 2
            left = screen_geometry.left() + (screen_geometry.width() - width) // 2
            top = screen_geometry.top() + (screen_geometry.height() - height) // 2
            self.setGeometry(left, top, width, height)
        else:
            print("Warning: Unable to determine screen geometry, using default size.")
            self.resize(1200, 400)

        # Initialize components
        fn = "projData.pkl"
        self.scanData = ScanData(fn, self.project_name)


        # --- Tabbed panel setup ---
        self.tabs = QTabWidget()

        # Initialize the scan list
        self.scans_widget = QListView()
        self.model = ScanListModel(self.scanData)
        self.scans_widget.setModel(self.model)
        self.scans_widget.selectionModel().currentChanged.connect(self.display_scan_data)
        self.firstScanSelected = False # TBF: kluge to avoid displaying the first scan on startup


        # Create the continuum tab and add it to the tab widget
        self.continuum_tab = ContinuumTab(
            parent=self,
            scanData=self.scanData,
            model=self.model
        )
        self.tabs.addTab(self.continuum_tab, "Continuum")


        # Create the pointing tab (placeholder)
        self.pointing_tab = QWidget()
        pointing_layout = QVBoxLayout(self.pointing_tab)
        self.pointing_label = QLabel("Pointing tab content goes here.")
        pointing_layout.addWidget(self.pointing_label)
        self.pointing_tab.setLayout(pointing_layout)
        self.tabs.addTab(self.pointing_tab, "Pointing")

        # Create the focus tab (placeholder)
        self.focus_tab = QWidget()
        focus_layout = QVBoxLayout(self.focus_tab)
        self.focus_label = QLabel("Focus tab content goes here.")
        focus_layout.addWidget(self.focus_label)
        self.focus_tab.setLayout(focus_layout)
        self.tabs.addTab(self.focus_tab, "Focus")

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.scans_widget)
        splitter.addWidget(self.tabs)
        splitter.setSizes([200, 600])
        layout = QHBoxLayout(self)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def display_scan_data(self, current, previous):
        # keep the first scan from being displayed on startup
        if not self.firstScanSelected:  # TBF: kluge
            self.firstScanSelected = True
            return
        # get the scan type from the scanIndex
        scanIndex = current.row()
        scanType = self.scanData.getScanDataByIndex(scanIndex)['scanType']
        continuumTypes = ['Peak', 'Focus']
        peakTypes = ['Peak']
        focusTypes = ['Focus']
        desc = self.scanData.getScanFullDesc(scanIndex)
        # Delegate scan display to the tabs
        if scanType in continuumTypes:
            self.continuum_tab.display_scan_data(current)
            self.tabs.setCurrentWidget(self.continuum_tab)
        if scanType in peakTypes:
            # self.peak_tab.display_scan_data(current, previous)
            self.pointing_label.setText(f"Peak scan type detected. {desc}")
            self.tabs.setCurrentWidget(self.pointing_tab)
        if scanType in focusTypes:
            # self.focus_tab.display_scan_data(current, previous)
            self.focus_label.setText(f"Focus scan type detected. {desc}")
            self.tabs.setCurrentWidget(self.focus_tab)
        # else:
        #     print(f"Unknown scan type: {scanType}. No action taken.")


    def on_option_checkbox_changed(self):
        # Delegate to the tab's handler
        self.continuum_tab.on_option_checkbox_changed()



