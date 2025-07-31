"A module for the ContinuumTab Class"

import itertools

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QGroupBox, QCheckBox
from GfmTab import GfmTab
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT

from ScanData import ScanData
from PlotData import PlotData

class SpectralTab(GfmTab):

    """
    A class for handling all VEGAS data in GFM.
    """

    def __init__(
        self,
        parent,
        scanData : ScanData,
        name : str,
        scanTypes : list,
    ):
        super().__init__(parent, scanData, name, scanTypes)

        self.options_panel = QWidget()
        self.options_layout = QVBoxLayout(self.options_panel)
        self.options_checkboxes = {}
        self.options_panel.setLayout(self.options_layout)
        plot_panel = QWidget()
        plot_layout = QVBoxLayout(plot_panel)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)
        plot_panel.setLayout(plot_layout)
        layout = QHBoxLayout(self)
        vbox = QVBoxLayout()
        vbox.addWidget(plot_panel)
        layout.addLayout(vbox)
        layout.addWidget(self.options_panel)
        self.setLayout(layout)

        # these are the options available for spectral data
        self.labels = ["beams", "pols", "phases", "IFs"]

    def display_scan_data(self, currentScanIndex):
        "Called in response to a scan selection change.  Displays the default plot"
        # save which scan index was selected
        self.currentScanIndex = currentScanIndex
        # get the scan data by index
        scan = self.scanData.getScanDataByIndex(self.currentScanIndex)
        # use the scan data to update the text edit and options panel
        print(f"Displaying scan data for: {scan['scan']}, type: {type(scan)}")
        # value = f"proj: {self.scanData.project}, scan: {scan['scan']}"  # removed text_edit
        # Clear previous options
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.options_checkboxes.clear()
        # Get scan options and create checkboxes
        opts = self.scanData.getScanOptions(self.currentScanIndex, self.labels)
        self.optionKeys = opts.keys()
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
        "Called when an option checkbox is changed.  Updates the plot based on selected options."
        # find the selected values from the checkboxes
        # labels = ["beams", "pols", "phases", "freqs"]
        labels = self.optionKeys
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
        # if any option has NO selected values, do not plot
        if any(len(selected_values[label]) == 0 for label in labels):
            return
        # turn this dict into a list of all combinations of selected values
        value_lists = [selected_values[label] for label in labels]
        key_combinations = list(itertools.product(*value_lists))
        print(f"key_combinations: {key_combinations}")
        self.plot_data(self.currentScanIndex, key_combinations)

    def plot_data(self, scanIndex : int, optionsKeys : list):
        "Uses ScanData and PlotData to create a matplotlib figure and refreshes the canvas"
        print("plot_data: ", scanIndex)
        self._last_scan_index = scanIndex
        x = self.scanData.getScanXDataByIndex(scanIndex)
        y_list = [self.scanData.getScanYDataByIndex(scanIndex, key) for key in optionsKeys]

        scanInfo = self.scanData.getScanFullDesc(scanIndex)
        title = f"{scanInfo['project']}:{scanInfo['scan']}"
        self.update_plot(x, y_list, optionsKeys, "Channels", "Counts", title)





