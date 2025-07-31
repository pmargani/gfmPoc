"Dialog for choosing polarization in the Pointing tab."

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox

class PointingOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pointing Options")
        from PySide6.QtWidgets import QRadioButton, QDialogButtonBox, QHBoxLayout
        layout = QVBoxLayout(self)
        label = QLabel("Choose polarization for Pointing tab:")
        layout.addWidget(label)
        self.radio_x = QRadioButton("X")
        self.radio_y = QRadioButton("Y")
        self.radio_x.setChecked(True)
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_x)
        radio_layout.addWidget(self.radio_y)
        layout.addLayout(radio_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    @staticmethod
    def get_polarization(parent=None):
        dialog = PointingOptionsDialog(parent)
        result = dialog.exec()
        if result == QDialog.Accepted:
            pol = 'X' if dialog.radio_x.isChecked() else 'Y'
            QMessageBox.information(parent or dialog, "Pointing Tab", f"You chose {pol} polarization.")
            return pol
        return None
