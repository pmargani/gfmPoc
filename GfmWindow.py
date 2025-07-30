import sys
from PySide6.QtWidgets import QWidget, QListView, QTextEdit, QHBoxLayout, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from ScanData import ScanData
from PlotData import PlotData
from ScanListModel import ScanListModel

class GfmWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GFM - List and Text Edit")
        self.resize(600, 400)

        fn = "dcr.pkl"
        self.scanData = ScanData(fn)
        self.scans_widget = QListView()
        self.text_edit = QTextEdit()
        self.canvas = FigureCanvas()
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.scans = list(range(1, 5))
        self.model = ScanListModel(self.scans)
        self.scans_widget.setModel(self.model)
        self.scans_widget.selectionModel().currentChanged.connect(self.display_scan_data)
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
        scan = self.model.data(current, Qt.DisplayRole)
        value = f"proj: {self.scanData.data['project']}, scan: {scan}"
        self.text_edit.setPlainText(value)
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.options_checkboxes.clear()
        opts = self.scanData.getScanOptions()
        from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QCheckBox
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
                cb.stateChanged.connect(self.on_option_checkbox_changed)
            group_box.setLayout(h_layout)
            self.options_layout.addWidget(group_box)
            self.options_checkboxes[label] = checkboxes
            self.on_option_checkbox_changed()

    def on_option_checkbox_changed(self):
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
        import itertools
        value_lists = [selected_values[label] for label in labels]
        key_combinations = list(itertools.product(*value_lists))
        scan = self.model.data(self.scans_widget.currentIndex(), Qt.DisplayRole)
        self.plot_data(self.scanData.project, scan, key_combinations)
        labels = ["beams", "pols", "phases", "freqs"]
        selected_values = {}
        for label in labels:
            selected_values[label] = []
            checkboxes = self.options_checkboxes[label]
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
        value_lists = [selected_values[label] for label in labels]
        key_combinations = list(itertools.product(*value_lists))
        print(f"key_combinations: {key_combinations}")
        self.plot_data(self.scanData.project, scan, key_combinations)

    def plot_data(self, project, scan, optionsKeys):
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
