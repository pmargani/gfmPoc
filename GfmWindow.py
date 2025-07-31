"module for the GFM application window"

import logging
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QListView
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QTabWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QStatusBar
from PySide6.QtWidgets import QFileDialog

from ScanData import ScanData
from ScanListModel import ScanListModel
from ContinuumTab import ContinuumTab
from PointingTab import PointingTab
from FocusTab import FocusTab
from SpectralTab import SpectralTab
from MenuBar import MenuBar

logger = logging.getLogger(__name__)

class GfmWindow(QWidget):

    """
    Main window for the GFM application.
    """

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
        # self.firstScanSelected = False # TBF: kluge to avoid displaying the first scan on startup


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

        self.gfm_tabs = [
            self.continuum_tab,
            self.pointing_tab,
            self.focus_tab,
            self.spectral_tab,
        ]

        # separate tabs and the scan list with a splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.scans_widget)
        splitter.addWidget(self.tabs)
        splitter.setSizes([200, 600])

        # Create bottom tab panel with Shell and Console tabs
        self.bottom_tabs = QTabWidget()
        self.shell_tab = QTextEdit()
        shellTxt = (
            "PySide6 does not support python console.\n"
            "I don't think this is a good idea anyway.\n"
        )
        self.shell_tab.setText(shellTxt)
        self.shell_tab.setReadOnly(True)
        self.console_tab = QTextEdit()
        self.console_tab.setReadOnly(True)
        self.console_tab.setFontFamily("Courier New")
        self.bottom_tabs.addTab(self.console_tab, "Console")
        self.bottom_tabs.addTab(self.shell_tab, "Shell")

        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setMenuBar(self.menubar)
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.bottom_tabs)

        # Add status bar at the bottom
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        main_layout.addWidget(self.status_bar)

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


    def display_scan_data(self, current, previous):
        # keep the first scan from being displayed on startup
        print("display_scan_data called", current) # self.firstScanSelected:", self.firstScanSelected)
        # if not self.firstScanSelected:  # TBF: kluge
        #     self.firstScanSelected = True
        #     return
        # get the scan type from the scanIndex
        scanIndex = current.row()
        # scanType = self.scanData.getScanDataByIndex(scanIndex)['scanType']
        scanInfo = self.scanData.getScanDataByIndex(scanIndex)
        scanType = scanInfo['scanType'] if 'scanType' in scanInfo else 'unknown'

        # update UI to indicate progress
        msg = f"Displaying scan data for scan {scanInfo['scan']} of type {scanType}"
        self.write_to_console(msg)
        status_message = f"Processing scan {scanInfo['scan']} of type {scanType}"
        self.status_bar.showMessage(status_message)


        # desc = self.scanData.getScanFullDesc(scanIndex)

        for tab in self.gfm_tabs:
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

        self.status_bar.showMessage("Ready")

    def write_to_console(self, message, level=logging.INFO, color=None):
        """
        Write a message to the console (or log).
        """
        if not hasattr(self, 'bottom_tabs'):
            return
        self.bottom_tabs.setCurrentWidget(self.console_tab)
        print(message)
        logger.log(level, message)

        # black is the default color
        if color is None:
            # color = '#00000000'
            color = '#FFFF'

        # Append the message in the specified color to the console_tab
        self.console_tab.append(f'<span style="color:{color};">{message}</span>')


    # def on_option_checkbox_changed(self):
    #     # Delegate to the tab's handler
    #     self.continuum_tab.on_option_checkbox_changed()



