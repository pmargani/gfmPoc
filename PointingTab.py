"A module for the PointingTab Class"

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class PointingTab(QWidget):
    """
    A class for handling all Pointing tab content in GFM.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel("Pointing tab content goes here.")
        layout.addWidget(self.label)
        self.setLayout(layout)

    def display_scan_data(self, currentSelection):
        # Example: update label with scan info if needed
        self.label.setText(f"Pointing tab: scan index {currentSelection.row()}")
