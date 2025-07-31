"A module for the GfmTab base class for GFM tabs."

from PySide6.QtWidgets import QWidget

class GfmTab(QWidget):
    """
    Base class for all GFM tab widgets.
    Provides a common interface and shared logic for all tabs.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Any shared initialization for all tabs can go here

    def display_scan_data(self, currentSelection):
        """
        Called when a scan is selected. Should be overridden by subclasses.
        """
        raise NotImplementedError("display_scan_data must be implemented by subclasses.")
