"A module for the PointingTab Class, child of ContCalibTab."

from ContCalibTab import ContCalibTab
from PlotData import PlotData
from ScanData import ScanData
import re

class PointingTab(ContCalibTab):
    """
    A class for handling all Pointing tab content in GFM.
    """
    def __init__(self, parent, scanData: ScanData, name: str, scanTypes: list):
        super().__init__(parent, scanData, name, scanTypes)
        self.plot_history = []  # Store history of plot figures
        # You can add more Pointing-specific initialization here if needed

        self.peakScanIndex = None  # Initialize peak scan index

    def display_scan_data(self, currentScanIndex):
        "For pointing scans, we want to display the scans in a 2x2 grid."

        scanInfo = self.scanData.getScanDataByIndex(currentScanIndex)
        desc = scanInfo.get("description", None)
        desc = desc[5:] # remove "Peak "
        print(f"Displaying Pointing scan data: {desc}")
        match = re.search(r'\((\d+) of (\d+)\)', desc if desc else "")
        if match:
            n = int(match.group(1))
            m = int(match.group(2))
            print(f"Found pattern '(N of M)': N={n}, M={m}")
            self.peakScanIndex = n - 1
        else:
            self.peakScanIndex = None

        # Always create a 2x2 grid of plots
        fig = self.canvas.figure
        fig.clear()
        axes = [fig.add_subplot(2, 2, i+1) for i in range(4)]

        if len(self.plot_history) >= 4:
            # start over
            self.plot_history = []


        # Plot previous scans from history in their quadrants
        for idx, plot_data in self.plot_history:
            if plot_data is None or idx is None or not (0 <= idx < 4):
                continue
            try:
                # Assume plot_data is a tuple (scanNum, x, y, pol, key, desc) or a figure
                # If it's a figure, skip (we want raw data)
                if isinstance(plot_data, dict):
                    print("history plot data found", plot_data)
                    ax = axes[idx]

                    pol = plot_data['pol']
                    scanNum = plot_data['scanNum']
                    title = f"Scan {scanNum} - {pol} Pol"
                    label = f"{pol}"
                    p = PlotData(
                        plot_data["x"],
                        [plot_data["y"]],
                        labels=[label],
                        xlabel="Time",
                        ylabel="Power",
                        title=title
                    )
                    p.plot(ax=ax)
            except Exception as e:
                print(f"Error plotting history scan in quadrant {idx}: {e}")

        # Plot the current scan in the correct quadrant
        try:
            scanNum = self.scanData.getScanNumByIndex(currentScanIndex)
            x = self.scanData.getScanXDataByIndex(currentScanIndex)
            opts = self.scanData.getScanOptions(currentScanIndex, self.labels)
            pol = self.polarization
            key = self.get_key_for_pol(pol, opts)
            y = self.scanData.getScanYDataByIndex(currentScanIndex, key)
            idx = self.peakScanIndex if self.peakScanIndex is not None and 0 <= self.peakScanIndex < 4 else 0
            ax = axes[idx]
            PlotData(
                x,
                [y],
                labels=[pol],
                xlabel="Time",
                ylabel="Power",
                title=f"Scan {scanNum} - {pol} Pol"
            ).plot(ax=ax)
            title = f"Scan {scanNum} - {pol} Pol"

        except Exception as e:
            print(f"Error plotting current scan in quadrant: {e}")

        self.canvas.draw()

        # Save the current scan's data to history for future use
        plot_entry = {
            "scanNum": scanNum,
            "x": x,
            "y": y,
            "pol": pol,
            "key": key,
            "desc": desc,
        }
        self.plot_history.append((self.peakScanIndex, plot_entry))

