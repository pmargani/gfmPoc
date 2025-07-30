

import sys
import pickle

from PySide6.QtWidgets import QApplication, QWidget, QListView, QTextEdit, QHBoxLayout, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT

class PlotData:
    def __init__(self, x, y_list, labels=None, xlabel="", ylabel="", title=""):
        self.x = x
        self.y_list = y_list  # List of y data arrays
        self.labels = labels if labels is not None else [f"Series {i+1}" for i in range(len(y_list))]
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title

    def plot(self):
        fig = Figure(figsize=(4, 3))
        ax = fig.add_subplot(111)
        for y, label in zip(self.y_list, self.labels):
            ax.plot(self.x, y, label=label)
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.legend()
        return fig, ax

class ScanData:
    "class to abstract out the pickle file data"
    def __init__(self, pkl_file):
        with open(pkl_file, 'rb') as f:
            self.data = pickle.load(f, encoding='latin1')
        self.project = self.data['project']
        self.numScans = 4

    def getScanOptions(self):
        ydata = self.data['ydata']
        keys = list(ydata.keys())
        options = {}
        labels = ["beams", "pols", "phases", "freqs"]
        # extract the unique values for each label
        for i, label in enumerate(labels):
            options[label] = set([key[i] for key in keys])
        # convert sets to sorted lists
        for k, v in options.items():
            options[k] = sorted(list(v))

        return options

    def __repr__(self):
        return f"ScanData(project={self.project}, scan={self.scan})"


# Custom list model for scans
class ScanListModel(QAbstractListModel):
    def __init__(self, scans=None):
        super().__init__()
        self.scans = scans or []

    def rowCount(self, parent=QModelIndex()):
        return len(self.scans)

    def data(self, index, role):
        if role == Qt.DisplayRole and index.isValid():
            return f"Scan {self.scans[index.row()]}"
        return None

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GFM - List and Text Edit")
        self.resize(600, 400)

        # get the data we're going to plot
        fn = "dcr.pkl"
        # with open(fn, 'rb') as f:
        #     self.data = pickle.load(f, encoding='latin1')
        self.scanData = ScanData(fn)
        # Create widgets
        self.scans_widget = QListView()
        self.text_edit = QTextEdit()
        self.canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # Add some example items
        self.scans = list(range(1, 5))  # Example list of scans
        self.model = ScanListModel(self.scans)
        self.scans_widget.setModel(self.model)

        # Connect selection change to handler
        self.scans_widget.selectionModel().currentChanged.connect(self.display_scan_data)


        # Create options panel with checkboxes
        self.options_panel = QWidget()
        self.options_layout = QVBoxLayout(self.options_panel)
        self.options_checkboxes = {}  # Dict[label] = list of QCheckBox

        self.options_panel.setLayout(self.options_layout)

        # Create right panel layout (vertical: text_edit on top, plot below, options to the right)
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

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.scans_widget)
        splitter.addWidget(right_panel)
        splitter.setSizes([200, 600])

        # Layout
        layout = QHBoxLayout(self)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def display_scan_data(self, current, previous):
        scan = self.model.data(current, Qt.DisplayRole)
        value = f"proj: {self.scanData.data['project']}, scan: {scan}"
        self.text_edit.setPlainText(value)

        # Remove current checkboxes from options_layout
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.options_checkboxes.clear()

        opts = self.scanData.getScanOptions()
        from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QCheckBox, QLabel
        import itertools
        for label, values in opts.items():
            group_box = QGroupBox(label)
            h_layout = QHBoxLayout()
            checkboxes = []
            for i, val in enumerate(values):
                cb = QCheckBox(str(val))
                if i == 0:
                    cb.setChecked(True)
                h_layout.addWidget(cb)
                checkboxes.append(cb)
                # Connect checkbox to handler
                cb.stateChanged.connect(self.on_option_checkbox_changed)
            group_box.setLayout(h_layout)
            self.options_layout.addWidget(group_box)
            self.options_checkboxes[label] = checkboxes
            self.on_option_checkbox_changed()  # Initial call to set up the plot

    def on_option_checkbox_changed(self):
        # Only plot if every row has at least one checked box
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
        # If any row has no checked box, do not plot
        if any(len(selected_values[label]) == 0 for label in labels):
            return
        import itertools
        value_lists = [selected_values[label] for label in labels]
        key_combinations = list(itertools.product(*value_lists))
        key = key_combinations[0] if key_combinations else None
        # Use the last selected scan
        scan = self.model.data(self.scans_widget.currentIndex(), Qt.DisplayRole)
        self.plot_data(self.scanData.project, scan, key_combinations)

        # Build the key tuple from selected checkboxes
        labels = ["beams", "pols", "phases", "freqs"]
        selected_values = {}
        for label in labels:
            selected_values[label] = []
            checkboxes = self.options_checkboxes[label]
            for cb in checkboxes:
                if cb.isChecked():
                    # Try to convert to int or float if possible
                    val = cb.text()
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                    selected_values[label].append(val)
                    # break  # Only take the first checked per label
        # Build all combinations of selected checkbox values as tuples
        value_lists = [selected_values[label] for label in labels]
        key_combinations = list(itertools.product(*value_lists))
        print(f"key_combinations: {key_combinations}")
        # For demonstration, just use the first combination (or handle all as needed)
        # key = key_combinations[0] if key_combinations else None
        # key = tuple(selected_values)

        self.plot_data(self.scanData.project, scan, key_combinations)


    def plot_data(self, project, scan, optionsKeys):
        """plots the data contained in the member vars"""

        opts = self.scanData.getScanOptions()
        print(opts)
        plotter = PlotData(
            x=self.scanData.data['x'],
            y_list=[self.scanData.data['ydata'][key] for key in optionsKeys],
            labels=optionsKeys,
            xlabel="X-axis",
            ylabel="Y-axis",
            title=f"Scan {scan}"
        )
        fig, ax = plotter.plot()
        # Remove the old canvas and toolbar and add the new ones
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
