"module for the GFM application window"

import sys
import itertools

from PySide6.QtWidgets import QWidget, QListView, QTextEdit, QHBoxLayout, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QCheckBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from ScanData import ScanData
from PlotData import PlotData
from ScanListModel import ScanListModel

class GfmWindow(QWidget):
    def __init__(self, project_name : str):
        super().__init__()
        self.project_name = project_name
        self.setWindowTitle("GFM - " + self.project_name)

        # Try to size the window to about half the screen
        from PySide6.QtGui import QGuiApplication
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

        self.text_edit = QTextEdit()
        self.canvas = FigureCanvas()
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # Initialize the scan list
        # here we use a model to ensure the scans are displayed correctly
        self.scans_widget = QListView()
        self.model = ScanListModel(self.scanData)
        self.scans_widget.setModel(self.model)
        self.scans_widget.selectionModel().currentChanged.connect(self.display_scan_data)
        self.firstScanSelected = False # TBF: kluge to avoid displaying the first scan on startup

        self.options_panel = QWidget()
        self.options_layout = QVBoxLayout(self.options_panel)
        self.options_checkboxes = {}
        self.options_panel.setLayout(self.options_layout)
        plot_panel = QWidget()
        plot_layout = QVBoxLayout(plot_panel)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)
        plot_panel.setLayout(plot_layout)
        right_panel = QWidget()
        right_layout = QHBoxLayout(right_panel)
        vbox = QVBoxLayout()
        vbox.addWidget(self.text_edit)
        vbox.addWidget(plot_panel)
        right_layout.addLayout(vbox)
        right_layout.addWidget(self.options_panel)
        right_panel.setLayout(right_layout)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.scans_widget)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 600])
        layout = QHBoxLayout(self)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def display_scan_data(self, current, previous):
        # keep the first scan from being displayed on startup
        if not self.firstScanSelected:  # TBF: kluge
            self.firstScanSelected = True
            return

        # scan = self.model.data(current, Qt.DisplayRole)

        # get the scan data by index
        scan = self.model.getScanDataByIndex(current.row())

        # use the scan data to update the text edit and options panel
        print(f"Displaying scan data for: {scan}, type: {type(scan)}")
        value = f"proj: {self.project_name}, scan: {scan['scan']}"
        self.text_edit.setPlainText(value)
        # Clear previous options
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.options_checkboxes.clear()

        # Get scan options and create checkboxes
        opts = self.scanData.getScanOptions(current.row())
        for label, values in opts.items():
            group_box = QGroupBox(label)
            v_layout = QVBoxLayout()
            checkboxes = []
            for i, val in enumerate(values):
                cb = QCheckBox(str(val))
                # first checkbox is checked by default
                if i == 0:
                    cb.setChecked(True)
                v_layout.addWidget(cb)
                checkboxes.append(cb)
                cb.stateChanged.connect(self.on_option_checkbox_changed)
            group_box.setLayout(v_layout)
            self.options_layout.addWidget(group_box)
            self.options_checkboxes[label] = checkboxes

        # Trigger the checkbox change handler to update the plot
        self.on_option_checkbox_changed()

    def on_option_checkbox_changed(self):

        # find the selected values from the checkboxes
        labels = ["beams", "pols", "phases", "freqs"]
        selected_values = {}
        for label in labels:
            selected_values[label] = []
            checkboxes = self.options_checkboxes.get(label, [])
            for cb in checkboxes:
                if cb.isChecked():
                    val = cb.text()
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                    selected_values[label].append(val)
        if any(len(selected_values[label]) == 0 for label in labels):
            return
        value_lists = [selected_values[label] for label in labels]
        key_combinations = list(itertools.product(*value_lists))
        # scan = self.model.data(self.scans_widget.currentIndex(), Qt.DisplayRole)
        scanIndex = self.scans_widget.currentIndex().row()
        scan = self.model.getScanDataByIndex(scanIndex)
        print(f"key_combinations: {key_combinations}")
        self.plot_data(self.scanData.project, scanIndex, key_combinations)


    def plot_data(self, project, scanIndex : int, optionsKeys):
        opts = self.scanData.getScanOptions(scanIndex)
        plotter = PlotData(
            x=self.scanData.getScanXDataByIndex(scanIndex),
            y_list=[self.scanData.getScanYDataByIndex(scanIndex, key) for key in optionsKeys],
            labels=optionsKeys,
            xlabel="Time",
            ylabel="Power",
            title=self.scanData.getScanShortDesc(scanIndex)
        )
        fig, ax = plotter.plot()
        parent_layout = self.canvas.parentWidget().layout()
        if self.toolbar is not None:
            parent_layout.removeWidget(self.toolbar)
            self.toolbar.setParent(None)
            self.toolbar.deleteLater()
        if self.canvas is not None:
            parent_layout.removeWidget(self.canvas)
            self.canvas.setParent(None)
            self.canvas.deleteLater()
        self.canvas = FigureCanvas(fig)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        parent_layout.addWidget(self.toolbar)
        parent_layout.addWidget(self.canvas)
