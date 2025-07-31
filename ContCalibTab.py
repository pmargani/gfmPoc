"A module for the PointingTab Class"

from PySide6.QtWidgets import QVBoxLayout, QLabel

from GfmTab import GfmTab
from ScanData import ScanData


class ContCalibTab(GfmTab):
    """
    A parent class for handling all Continuum Calibration tabs content in GFM.
    """
    def __init__(self, parent, scanData : ScanData, name : str, scanTypes : list):
        super().__init__(parent, scanData, name, scanTypes)
        layout = QVBoxLayout(self)
        self.label = QLabel(f"{self.name} tab content goes here.")
        layout.addWidget(self.label)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.polarization = 'X'  # Default polarization

        # these are the options available for continuum data
        self.labels = ["beams", "pols", "phases", "freqs"]

    def display_scan_data(self, currentScanIndex):
        # save which scan index was selected
        self.currentScanIndex = currentScanIndex
        scanIndex = currentScanIndex
        self.label.setText(f"Pointing tab: scan index {scanIndex}")
        # Get scanData from parent (GfmWindow)
        # scanData = getattr(self.parent, 'scanData', None)
        if self.scanData is None:
            self.label.setText("No scan data available.")
            return
        # Try to get Y polarization data
        try:
            scanNum = self.scanData.getScanNumByIndex(scanIndex)
            x = self.scanData.getScanXDataByIndex(scanIndex)
            # Try to find the key for Y polarization
            opts = self.scanData.getScanOptions(scanIndex, self.labels)

            pol = self.polarization
            key = self.get_key_for_y_pol(pol, opts)
            y = self.scanData.getScanYDataByIndex(scanIndex, key)
            # Plot using PlotData
            self.update_plot(x, [y], [pol], "Time", "Power", f"Scan {scanNum} - {pol} Pol")
        except Exception as e:
            self.label.setText(f"Error plotting Y pol: {e}")

    def get_key_for_y_pol(self, pol, opts):
        # Find the key for polarization (case-insensitive)
        pol_key = None
        for k in opts:
            if k.lower() == 'pols':
                pol_key = k
                break
        if pol_key is None:
            self.label.setText("No polarization data available.")
            return
        y_pols = opts[pol_key]
        # Find the value for the given polarization
        y_val = None
        for v in y_pols:
            if str(v).upper() == pol.upper():
                y_val = v
                break
        if y_val is None:
            self.label.setText(f"No {pol} polarization found.")
            return
        # Build the key tuple for Y polarization (use first values for other options)
        key = []
        for k, vals in opts.items():
            if k == pol_key:
                key.append(y_val)
            else:
                key.append(vals[0])
        return tuple(key)

    def set_polarization(self, pol):
        """
        Set the polarization for the tab.
        This method can be called to change the polarization dynamically.
        """
        if pol not in ['X', 'Y']:
            raise ValueError("Polarization must be 'X' or 'Y'.")
        self.polarization = pol
        # self.label.setText(f"Polarization set to {pol}.")
        # Optionally, you can trigger a replot or update based on the new polarization
        if self.currentScanIndex is not None:
            self.display_scan_data(self.currentScanIndex)
        # Note: currentSelection should be set to the currently selected scan in the parent widget
