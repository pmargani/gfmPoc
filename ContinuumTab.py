"A module for the ContinuumTab Class"

from ScanData import ScanData
from OptionsTab import OptionsTab

class ContinuumTab(OptionsTab):

    """
    A class for handling all DCR data in GFM.
    """

    def __init__(
        self,
        parent,
        scanData : ScanData,
        name : str,
        scanTypes : list,
    ):
        super().__init__(parent, scanData, name, scanTypes)

        # these are the options available for continuum data
        self.labels = ["beams", "pols", "phases", "freqs"]

