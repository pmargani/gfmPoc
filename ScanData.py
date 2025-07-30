import pickle

class ScanData:
    """class to abstract out the pickle file data"""
    def __init__(self, pkl_file, project_name):
        with open(pkl_file, 'rb') as f:
            self.data = pickle.load(f, encoding='latin1')
        self.project = project_name
        self.numScans = len(self.data[project_name])
        print(f"ScanData: loaded {self.numScans} scans for project {self.project}")
        print(type(self.data[self.project]))

        self.scanNumToIndex = {}
        # create a mapping from scan number to index for quick access
        for i, scanInfo in enumerate(self.data[self.project]):
            self.scanNumToIndex[scanInfo['scan']] = i

    def getScanDataByIndex(self, index):
        """returns the scan data for the given index"""
        scan = self.data[self.project][index]
        return scan

    def getScanOptions(self, scanIndex):
        """returns the scan options for the given scan index"""
        ydata = self.data[self.project][scanIndex]['ydata']
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

    def getScanXDataByIndex(self, scanIndex):
        """returns the x data for the given scan index"""
        return self.data[self.project][scanIndex]['x']

    def getScanYDataByIndex(self, scanIndex, key):
        """returns the y data for the given scan index and key"""
        ydata = self.data[self.project][scanIndex]['ydata']
        return ydata[key]

    def getScanFullDesc(self, scan_index):
        """returns a full description of the scan"""
        scan = self.data[self.project][scan_index]
        desc = f"{scan['scan']}:{scan['source']} {scan['description']}"
        return desc

    def getScanShortDesc(self, scan_index):
        """returns a short description of the scan"""
        scan = self.data[self.project][scan_index]
        desc = f"{scan['scan']}:{scan['source']}"
        return desc

    def __repr__(self):
        return f"ScanData(project={self.project}, scan={getattr(self, 'scan', None)})"
