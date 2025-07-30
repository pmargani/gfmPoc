import pickle

class ScanData:
    """class to abstract out the pickle file data"""
    def __init__(self, pkl_file):
        with open(pkl_file, 'rb') as f:
            self.data = pickle.load(f, encoding='latin1')
        self.project = self.data['project']
        self.numScans = 4

    def getScanOptions(self):
        ydata = self.data['ydata']
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

    def __repr__(self):
        return f"ScanData(project={self.project}, scan={getattr(self, 'scan', None)})"
