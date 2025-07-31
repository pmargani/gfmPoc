"A module for the ContinuumTab Class"

import itertools

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QGroupBox, QCheckBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from PySide6.QtWidgets import QSpinBox, QLabel
from PySide6.QtWidgets import QRadioButton, QButtonGroup
import numpy as np

from ScanData import ScanData
from PlotData import PlotData
from GfmTab import GfmTab


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

        # TBF: our data doesn't have multiple integrations, faking it
        self.numIntegrations = 3
        self.integration = 0

        # TBF: we also don't have the freq data so fake this as well
        self.xUnits = "Channels"
        self.xFreqRange = (1620, 1650)  # MHz

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

        # Add a widget for selecting integration
        integration_layout = QHBoxLayout()
        integration_label = QLabel("integration")
        self.integration_spinbox = QSpinBox()
        self.integration_spinbox.setMinimum(0)
        self.integration_spinbox.setMaximum(self.numIntegrations - 1)
        self.integration_spinbox.setValue(self.integration)
        self.integration_spinbox.setSingleStep(1)
        self.integration_spinbox.valueChanged.connect(lambda val: setattr(self, "integration", val))
        self.integration_spinbox.valueChanged.connect(self.on_option_checkbox_changed)
        integration_layout.addWidget(integration_label)
        integration_layout.addWidget(self.integration_spinbox)
        self.options_layout.addLayout(integration_layout)

        # Add radio buttons for "Channels" and "Frequency" view
        view_layout = QHBoxLayout()
        view_label = QLabel("View")
        view_layout.addWidget(view_label)

        self.channels_radio = QRadioButton("Channels")
        self.frequency_radio = QRadioButton("Frequency")
        self.channels_radio.setChecked(True)

        self.view_button_group = QButtonGroup(self.options_panel)
        self.view_button_group.addButton(self.channels_radio)
        self.view_button_group.addButton(self.frequency_radio)
        self.view_button_group.buttonClicked.connect(self.on_option_checkbox_changed)

        view_layout.addWidget(self.channels_radio)
        view_layout.addWidget(self.frequency_radio)

        self.options_layout.addLayout(view_layout)

        # now add a textbox for which integration to plot
        # self.integration_text_edit = QTextEdit()
        # self.integration_text_edit.setText(str(self.integration))
        # self.integration_text_edit.setMaximumHeight(30)
        # self.options_layout.addWidget(self.integration_text_edit)
        #
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
        x_label = "Channels"

        # how we plot data depends on the view selected
        if self.frequency_radio.isChecked():
            x_label = "Frequency (MHz)"
            # TBF: kluge - we don't have freq. data in pickle file yet
            # convert x data to frequency using the xFreqRange
            x = np.asarray(x)
            # Avoid division by zero if x is all zeros
            x_max = x.max() if x.size > 0 else 1
            x = self.xFreqRange[0] + (self.xFreqRange[1] - self.xFreqRange[0]) * (x / x_max)
            y_list = [np.asarray(y)[::-1] for y in y_list]

        scanInfo = self.scanData.getScanDataByIndex(scanIndex)
        title = f"{scanInfo['project']}:{scanInfo['scan']}:{self.integration}"
        self.update_plot(x, y_list, optionsKeys, x_label, "Counts", title)





