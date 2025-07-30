from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QGroupBox, QCheckBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT


class ContinuumTab(QWidget):

    def on_option_checkbox_changed(self):
        # find the selected values from the checkboxes
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
        value_lists = [selected_values[label] for label in labels]
        import itertools
        key_combinations = list(itertools.product(*value_lists))
        # Use the last scan index that was displayed
        scanIndex = getattr(self, '_last_scan_index', 0)
        scan = self.model.getScanDataByIndex(scanIndex)
        print(f"key_combinations: {key_combinations}")
        self.plot_data(self.scanData.project, scanIndex, key_combinations)

    def plot_data(self, project, scanIndex : int, optionsKeys):
        self._last_scan_index = scanIndex
        from PlotData import PlotData
        plotter = PlotData(
            x=self.scanData.getScanXDataByIndex(scanIndex),
            y_list=[self.scanData.getScanYDataByIndex(scanIndex, key) for key in optionsKeys],
            labels=optionsKeys,
            xlabel="Time",
            ylabel="Power",
            title=self.scanData.getScanShortDesc(scanIndex)
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

    def display_scan_data(self, current, previous):
        # get the scan data by index
        scan = self.model.getScanDataByIndex(current.row())
        # use the scan data to update the text edit and options panel
        print(f"Displaying scan data for: {scan}, type: {type(scan)}")
        value = f"proj: {self.scanData.project}, scan: {scan['scan']}"
        self.text_edit.setPlainText(value)
        # Clear previous options
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.options_checkboxes.clear()
        # Get scan options and create checkboxes
        opts = self.scanData.getScanOptions(current.row())
        for label, values in opts.items():
            group_box = QGroupBox(label)
            v_layout = QVBoxLayout()
            checkboxes = []
            for i, val in enumerate(values):
                cb = QCheckBox(str(val))
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
    def __init__(self, parent, scanData, model, text_edit=None, canvas=None, toolbar=None, options_panel=None, options_layout=None, options_checkboxes=None):
        super().__init__(parent)
        self.scanData = scanData
        self.model = model
        self.text_edit = text_edit or QTextEdit()
        self.canvas = canvas or FigureCanvas()
        self.toolbar = toolbar or NavigationToolbar2QT(self.canvas, self)
        self.options_panel = options_panel or QWidget()
        self.options_layout = options_layout or QVBoxLayout(self.options_panel)
        self.options_checkboxes = options_checkboxes or {}
        self.options_panel.setLayout(self.options_layout)
        plot_panel = QWidget()
        plot_layout = QVBoxLayout(plot_panel)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)
        plot_panel.setLayout(plot_layout)
        layout = QHBoxLayout(self)
        vbox = QVBoxLayout()
        vbox.addWidget(self.text_edit)
        vbox.addWidget(plot_panel)
        layout.addLayout(vbox)
        layout.addWidget(self.options_panel)
        self.setLayout(layout)
