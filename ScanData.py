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

    def getScanIndexByScanNum(self, scanNum):
        """returns the index of the scan with the given scan number"""
        return self.scanNumToIndex.get(scanNum, -1)

    def getScanNumByIndex(self, index):
        """returns the scan number for the given index"""
        if 0 <= index < self.numScans:
            return self.data[self.project][index]['scan']
        return None

    def getScanDataByIndex(self, index):
        """returns the scan data for the given index"""
        scan = self.data[self.project][index]
        return scan

    def getScanOptions(self, scanIndex, labels):
        """returns the scan options for the given scan index"""
        # ydata = self.data[self.project][scanIndex]['ydata']
        d = self.data[self.project][scanIndex]
        # TBF: bugs in pkl file
        key = "ydata" if "ydata" in d else "ys"
        ydata = d[key]
        keys = list(ydata.keys())
        options = {}
        # labels = ["beams", "pols", "phases", "freqs"]
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
        d = ydata = self.data[self.project][scanIndex]
        k = "ydata" if "ydata" in d else "ys"
        ydata = d[k]
        data = ydata[key]
        # TBF: bugs in pkl file
        if len(data) == 2:
            data = data[0]
        return data


    def getScanFullDesc(self, scan_index):
        """returns a full description of the scan"""
        scan = self.data[self.project][scan_index]
        src = scan['source'] if 'source' in scan else 'unknown'
        desc = f"{scan['scan']}:{src} {scan['description']}"
        return desc

    def getScanShortDesc(self, scan_index):
        """returns a short description of the scan"""
        scan = self.data[self.project][scan_index]
        src = scan['source'] if 'source' in scan else 'unknown'
        desc = f"{scan['scan']}:{src} {scan['description']}"
        return desc

    def getScanShortDesc(self, scan_index):
        """returns a short description of the scan"""
        scan = self.data[self.project][scan_index]
        src = scan['source'] if 'source' in scan else 'unknown'
        desc = f"{scan['scan']}:{src}"
        return desc

    def __repr__(self):
        return f"ScanData(project={self.project}, scan={getattr(self, 'scan', None)})"
