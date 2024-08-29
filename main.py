import sys

from modules.classes import DICDataset, Config
from modules import methods, loading

if __name__ == '__main__':

    sys.path.append("..")
    CONF = Config()

    # Stereo pair directories
    stereo_pair_dirs = ["test_files/cam1-2/",
                        "test_files/cam2-3/",
                        "test_files/cam3-4/"]

    datasets = loading.load_multiple_stereo_pairs(stereo_pair_dirs=stereo_pair_dirs,
                                                  config=CONF)

    
    methods.mesh_filter_plot_combined(datasets=datasets)
