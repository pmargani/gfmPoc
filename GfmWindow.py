"module for the GFM application window"

import logging

from email.mime import message
import sys
import itertools

from PySide6.QtWidgets import QWidget, QListView, QTextEdit, QHBoxLayout, QVBoxLayout, QSplitter, QTabWidget
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QCheckBox
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtWidgets import QTextEdit

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT

from ScanData import ScanData
from PlotData import PlotData
from ScanListModel import ScanListModel
from ContinuumTab import ContinuumTab
from PointingTab import PointingTab
from FocusTab import FocusTab
from SpectralTab import SpectralTab
from MenuBar import MenuBar
from PySide6.QtWidgets import QFileDialog

logger = logging.getLogger(__name__)

class GfmWindow(QWidget):
    def __init__(self, project_name : str, app):
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
        fn = "projData3.pkl"
        self.scanData = ScanData(fn, self.project_name)

        self.menubar = MenuBar(self, app, self.open_project)

        # --- Tabbed panel setup ---
        self.tabs = QTabWidget()

        # Initialize the scan list
        self.scans_widget = QListView()
        self.model = ScanListModel(self.scanData)
        self.scans_widget.setModel(self.model)
        self.scans_widget.selectionModel().currentChanged.connect(self.display_scan_data)
        self.firstScanSelected = False # TBF: kluge to avoid displaying the first scan on startup


        # *** create tabs:

        # Create the continuum tab and add it to the tab widget
        self.continuum_tab = ContinuumTab(
            self,
            self.scanData,
            "Continuum",
            ["Peak", "Focus"],
        )
        self.tabs.addTab(self.continuum_tab, "Continuum")


        # Create the pointing tab (now a class)
        self.pointing_tab = PointingTab(
            self,
            self.scanData,
            "Pointing",
            ["Peak"],
        )
        self.tabs.addTab(self.pointing_tab, "Pointing")

        # Create the focus tab (placeholder)
        self.focus_tab = FocusTab(
            self,
            self.scanData,
            "Focus",
            ["Focus"],
        )
        self.tabs.addTab(self.focus_tab, "Focus")

        self.spectral_tab = SpectralTab(
            self,
            self.scanData,
            "Spectral",
            ["spectral"],
        )
        self.tabs.addTab(self.spectral_tab, "Spectral")

        # separate tabs and the scan list with a splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.scans_widget)
        splitter.addWidget(self.tabs)
        splitter.setSizes([200, 600])

        # Create bottom tab panel with Shell and Console tabs
        self.bottom_tabs = QTabWidget()
        self.shell_tab = QTextEdit()
        shellTxt = "PySide6 does not support python console.\nI don't think this is a good idea anyway.\n"
        self.shell_tab.setText(shellTxt)
        self.shell_tab.setReadOnly(True)
        self.console_tab = QTextEdit()
        self.console_tab.setReadOnly(True)
        self.bottom_tabs.addTab(self.console_tab, "Console")
        self.bottom_tabs.addTab(self.shell_tab, "Shell")

        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setMenuBar(self.menubar)
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.bottom_tabs)
        self.setLayout(main_layout)

    def open_project(self):
        # Logic to open a project
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project Data File",
            "",
            "Pickle Files (*.pkl);;All Files (*)"
        )
        if file_name:
            self.scanData = ScanData(file_name, self.project_name)
            self.model = ScanListModel(self.scanData)
            self.scans_widget.setModel(self.model)
            self.firstScanSelected = False
        pass

    def display_scan_data(self, current, previous):
        # keep the first scan from being displayed on startup
        if not self.firstScanSelected:  # TBF: kluge
            self.firstScanSelected = True
            return
        # get the scan type from the scanIndex
        scanIndex = current.row()
        # scanType = self.scanData.getScanDataByIndex(scanIndex)['scanType']
        scanInfo = self.scanData.getScanDataByIndex(scanIndex)
        scanType = scanInfo['scanType'] if 'scanType' in scanInfo else 'unknown'
        self.write_to_console(f"Displaying scan data for scan {scanInfo['scan']} of type {scanType}")
        tabs = [
            self.continuum_tab,
            self.pointing_tab,
            self.focus_tab,
            self.spectral_tab,
        ]
        # desc = self.scanData.getScanFullDesc(scanIndex)

        for tab in tabs:
            idx = self.tabs.indexOf(tab)
            if scanType in tab.scanTypes:
                if hasattr(tab, 'display_scan_data'):
                    tab.display_scan_data(current.row())
                self.tabs.setCurrentWidget(tab)
                self.tabs.tabBar().setTabTextColor(idx, Qt.blue)
                # self.tabs.setTabText(idx, f"<b>{label}</b>")
            else:
                # reset txt to normal
                self.tabs.tabBar().setTabTextColor(idx, Qt.black)
                # self.tabs.setTabText(idx, f"{label}")

    def write_to_console(self, message, level=logging.INFO):
        """
        Write a message to the console (or log).
        """
        if not hasattr(self, 'bottom_tabs'):
            return
        self.bottom_tabs.setCurrentWidget(self.console_tab)
        print(message)
        logger.log(level, message)
        self.console_tab.append(message)


    def on_option_checkbox_changed(self):
        # Delegate to the tab's handler
        self.continuum_tab.on_option_checkbox_changed()



