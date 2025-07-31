"A module for the FocusTab Class, child of ContCalibTab."

from ContCalibTab import ContCalibTab
from ScanData import ScanData

class FocusTab(ContCalibTab):
    """
    A class for handling all Focus tab content in GFM.
    """
    def __init__(self, parent, scanData: ScanData, name: str = "Focus", scanTypes: list = ["Focus"]):
        super().__init__(parent, scanData, name, scanTypes)
        # You can add more Focus-specific initialization here if needed
