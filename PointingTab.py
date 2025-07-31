"A module for the PointingTab Class"

from PySide6.QtWidgets import QVBoxLayout, QLabel
from GfmTab import GfmTab
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT

class PointingTab(GfmTab):
    """
    A class for handling all Pointing tab content in GFM.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        layout = QVBoxLayout(self)
        self.label = QLabel("Pointing tab content goes here.")
        layout.addWidget(self.label)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def display_scan_data(self, currentSelection):
        scanIndex = currentSelection.row()
        self.label.setText(f"Pointing tab: scan index {scanIndex}")
        # Get scanData from parent (GfmWindow)
        scanData = getattr(self.parent, 'scanData', None)
        if scanData is None:
            self.label.setText("No scan data available.")
            return
        # Try to get Y polarization data
        try:
            x = scanData.getScanXDataByIndex(scanIndex)
            # Try to find the key for Y polarization
            opts = scanData.getScanOptions(scanIndex)
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
            # Find the value for 'Y' or 'y'
            y_val = None
            for v in y_pols:
                if str(v).upper() == 'Y':
                    y_val = v
                    break
            if y_val is None:
                self.label.setText("No Y polarization found.")
                return
            # Build the key tuple for Y polarization (use first values for other options)
            key = []
            for k, vals in opts.items():
                if k == pol_key:
                    key.append(y_val)
                else:
                    key.append(vals[0])
            key = tuple(key)
            y = scanData.getScanYDataByIndex(scanIndex, key)
            # Plot using PlotData
            self.update_plot(x, [y], ['Y'], "Time", "Power", f"Scan {scanIndex} - Y Pol")
        except Exception as e:
            self.label.setText(f"Error plotting Y pol: {e}")


