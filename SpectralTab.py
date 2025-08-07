"A module for the ContinuumTab Class"

from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QSpinBox, QLabel
from PySide6.QtWidgets import QRadioButton, QButtonGroup
import numpy as np

from ScanData import ScanData
from OptionsTab import OptionsTab

class SpectralTab(OptionsTab):

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

        # these are the options available for spectral data
        self.labels = ["beams", "pols", "phases", "IFs"]

        # TBF: our data doesn't have multiple integrations, faking it
        self.numIntegrations = 3
        self.integration = 0

        # TBF: we also don't have the freq data so fake this as well
        self.xUnits = "Channels"
        self.xFreqRange = (1620, 1650)  # MHz


    def add_additional_options(self):
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

        # In-place refresh: clear only the axes, not the figure
        if self.canvas and hasattr(self.canvas, "figure"):
            fig = self.canvas.figure
            if fig.axes:
                ax = fig.axes[0]
                ax.clear()
            else:
                ax = fig.add_subplot(111)
        else:
            from matplotlib.figure import Figure
            fig = Figure(figsize=(4, 3))
            ax = fig.add_subplot(111)
            self.canvas.figure = fig

        # Plot the new data
        for y, label in zip(y_list, optionsKeys):
            ax.plot(x, y, label=str(label))
        scanInfo = self.scanData.getScanDataByIndex(scanIndex)
        title = f"{scanInfo['project']}:{scanInfo['scan']}:{self.integration}"
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel("Counts")
        ax.legend()
        # Print 'source' in the upper right hand corner of the plot
        ax.text(0.98, 0.98, "source", transform=ax.transAxes,
                fontsize=12, color="black", ha="right", va="top")
        self.canvas.draw()

        # Get the colors used for each line in the plot
        colors_used = []
        if self.canvas and hasattr(self.canvas, "figure"):
            for ax in self.canvas.figure.axes:
                for line in ax.get_lines():
                    colors_used.append(line.get_color())
        self.write_spectra_to_console(optionsKeys, colors_used)

    def write_spectra_to_console(self, optionsKeys, colors):
        """
        For each spectra, write color coded details to console.
        This should be like an ASCII table of spectra info.
        """
        self.write_to_console(f"Spectra for scan {self.scanData.getScanNumByIndex(self.currentScanIndex)}:")
        col_width = 12  # You can adjust this width as needed
        header = "|"
        header += " | ".join(label.ljust(col_width) for label in self.labels)
        header += "|"
        self.write_to_console(f"  {header}")
        for key, color in zip(optionsKeys, colors):
            # print("key: ", key)
            line = "|"
            line += " | ".join(str(part).ljust(col_width) for part in key)
            line += " |"
            self.write_to_console(f"  {line}", color=color)





