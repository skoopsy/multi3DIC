class DICDataset:
    """ Class to hold data from a stereo DIC dataset """

    def __init__(self):
        self.x = None
        self.x_filtered = None
        self.y = None
        self.y_filtered = None
        self.z = None
        self.z_filtered = None
        self.strain = None
        self.strain_filtered = None
        self.trisurface = None  # Depreciate
        self.simplices = None
        self.simplices_filtered = None


class Config:
    """ Class to hold configuration data for debugging """
    def __init__(self):
        self.debug = True
        self.print_sep = "=" * 30
        