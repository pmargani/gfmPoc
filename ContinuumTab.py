"A module for the ContinuumTab Class"

from ScanData import ScanData
from OptionsTab import OptionsTab

class ContinuumTab(OptionsTab):



    """
    A class for handling all DCR data in GFM.
    """

    def __init__(
        self,
        parent,
        scanData : ScanData,
        name : str,
        scanTypes : list,
    ):
        super().__init__(parent, scanData, name, scanTypes)

        # these are the options available for continuum data
        self.labels = ["beams", "pols", "phases", "freqs"]

    def plot_data(self, scanIndex: int, optionsKeys: list):
        print("plot_data: ", scanIndex)
        self._last_scan_index = scanIndex
        x = self.scanData.getScanXDataByIndex(scanIndex)
        y_list = [self.scanData.getScanYDataByIndex(scanIndex, key) for key in optionsKeys]

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
        ax.set_title(self.scanData.getScanShortDesc(scanIndex))
        ax.set_xlabel("Time")
        ax.set_ylabel("Power")
        ax.legend()
        self.canvas.draw()