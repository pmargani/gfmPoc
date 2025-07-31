"A module for the PointingTab Class, child of ContCalibTab."

from ContCalibTab import ContCalibTab
from ScanData import ScanData

class PointingTab(ContCalibTab):
    """
    A class for handling all Pointing tab content in GFM.
    """
    def __init__(self, parent, scanData: ScanData, name: str, scanTypes: list):
        super().__init__(parent, scanData, name, scanTypes)
        # You can add more Pointing-specific initialization here if needed
