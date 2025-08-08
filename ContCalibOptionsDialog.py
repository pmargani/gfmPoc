"Dialog for choosing polarization in the Pointing tab."

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QButtonGroup

class ContCalibOptionsDialog(QDialog):
    def __init__(self, name, parent, polarization, options : dict):

        super().__init__(parent)
        print(f"Creating {name} Options Dialog with polarization: {polarization}")

        self.name = name
        self.polarization = polarization
        self.setWindowTitle(f"{name} Options")

        polarizations_model = options.get('polarizations', [])
        fitting_model = options.get('fitting', [])
        heuristics_model = options.get('heuristics', [])
        processing_model = options.get('processing', [])

        from PySide6.QtWidgets import QRadioButton, QDialogButtonBox, QHBoxLayout, QTabWidget, QWidget, QVBoxLayout
        main_layout = QVBoxLayout(self)
        tab_widget = QTabWidget()
        # Polarizations tab
        polarizations_tab = QWidget()
        pol_layout = QVBoxLayout(polarizations_tab)
        label = QLabel(f"Choose polarization for {name} tab:")
        pol_layout.addWidget(label)
        # Use passed-in model for polarizations: (label, value)
        self.polarization_buttons = []
        self.polarization_group = QButtonGroup(self)
        self.polarization_button_map = {}  # btn: value
        radio_layout = QVBoxLayout()
        for label, value in polarizations_model:
            btn = QRadioButton(label)
            self.polarization_group.addButton(btn)
            radio_layout.addWidget(btn)
            self.polarization_buttons.append(btn)
            self.polarization_button_map[btn] = value
        # Set checked based on initial polarization
        for btn, value in self.polarization_button_map.items():
            if self.polarization == value:
                btn.setChecked(True)
        pol_layout.addLayout(radio_layout)
        tab_widget.addTab(polarizations_tab, "Polarizations")

        # Fitting Acceptance Criteria tab
        fitting_tab = QWidget()
        fitting_layout = QVBoxLayout(fitting_tab)
        fitting_label = QLabel("Set fitting acceptance criteria here.")
        fitting_layout.addWidget(fitting_label)
        # Use passed-in model for fitting acceptance criteria: (label, value)
        self.fitting_buttons = []
        self.fitting_group = QButtonGroup(self)
        self.fitting_button_map = {}  # btn: value
        fitting_radio_layout = QVBoxLayout()
        for label, value in fitting_model:
            btn = QRadioButton(label)
            self.fitting_group.addButton(btn)
            fitting_radio_layout.addWidget(btn)
            self.fitting_buttons.append(btn)
            self.fitting_button_map[btn] = value
        self.fitting_buttons[0].setChecked(True)
        fitting_layout.addLayout(fitting_radio_layout)
        tab_widget.addTab(fitting_tab, "Fitting Acceptance Criteria")

        # Heuristics tab
        heuristics_tab = QWidget()
        heuristics_layout = QVBoxLayout(heuristics_tab)
        heuristics_label = QLabel("Configure heuristics here.")
        heuristics_layout.addWidget(heuristics_label)
        # Use passed-in model for heuristics: (label, value)
        self.heuristics_buttons = []
        self.heuristics_group = QButtonGroup(self)
        self.heuristics_button_map = {}  # btn: value
        heuristics_radio_layout = QVBoxLayout()
        for label, value in heuristics_model:
            btn = QRadioButton(label)
            self.heuristics_group.addButton(btn)
            heuristics_radio_layout.addWidget(btn)
            self.heuristics_buttons.append(btn)
            self.heuristics_button_map[btn] = value
        self.heuristics_buttons[0].setChecked(True)
        heuristics_layout.addLayout(heuristics_radio_layout)
        tab_widget.addTab(heuristics_tab, "Heuristics")

        # Processing tab
        processing_tab = QWidget()
        processing_layout = QVBoxLayout(processing_tab)
        processing_label = QLabel("Set processing options here.")
        processing_layout.addWidget(processing_label)
        # Use passed-in model for processing options: (label, value)
        self.processing_buttons = []
        self.processing_group = QButtonGroup(self)
        self.processing_button_map = {}  # btn: value
        processing_radio_layout = QVBoxLayout()
        for label, value in processing_model:
            btn = QRadioButton(label)
            self.processing_group.addButton(btn)
            processing_radio_layout.addWidget(btn)
            self.processing_buttons.append(btn)
            self.processing_button_map[btn] = value
        self.processing_buttons[0].setChecked(True)
        processing_layout.addLayout(processing_radio_layout)
        tab_widget.addTab(processing_tab, "Processing")
        main_layout.addWidget(tab_widget)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)


