"A module for the GfmTab base class for GFM tabs."

from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT

from PlotData import PlotData
from ScanData import ScanData

class GfmTab(QWidget):
    """
    Base class for all GFM tab widgets.
    Provides a common interface and shared logic for all tabs.
    """
    def __init__(self, parent, scanData : ScanData, name : str, scanTypes : list):
        super().__init__(parent)

        self.scanData = scanData
        self.name = name
        self.scanTypes = scanTypes

        # Shared matplotlib canvas and toolbar for all tabs
        self.canvas = FigureCanvas()
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.currentScanIndex = None  # To track the currently selected scan index

    def display_scan_data(self, currentSelection):
        """
        Called when a scan is selected. Should be overridden by subclasses.
        """
        raise NotImplementedError("display_scan_data must be implemented by subclasses.")

    def update_plot(self, x, ys, ylabels, xaxis_label, yaxis_label, title):
        plotter = PlotData(
            x=x,
            y_list=ys,
            labels=ylabels,
            xlabel=xaxis_label,
            ylabel=yaxis_label,
            title=title
        )
        fig, _ = plotter.plot()
        # Update canvas
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